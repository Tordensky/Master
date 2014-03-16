import random
from threading import Thread
import time
import ps3
import sphero


class ControllableSphero(object):
    def __init__(self, device):
        """

        @param device:
        @type device: sphero.SpheroAPI
        """
        super(ControllableSphero, self).__init__()
        self.msg_retries = 5
        self._last_speed = -1000.0
        self._turn_rate = 0.0
        self.device = device

        self._speed = 0.0
        self._turn = 0.0

        # self.device.set_motion_timeout(2000)
        self._init_motion()

    def _init_motion(self):
        thread = Thread(target=self._motion_thread)
        thread.start()

    def set_ps3_controller(self, ps3_controller):
        """
        Used to map sphero commands to controller

        @param ps3_controller:
        @type ps3_controller: ps3.PS3C
        """
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
        self.device.disconnect()

    def lights_random_color(self):
        r = random.randrange(0, 255)
        g = random.randrange(0, 255)
        b = random.randrange(0, 255)
        print "Lights random color: ", self.device.set_rgb(r, g, b, True).success

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

    def _motion_thread(self):
        while True:
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
        for retry in xrange(self.msg_retries):
            try:
                self.device.roll(int(abs(speed) * 0xFF), heading, 2)
                break
            except sphero.SpheroError:
                print "fails to execute roll cmd %d times" % retry
        else:
            raise sphero.SpheroError