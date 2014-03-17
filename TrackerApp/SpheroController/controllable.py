import random
from threading import Thread
import time
import ps3
import sphero


class ControllableSphero(object):
    def __init__(self, device):
        """

        @param device: The device to control
        @type device: sphero.SpheroAPI
        """
        super(ControllableSphero, self).__init__()
        self._run_motion = True
        self.sphero_clean_up_cb = None
        self.motion_timeout = 3000
        self.cmd_retries = 5

        self._device = device
        self._last_speed = -1000.0
        self._turn_rate = 0.0

        self._speed = 0.0
        self._turn = 0.0

        self._ps3_controller = None

        self._setup_sphero()
        self._init_motion_control()

    def _setup_sphero(self):
        self._device.set_option_flags(
            motion_timeout=True,
            tail_LED=True
        )
        self._device.set_motion_timeout(self.motion_timeout)
        self._device.set_rgb(0xFF, 0xFF, 0xFF, True)

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

                ps3.BUTTON_JOY_PAD_LEFT: self.get_battery_state
            },
            axis={
                ps3.AXIS_JOYSTICK_L_VER: self._set_speed,
                ps3.AXIS_JOYSTICK_R_HOR: self._set_turn_rate
            }
        )

    def disconnect(self):
        self._device.disconnect()
        self._on_sphero_disconnected()

    def lights_random_color(self):
        r = random.randrange(0, 255)
        g = random.randrange(0, 255)
        b = random.randrange(0, 255)
        print "Lights random color: ", self._device.set_rgb(r, g, b, True).success

    def lights_off(self):
        print "LIGHTS OFF:", self._device.set_rgb(0, 0, 0, True).success

    def ping(self):
        print "PING SUCCESSFUL:", self._device.ping().success

    def get_battery_state(self):
        print self._device.get_power_state()

    def _set_speed(self, value):
        self._speed = value

    def _set_turn_rate(self, value):
        self._turn_rate = value * 10.0

    def _has_new_command(self):
        if self._turn_rate or self._speed != self._last_speed:
            self._last_speed = self._speed
            return True
        return False

    def _motion_thread(self):
        while self._run_motion:
            # TODO make this at a fixed speed e.g 25fps
            if self._has_new_command():
                self._move(self._speed)
            time.sleep(1.0 / 50.0)

    def _get_heading(self, speed):
        self._turn += self._turn_rate
        if speed > 0.01:
            # Drive in reverse
            return (self._turn - 180) % 359
        return self._turn % 359

    def _move(self, speed):
        heading = self._get_heading(speed)
        for retry in xrange(self.cmd_retries):
            try:
                self._device.roll(int(abs(speed) * 0xFF), heading, 2)
                break
            except sphero.SpheroError:
                print "fails to execute roll cmd %d times" % retry
        else:
            raise sphero.SpheroError

    def set_sphero_disconnected_cb(self, cb):
        self.sphero_clean_up_cb = cb

    def _on_sphero_disconnected(self):
        print "PS3 / SPHERO clean up"
        if self._ps3_controller:
            self._ps3_controller.free()
        self.sphero_clean_up_cb(self._device)