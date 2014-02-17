# coding: utf-8
import bluetooth
import struct
import logging
from threading import Thread
import time
import request


class SpheroError(Exception):
    pass


class MotorMode(object):
    MOTOR_OFF = 0
    MOTOR_FWD = 1
    MOTOR_REV = 2
    MOTOR_BRK = 3
    MOTOR_IGNORE = 4


class SpheroAPI(object):
    SOCKET_TIME_OUT = 5

    def __init__(self, bt_name=None, bt_addr=None):
        self.dev = 0x00
        self.seq = 0x00

        self.bt_name = bt_name
        self.bt_addr = bt_addr

        self.bt_socket = None
        self._connecting = False

    def __repr__(self):
        self_str = "\n Name: %s\n Addr: %s\n Connected: %s\n" % (
            self.bt_name, self.bt_addr, "Yes" if self.connected() else "No")
        return self_str

    def _connect(self, retries):

        for _ in xrange(retries):
            try:
                self.bt_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.bt_socket.connect((self.bt_addr, 1))
                break
            except bluetooth.btcommon.BluetoothError:
                time.sleep(1)
        else:
            self._connecting = False
            raise SpheroError('failed to connect after %d tries' % retries)
        self.bt_socket.settimeout(SpheroAPI.SOCKET_TIME_OUT)
        self._connecting = False

    def connect(self, retries=100, async=False):
        if self.bt_addr is None:
            raise SpheroError("No device address is set for the connection")

        if self._connecting:
            raise SpheroError("Device is already trying to connect")

        self._connecting = True
        if async:
            print "starts connection thread"
            thread = Thread(target=self._connect, args=(retries,))
            thread.start()
        else:
            self._connect(retries)

    def disconnect(self):
        if self.bt_socket is not None:
            self.bt_socket.close()
            self.bt_socket = None

    def connected(self):
        if self.bt_socket is not None and not self._connecting:
            return self.bt_socket.getsockname()[1]
        else:
            return False

    def can_connect(self):
        return not self._connecting

    def write(self, packet):
        if not self.connected():
            raise SpheroError('Device is not connected')

        self.bt_socket.send(str(packet))
        self.seq += 1
        if self.seq >= 0xFF:
            self.seq = 0x00

        try:
            # TODO verify seq is the same as sent
            # TODO maybe add a lock here? critical section
            raw_response = self.bt_socket.recv(5)
            header = struct.unpack('5B', raw_response)
            body = self.bt_socket.recv(header[-1])

            response = packet.response(header, body)

        except struct.error as e:
            print e.message
            raise SpheroError("NO RESPONSE RECEIVED FROM SPHERO")

        if response.success:
            return response
        else:
            print response.msg
            raise SpheroError('request failed (request: %s:%s, response: %s:%s)' % (header,
                                                                                    repr(body),
                                                                                    response.header,
                                                                                    repr(response.body)))

    def prep_str(self, s):
        """ Helper method to take a string and give a array of "bytes" """
        return [ord(c) for c in s]

    # CORE COMMANDS

    def ping(self):
        return self.write(request.Ping(self.seq))

    def set_rgb(self, r, g, b, persistant=False):
        return self.write(request.SetRGB(self.seq, r, g, b, 0x01 if persistant else 0x00))

    def get_rgb(self):
        return self.write(request.GetRGB(self.seq))

    def get_version(self):
        raise NotImplementedError

    def get_device_name(self):
        # GET_DEVICE_NAME is not really part of the api,
        # it has changed to GET_BLUETOOTH_INFO.
        # Which returns both name and Bluetooth mac address.
        return self.get_bluetooth_info().name

    def set_device_name(self, newname):
        """ Sets internal device name. (not announced bluetooth name).
        requires utf-8 encoded string. """
        return self.write(request.SetDeviceName(self.seq, *self.prep_str(newname)))

    def get_bluetooth_info(self):
        return self.write(request.GetBluetoothInfo(self.seq))

    def set_auto_reconnect(self):
        raise NotImplementedError

    def get_auto_reconnect(self):
        raise NotImplementedError

    def get_power_state(self):
        return self.write(request.GetPowerState())

    def set_power_notification(self):
        raise NotImplementedError

    def sleep(self, wakeup=0, macro=0, orbbasic=0):
        return self.write(request.Sleep(self.seq, wakeup, macro, orbbasic))

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

    def poll_packet_times(self):
        raise NotImplementedError

    # SPHERO COMMANDS

    def set_heading(self, value):
        """value can be between 0 and 359"""
        return self.write(request.SetHeading(self.seq, value))

    def set_stabilization(self, state):
        """
        Turns off or on the internal stabilization of the sphero
        @param state: Sets stabilization on or off
        @type state: bool
        @rtype: response.Response
        @return: SimpleResponse
        """
        return self.write(request.SetStabilization(self.seq, state))

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
        return self.write(request.SetRotationRate(self.seq, val))

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
        raise NotImplementedError

    def set_data_streaming(self):
        raise NotImplementedError

    def configure_collision_detection(self):
        raise NotImplementedError

    def set_back_led_output(self, value):
        """value can be between 0x00 and 0xFF"""
        return self.write(request.SetBackLEDOutput(self.seq, value))

    def roll(self, speed, heading, state=1):
        """
        speed can have value between 0x00 and 0xFF
        heading can have value between 0 and 359

        State:
        As of the 1.13 firmware version.
        State   Speed   Result
        1       > 0     Normal driving
        1       0       Rotate in place
        2       x       Force fast rotation
        0       x       Commence optimal braking to zero speed

        """
        return self.write(request.Roll(self.seq, speed, heading, state))

    def set_boost_with_time(self):
        raise NotImplementedError

    def set_raw_motor_values(self, left_mode=MotorMode.MOTOR_IGNORE, left_power=0x00,
                             right_mode=MotorMode.MOTOR_IGNORE, right_power=0x00):
        """
        Sets a raw value to one or both of spheros engines.

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
        return self.write(request.SetRawMotorValues(self.seq, left_mode, left_power, right_mode, right_power))

    def set_motion_timeout(self):
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

        print hex(flags), bin(flags)
        return self.write(request.SetOptionFlags(self.seq, flags))

    def get_option_flags(self):
        raise NotImplementedError

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

    def abort_orbbasic_program(self):
        raise NotImplementedError

    # BOOTLOADER COMMANDS (still looking for actual docs on these)

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
        return self.write(request.ConfigureLocator(self.seq, flags, x_pos, y_pos, yaw_tare))

    def read_locator(self):
        """
        This reads spheros current X, Y position, component velocities
        and SOG(speed over ground). Position is a signed value in cm.
        The component velocities are signed cm/sec while the SOG is
        unsigned cm/sec.
        @return: response.Response
        """
        return self.write(request.ReadLocator())

    # Additional "higher-level" commands

    def stop(self):
        return self.roll(0, 0)

        pass


if __name__ == '__main__':
    # import time
    # logging.getLogger().setLevel(logging.DEBUG)
    s = SpheroAPI(bt_name="Sphero-YGY", bt_addr="68:86:e7:03:24:54")
    s.connect()
    print s.set_option_flags(stay_on=False,
                             vector_drive=False,
                             leveling=False,
                             tail_LED=False,
                             motion_timeout=False,
                             demo_mode=False,
                             tap_light=False,
                             tap_heavy=False,
                             gyro_max=False).success

    print s.get_power_state()

    for _ in xrange(10):
        try:
            s.set_raw_motor_values(left_mode=MotorMode.MOTOR_FWD, left_power=0xff,
                                   right_mode=MotorMode.MOTOR_FWD, right_power=0xff)

            time.sleep(0.2)
            s.set_raw_motor_values(left_mode=MotorMode.MOTOR_REV, left_power=0xff,
                                   right_mode=MotorMode.MOTOR_REV, right_power=0xff)
            time.sleep(0.2)
            s.set_raw_motor_values(left_mode=MotorMode.MOTOR_BRK,
                                   right_mode=MotorMode.MOTOR_BRK,)
        except SpheroError:
            pass

    s.set_stabilization(True)
    s.disconnect()
    # s.ping()
    #
    # print s.get_power_state()
    # s.set_raw_motor_values(left_mode=MotorMode.MOTOR_FWD, left_power=0xff,
    #                        right_mode=MotorMode.MOTOR_REV, right_power=0xff)
    # time.sleep(5)
    #
    # s.set_raw_motor_values(left_mode=MotorMode.MOTOR_REV, left_power=0xff,
    #                        right_mode=MotorMode.MOTOR_FWD, right_power=0xff)
    # time.sleep(5)
    # s.set_raw_motor_values(left_mode=MotorMode.MOTOR_OFF, right_mode=MotorMode.MOTOR_OFF)
    #
    # s.set_stabilization(True)

    # for x in xrange(100):
    #     try:
    #         print x
    #         s.configure_locator(x, x)
    #         res = s.read_locator()
    #         print res
    #         time.sleep(1)
    #     except:
    #         pass
    #s.sleep()

    # s.set_rgb(0, 255, 0, True)
    # time.sleep(2)
    # s.set_heading(100)
    # #s.sleep(wakeup=10)
    # for _ in xrange(360):
    #     try:
    #         s.roll(0, _)
    #     except SpheroError:
    #         print "Error"
    # #s.connect_all_spheros()
    #
    # # s.connect()
    # #
    # # #print ( s.set_device_name("Sphero-Salmon") )
    # #
    # # print( """Bluetooth info:
    # #     name: %s
    # #     bta: %s
    # #     """
    # #     % ( s.get_bluetooth_info().name,
    # #         s.get_bluetooth_info().bta
    # #       )
    # # )
    # #
    # s.set_rotation_rate(0x00)
    # s.set_heading(0)
    #
    # time.sleep(2)
    # print "READY TO PARTY"

    # import random
    #
    # for _ in xrange(359):
    #     try:
    #         s.set_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), persistant=True)
    #         time.sleep(0.05)
    #     except:
    #         print "msg error"
    #
    # time.sleep(1)
    # # for x in xrange(10):
    # #     s.roll(0x50, 90)
    # #     time.sleep(1)
    # #     s.stop()
    # #     s.roll(0x50, 180)
    # #     time.sleep(1)
    # #     s.stop()
    # #     s.roll(0x50, 270)
    # #     time.sleep(1)
    # #     s.stop()
    # #     s.roll(0x50, 0)
    # #     time.sleep(1)
    # #     s.stop()
    # for x in xrange(10):
    #     s.roll(0x70, 0)
    #     s.stop()
    #     time.sleep(1)
    #     s.roll(0x70, 90)
    #     time.sleep(1)
    #     s.stop()
    # s.set_heading(45)
    # time.sleep(3)
    #
    # time.sleep(10)
    #
    #
    #
    #
    # # handy for debugging calls
    # def raw(did, cid, *data, **kwargs):
    #     req = request.Request(s.seq, *data)
    #     req.did = did
    #     req.cid = cid
    #     if 'fmt' in kwargs:
    #         req.fmt = kwargs['fmt']
    #     res = s.write(req)
    #     logging.debug('request: %s', repr(req.bytes))
    #     logging.debug('response: %s', repr(res.data))
    #     return res
