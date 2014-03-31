import random
from threading import Thread
import time
import math

from SpheroController.tracablesphero import SpheroTraceable
import ps3
import sphero
from sphero import SensorStreamingConfig, MotorMode, SpheroError


class ControllableSphero(object):
    def __init__(self, device):
        """

        @param device: The device to control
        @type device: sphero.SpheroAPI
        """
        super(ControllableSphero, self).__init__()
        self.device = device

        self._sphero_clean_up_cb = None
        self._cmd_retries = 5

        self._ps3_controller = None

        # SENSOR STREAMING
        self._ssc = SensorStreamingConfig()

        # SPHERO TRACKING
        self.traceable = SpheroTraceable(name=self.device.bt_name, device=self.device)

        # MOTION
        self._run_motion = True
        self._motion_timeout = 3000
        self._last_speed = -1000.0
        self._turn_rate = 0.0
        self._speed = 0.0
        self._turn = 0.0

        # RAW ENGINE MOTION
        self._stabilization = True
        self._raw_left = 0.0
        self._raw_right = 0.0

        # SETUP
        self._setup_sphero()
        self._init_motion_control()

    def _configure_sensor_streaming(self):
        self._ssc.num_packets = SensorStreamingConfig.STREAM_FOREVER
        self._ssc.sample_rate = 5
        self._ssc.stream_odometer()
        self._ssc.stream_imu_angle()
        self._ssc.stream_velocity()
        self.device.set_sensor_streaming_cb(self._on_data_streaming)
        self.device.set_data_streaming(self._ssc)

    def _setup_sphero(self):
        self.device.set_option_flags(
            motion_timeout=True,
            tail_LED=True
        )
        self.device.set_motion_timeout(self._motion_timeout)
        self.device.set_rgb(0xFF, 0xFF, 0xFF, True)

        self._configure_sensor_streaming()

    def _on_data_streaming(self, response):
        """
        @param response: Streaming response from sphero
        @type response: sphero.SensorStreamingResponse
        """
        self.traceable.set_data(response.sensor_data)

    def _init_motion_control(self):
        thread = Thread(target=self._motion_thread, name="SpheroMotionThread")
        thread.daemon = True
        thread.start()

    def set_ps3_controller(self, ps3_controller):
        """
        Used to set and map the PS3 controller to run the sphero commands

        @param ps3_controller:
        @type ps3_controller: ps3.PS3C
        """
        self._ps3_controller = ps3_controller
        self._map_controls(ps3_controller)

    def _map_controls(self, ps3_controller):
        ps3_controller.set_events(
            button_press={
                ps3.BUTTON_CIRCLE: self.ping,
                ps3.BUTTON_SQUARE: self.lights_off,
                ps3.BUTTON_CROSS: self.lights_random_color,
                ps3.BUTTON_START: self.disconnect,

                ps3.BUTTON_JOY_PAD_LEFT: self.get_battery_state,
                ps3.BUTTON_JOY_PAD_UP: self.reset_locator,

                ps3.BUTTON_L1: self.spin_left,
                ps3.BUTTON_R1: self.spin_right
            },
            button_release={
                ps3.BUTTON_L1: self.stop_spin,
                ps3.BUTTON_R1: self.stop_spin
            },
            axis={
                ps3.AXIS_JOYSTICK_L_VER: self._set_speed,
                ps3.AXIS_JOYSTICK_R_HOR: self._set_turn_rate,
                ps3.AXIS_R2: self.set_raw_left,
                ps3.AXIS_L2: self.set_raw_right
            }
        )

    def reset_locator(self):
        self.device.set_heading(0)
        #self.device.configure_locator(0, 0, 0)

    def disconnect(self):
        self.device.disconnect()
        self._on_sphero_disconnected()

    def lights_random_color(self):
        r = random.randrange(0, 255)
        g = random.randrange(0, 255)
        b = random.randrange(0, 255)
        print "Lights random color: ", self.device.set_rgb(r, g, b, True).success

    def spin_left(self):
        self._raw_right = 255.0
        self._raw_left = 255.0
        self.device.set_raw_motor_values(MotorMode.MOTOR_REV, self._raw_left, MotorMode.MOTOR_FWD, self._raw_right)

    def spin_right(self):
        self._raw_right = 255.0
        self._raw_left = 255.0
        self.device.set_raw_motor_values(MotorMode.MOTOR_FWD, self._raw_left, MotorMode.MOTOR_REV, self._raw_right)

    def stop_spin(self):
        self._raw_right = 0.0
        self._raw_left = 0.0
        self.set_raw_engine()

    @staticmethod
    def to_motor_value(value):
        value = (value + 1.0) / 2.0
        if value > 0.0:
            return min([abs(math.floor(value * 255.0)), 255])
        return 0.0

    def set_raw_left(self, value):
        self._raw_left = self.to_motor_value(value)
        self.set_raw_engine()

    def set_raw_right(self, value):
        self._raw_right = self.to_motor_value(value)
        self.set_raw_engine()

    def set_raw_engine(self):
        if self._raw_left or self._raw_right:
            self._stabilization = False
            print self._raw_left, self._raw_right
            self.device.set_raw_motor_values(MotorMode.MOTOR_FWD, self._raw_left, MotorMode.MOTOR_FWD, self._raw_right)
        else:
            if not self._stabilization:
                self.device.set_stabilization(True)
                self._stabilization = True

    def lights_off(self):
        print "LIGHTS OFF:", self.device.set_rgb(0, 0, 0, True).success

    def ping(self):
        print "PING SUCCESSFUL:", self.device.ping().success

    def get_battery_state(self):
        print self.device.get_power_state()

    def _set_speed(self, value):
        self._speed = value

    def _set_turn_rate(self, value):
        self._turn_rate = value * 10.0

    def _has_new_command(self):
        if self._turn_rate or self._speed != self._last_speed:
            self._last_speed = self._speed
            return True
        return False

    def _get_heading(self, speed):
        self._turn += self._turn_rate
        if speed > 0.01:
            # Drive in reverse
            return (self._turn - 180) % 359
        return self._turn % 359

    def _motion_thread(self):
        while self._run_motion:
            # TODO make this at a fixed speed e.g 25fps
            if self._has_new_command():
                self._move(self._speed)
            time.sleep(1.0 / 50.0)

    def _move(self, speed):
        heading = self._get_heading(speed)
        for retry in xrange(self._cmd_retries):
            try:
                self.device.roll(int(abs(speed) * 0xFF), heading, 2)
                break
            except SpheroError:
                print "fails to execute roll cmd %d times" % retry
        else:
            self.disconnect()
            print "SPHERO FAILS TO COMMUNICATE"
            #raise sphero.SpheroError

    def set_sphero_disconnected_cb(self, cb):
        self._sphero_clean_up_cb = cb

    def _on_sphero_disconnected(self):
        print "PS3 / SPHERO clean up"
        if self._ps3_controller:
            self._ps3_controller.free()
        self._sphero_clean_up_cb(self.device)