# coding: utf-8
import bluetooth
import struct
import logging
from threading import Thread
import threading
import time
import select
import request
import response


class SpheroError(Exception):
    pass


class MotorMode(object):
    MOTOR_OFF = 0
    MOTOR_FWD = 1
    MOTOR_REV = 2
    MOTOR_BRK = 3
    MOTOR_IGNORE = 4


class SpheroAPI(object):
    GET_RESPONSE_RETRIES = 100

    def __init__(self, bt_name=None, bt_addr=None):
        self._dev = 0x00

        self._seq = 0x00
        self._seq_lock = threading.RLock()

        self.bt_name = bt_name
        self.bt_addr = bt_addr

        self._bt_socket = None
        self._connecting = False

        # FOR THE ASYNC RECEIVER
        self._receiver_thread = None
        self._run_receive = True
        self._packages = []
        self._responses = []

    @property
    def seq(self):
        """
        A thread-safe method for creating sequence numbers.
        @return: a new seq number
        """
        with self._seq_lock:
            self._seq += 1
            if self._seq >= 0xFF:
                self._seq = 0x00
            return self._seq

    def __repr__(self):
        self_str = "\n Name: %s\n Addr: %s\n Connected: %s\n" % (
            self.bt_name, self.bt_addr, "Yes" if self.connected() else "No")
        return self_str

    def connect(self, retries=100, async=False):
        """
        Connect the sphero device
        @param retries: Number of connection retries
        @param async: Should the connection be executed async. The method will return immediately
        @return: None
        """
        if self.bt_addr is None:
            raise SpheroError("No device address is set for the connection")

        if self._connecting:
            raise SpheroError("Device is already trying to connect")

        if self.connected():
            raise SpheroError("Device is already connected")

        self._connecting = True
        if async:
            thread = Thread(target=self._connect, args=(retries,))
            thread.start()
        else:
            self._connect(retries)

    def _connect(self, retries):
        """
        A Helper method for connecting the sphero. This is where the actual connection is executed
        """
        for _ in xrange(retries):
            try:
                self._bt_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self._bt_socket.connect((self.bt_addr, 1))

                # If connection was established, starts to listen for incoming packages
                self._start_receiver()
                break
            except bluetooth.btcommon.BluetoothError:
                time.sleep(1)
        else:
            self._connecting = False
            raise SpheroError('failed to connect after %d tries' % retries)
        self._connecting = False

    def _start_receiver(self):
        """
        Starts the asynchronous package receiver
        """
        if not self._receiver_thread:
            self._run_receive = True
            self._receiver_thread = Thread(target=self._receiver)
            self._receiver_thread.start()

    def _stop_receiver(self):
        """
        Stops the asynchronous package receiver
        """
        self._receiver_thread = None
        self._run_receive = False

    def disconnect(self):
        """
        Closes the sphero connecetcion
        @return: True if the connection was closed
        """
        if self._bt_socket is not None:
            self._stop_receiver()
            self._bt_socket.close()
            self._bt_socket = None
            return True
        return False

    def connected(self):
        """
        Returns a bool if the sphero is connected
        @return: True if the sphero is connected
        """
        if self._bt_socket is not None and not self._connecting:
            return True
        return False

    def _get_request(self, seq):
        """
        Helper method
        Returns the request package with the given sequence number
        Raises a indexError if the seq number does not exist
        @param seq: The request sequence number
        @raise: IndexError
        @return: The request object
        """
        return filter(lambda a: a.seq == seq, self._packages)[0]

    def _get_response(self, seq):
        """
        Helper method
        Returns the response package with the given sequence number
        Raises a indexError if the seq number does not exist
        @param seq: The response sequence number
        @raise: IndexError
        @return: The request object
        """
        return filter(lambda a: a.seq == seq, self._responses)[0]

    def _send_package(self, packet):
        """
        Sends the given package to the connected sphero
        @param packet: The request package to send to the connected device
        """
        self._packages.append(packet)
        self._bt_socket.send(str(packet))

    def _write(self, packet):
        """
        Sends a message to the connected device
        @param packet: The request to send. A subclass of the Request class
        @type packet: request.Request
        @return: A response class or @raise SpheroError: if no response received
        @rtype: response.Response
        """
        if not self.connected():
            raise SpheroError('Device is not connected')

        self._send_package(packet)

        # Gets response from async receiver
        for _ in xrange(self.GET_RESPONSE_RETRIES):
            try:
                res = self._get_response(packet.seq)
                if res.success:
                    self._packages.remove(packet)
                    self._responses.remove(res)
                    return res
                else:
                    raise SpheroError('request failed: '+res.msg)
            except IndexError:
                time.sleep(0.1)
        else:
            raise SpheroError('No response received found')

    @staticmethod
    def _is_sync_package(header):
        """ Helper method to check if this is a synchronous msg response"""
        return header[response.Response.SOP1] == 0xFF and header[response.Response.SOP2] == 0xFF

    @staticmethod
    def _is_async_package(header):
        """ Helper method to check if this is a a-synchronous msg"""
        return header[response.Response.SOP1] == 0xFF and header[response.Response.SOP2] == 0xFE

    def _something_to_receive(self):
        """ Helper method Checks if there is something to receive from the bt_socket"""
        ready_to_receive = select.select([self._bt_socket], [], [], 0.1)[0]
        return self._bt_socket in ready_to_receive

    def _receive_header(self, fmt='5B'):
        """
        Helper method, receives the header of the package from the bt socket and converts it into a tuple
        @param fmt: The format of the header
        @return: tuple
        """
        raw_response = self._bt_socket.recv(5)
        header = struct.unpack(fmt, raw_response)
        return header

    def _create_response_object(self, body, header):
        """
        Creates a response instance from the received package
        @param header: The header of the package received
        @param body: The body of the package received
        @return: response.Response
        """
        seq = header[response.Response.SEQ]
        packet = self._get_request(seq)
        new_response = packet.response(header, body)
        return new_response

    def _convert_to_async_header(self, header):
        dlen_msb = header[-2] << 8
        dlen = dlen_msb + header[-1]
        header = header[:-2] + (dlen,)
        return header

    def _receiver(self):
        """
        Asynchronous receiver of incoming data.
        Converts incoming data to the appropriate response instances and add these to
        the correct incoming message queues.

        This method is started when the device is successfully connected, and stoped when the device is
        disconnected.
        @raise SpheroError:
        """
        while self._run_receive:
            if self._something_to_receive():
                header = self._receive_header()
                if self._is_sync_package(header):
                    body = self._bt_socket.recv(header[-1])
                    new_response = self._create_response_object(body, header)
                    self._responses.append(new_response)

                elif self._is_async_package(header):
                    header = self._convert_to_async_header(header)
                    body = self._bt_socket.recv(header[-1])

                    if header[response.AsyncResponse.ID_CODE] == response.AsyncIdCode.COLLISION_DETECTED:
                        print "COLLISION DETECTED"
                        msg = response.CollisionDetected(header, body)
                        print msg
                    else:
                        # TODO implement
                        print "Received async msg: ", header
                else:
                    raise SpheroError("Unknown data received from sphero. Header: {}".format(header))

    # CORE COMMANDS
    def prep_str(self, s):
        """ Helper method to take a string and give a array of "bytes" """
        return [ord(c) for c in s]

    def ping(self):
        return self._write(request.Ping(self.seq))

    def set_rgb(self, r, g, b, persistent=False):
        return self._write(request.SetRGB(self.seq, r, g, b, 0x01 if persistent else 0x00))

    def get_rgb(self):
        return self._write(request.GetRGB(self.seq))

    def get_version(self):
        raise NotImplementedError

    def get_device_name(self):
        # GET_DEVICE_NAME is not really part of the api,
        # it has changed to GET_BLUETOOTH_INFO.
        # Which returns both name and Bluetooth mac address.
        return self.get_bluetooth_info().name

    def set_device_name(self, new_name):
        """ Sets internal device name. (not announced bluetooth name).
        requires utf-8 encoded string. """
        return self._write(request.SetDeviceName(self.seq, *self.prep_str(new_name)))

    def get_bluetooth_info(self):
        return self._write(request.GetBluetoothInfo(self.seq))

    def set_auto_reconnect(self):
        raise NotImplementedError

    def get_auto_reconnect(self):
        raise NotImplementedError

    def get_power_state(self):
        return self._write(request.GetPowerState(self.seq))

    def set_power_notification(self):
        raise NotImplementedError

    def sleep(self, wakeup=0, macro=0, orbbasic=0):
        return self._write(request.Sleep(self.seq, wakeup, macro, orbbasic))

    def get_voltage_trip_points(self):
        raise NotImplementedError

    def set_voltage_trip_points(self):
        raise NotImplementedError

    def set_inactivity_timeout(self):
        raise NotImplementedError

    def jump_to_bootloader(self):
        raise NotImplementedError

    def perform_level_1_diagnostics(self):
        raise NotImplementedError

    def perform_level_2_diagnostics(self):
        raise NotImplementedError

    def clear_counters(self):
        raise NotImplementedError

    def set_time_value(self):
        raise NotImplementedError

    # SPHERO COMMANDS

    def poll_packet_times(self):
        raise NotImplementedError

    def set_heading(self, value):
        """value can be between 0 and 359"""
        return self._write(request.SetHeading(self.seq, value))

    def set_stabilization(self, state):
        """
        Turns off or on the internal stabilization of the sphero
        @param state: Sets stabilization on or off
        @type state: bool
        @rtype: response.Response
        @return: SimpleResponse
        """
        return self._write(request.SetStabilization(self.seq, state))

    def set_rotation_rate(self, val):
        """ value ca be between 0x00 and 0xFF:
            value is a multiplied with 0.784 degrees/s except for:
            0   --> 1 degrees/s
            255 --> jumps to 400 degrees/s
            @param val: Sets the new rotation rate
            @type val: int
            @rtype: response.Response
            @return: SimpleResponse
        """
        return self._write(request.SetRotationRate(self.seq, val))

    def set_application_configuration_block(self):
        raise NotImplementedError

    def get_application_configuration_block(self):
        raise NotImplementedError

    def reenable_demo_mode(self):
        raise NotImplementedError

    def get_chassis_id(self):
        raise NotImplementedError

    def set_chassis_id(self):
        raise NotImplementedError

    def self_level(self):
        # TODO IMPLEMENT
        raise NotImplementedError

    def set_data_streaming(self):
        # TODO IMPLEMENT SUPPORT
        raise NotImplementedError

    def configure_collision_detection(self, meth=0x01, x_t=0x64, y_t=0x64, x_spd=0x64, y_spd=0x64, dead=0x64):
        # TODO WRITE DOCS
        return self._write(request.ConfigureCollisionDetection(self.seq, meth, x_t, y_t, x_spd, y_spd, dead))

    def set_back_led_output(self, value):
        """value can be between 0x00 and 0xFF"""
        return self._write(request.SetBackLEDOutput(self.seq, value))

    def roll(self, speed, heading, state=1):
        """
        @param speed: speed can have value between 0x00 and 0xFF
        @param heading: heading can have value between 0 and 359

        State:
        As of the 1.13 firmware version.
        State   Speed   Result
        1       > 0     Normal driving
        1       0       Rotate in place
        2       x       Force fast rotation
        0       x       Commence optimal braking to zero speed
        @return: SimpleResponse
        @rtype: response.Response
        """
        return self._write(request.Roll(self.seq, speed, heading, state))

    def set_boost_with_time(self):
        raise NotImplementedError

    def set_raw_motor_values(self, left_mode=MotorMode.MOTOR_IGNORE, left_power=0x00,
                             right_mode=MotorMode.MOTOR_IGNORE, right_power=0x00):
        """
        Sets a raw value to one or both of Spheros engines.

        NOTE: This command will disable stabilization if booth modes aren't MotorMode.MOTOR_IGNORE. This would have the
        be re-enabled with the set_stabilization command

        @param left_mode: Sets the mode of the engine (see the MotorMode class)
        @type left_mode: MotorMode
        @param left_power: Sets the motor power for the left engine. Value in range 0x00 - 0xFF
        @param right_mode: Sets the mode of the engine (see the MotorMode class)
        @type right_mode: MotorMode
        @param right_power: Sets the motor power for the right engine. Value in range 0x00 - 0xFF
        @rtype: response.Response
        @return: SimpleResponse
        """
        return self._write(request.SetRawMotorValues(self.seq, left_mode, left_power, right_mode, right_power))

    def set_motion_timeout(self):
        # TODO IMPLEMENT
        raise NotImplementedError

    def set_option_flags(self, stay_on=False, vector_drive=False, leveling=False, tail_LED=False, motion_timeout=False,
                         demo_mode=False, tap_light=False, tap_heavy=False, gyro_max=False):
        """
        Assigns the permanent option flags to the provided value and writes them to the config block for
        persistence across power cycles. See below for the bit definitions.

        @param stay_on: Set to prevent Sphero from immediately going to sleep when placed in the charger and connected
        over Bluetooth
        @param vector_drive: Set to enable Vector Drive, that is, when Sphero is stopped and a new roll command is
        issued it achieves the heading before moving along it
        @param leveling: Set to disable self-leveling when Sphero is inserted into the charger
        @param tail_LED: Set to force the tail LED always on
        @param motion_timeout: Set to enable motion timeouts (see DID 02h, CID 34h)
        @param demo_mode: Set to enable retail Demo Mode (when placed in the charger ball runs a slow rainbow macro for
        60 minutes and then goes to sleep).
        @param tap_light: Set double tap sensitivity to light
        @param tap_heavy: Set double tap sensitivity to heavy
        @param gyro_max: Enable gyro max async message
        @rtype: response.Response
        @return: SimpleResponse
        """
        flags = 0x0000
        flags |= 0x0001 if stay_on else 0x0000
        flags |= 0x0002 if vector_drive else 0x0000
        flags |= 0x0004 if leveling else 0x0000
        flags |= 0x0008 if tail_LED else 0x0000
        flags |= 0x0010 if motion_timeout else 0x0000
        flags |= 0x0020 if demo_mode else 0x0000
        flags |= 0x0040 if tap_light else 0x0000
        flags |= 0x0080 if tap_heavy else 0x0000
        flags |= 0x0100 if gyro_max else 0x0000

        return self._write(request.SetOptionFlags(self.seq, flags))

    def get_option_flags(self):
        return self._write(request.GetOptionFlags(self.seq))

    def get_configuration_block(self):
        raise NotImplementedError

    def set_device_mode(self):
        raise NotImplementedError

    def run_macro(self):
        raise NotImplementedError

    def save_temporary_macro(self):
        raise NotImplementedError

    def reinit_macro(self):
        raise NotImplementedError

    def abort_macro(self):
        raise NotImplementedError

    def get_macro_status(self):
        raise NotImplementedError

    def set_macro_parameter(self):
        raise NotImplementedError

    def append_macro_chunk(self):
        raise NotImplementedError

    def erase_orbbasic_storage(self):
        raise NotImplementedError

    def append_orbbasic_fragment(self):
        raise NotImplementedError

    def run_orbbasic_program(self):
        raise NotImplementedError

    # BOOTLOADER COMMANDS (still looking for actual docs on these)

    def abort_orbbasic_program(self):
        raise NotImplementedError

    def begin_bootloader_reflash(self):
        raise NotImplementedError

    def set_bootloader_page(self):
        raise NotImplementedError

    def leave_bootloader(self):
        raise NotImplementedError

    def is_bootloader_page_blank(self):
        raise NotImplementedError

    def erase_user_config(self):
        raise NotImplementedError

    def configure_locator(self, x_pos, y_pos, yaw_tare=0x00):
        """
        @param x_pos: in the range 0x00 - 0xff sets the new x position
        @param y_pos: in the range 0x00 - 0xff sets the new y position
        @param yaw_tare: in the range 0x00 - 0xff sert yaw tare
        @return: simple response
        """
        flags = 0x01  # Could make the user set this
        return self._write(request.ConfigureLocator(self.seq, flags, x_pos, y_pos, yaw_tare))

    # Additional "higher-level" commands

    def read_locator(self):
        """
        This reads spheros current X, Y position, component velocities
        and SOG(speed over ground). Position is a signed value in cm.
        The component velocities are signed cm/sec while the SOG is
        unsigned cm/sec.
        @return: response.Response
        """
        return self._write(request.ReadLocator(self.seq))

    def stop(self):
        return self.roll(0, 0)


if __name__ == '__main__':
    s = SpheroAPI(bt_name="Sphero-YGY", bt_addr="68:86:e7:03:24:54")
    s.connect()
    print s.set_option_flags(stay_on=False,
                             vector_drive=False,
                             leveling=False,
                             tail_LED=False,
                             motion_timeout=False,
                             demo_mode=True,
                             tap_light=False,
                             tap_heavy=False,
                             gyro_max=False).success

    print s.get_option_flags()

    print s.get_power_state()
    print s.get_power_state()
    print s.configure_collision_detection()

    time.sleep(100)

    print s.disconnect()

