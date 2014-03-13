import random
from threading import Thread
import time
import ps3
import sphero


class SpheroControls(object):
    def __init__(self, device):
        """

        @param device:
        @type device: sphero.SpheroAPI
        """
        super(SpheroControls, self).__init__()
        self.device = device

        self._speed = 0.0
        self._heading = 0.0

        #self.device.set_motion_timeout(2000)
        thread = Thread(target=self._motion_thread)
        thread.start()

    def map_controls(self, ps3_controller):
        """
        Used to map sphero commands to controller

        @param ps3_controller:
        @type ps3_controller: ps3.PS3C
        """
        ps3_controller.set_events(
            button_press={
                ps3.BUTTON_CIRCLE: self.ping,
                ps3.BUTTON_SQUARE: self.lights_off,
                ps3.BUTTON_X: self.lights_random_color,
                ps3.BUTTON_START: self.disconnect,

                ps3.BUTTON_JOY_PAD_LEFT: self.get_battery_state
            },
            axis={
                ps3.AXIS_JOY_L_VER: self.set_speed,
                ps3.AXIS_JOY_R_HOR: self.set_turn
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

    def set_speed(self, value):
        self._speed = value

    def set_turn(self, value):
        self._heading += value

    def _motion_thread(self):
        while True:
            self._roll(self._speed)

    def _calc_heading(self, speed):
        if speed > 0.2:
            direction = (self._heading - 180) % 359
        else:
            direction = self._heading % 359
        return direction

    def _roll(self, speed):
        print "roll"
        heading = self._calc_heading(speed)
        try:
            self.device.roll(int(abs(speed) * 0xFF), heading, 1)
        except sphero.SpheroError:
            print "FAILS TO EXECUTE ROLL"


class SpheroPS3(object):
    def __init__(self):
        super(SpheroPS3, self).__init__()
        self.ps3_manager = ps3.PS3manager()

        self.sphero_manager = sphero.SpheroManager()
        self.sphero_manager.set_sphero_found_cb(self.on_new_sphero)

    def run(self):
        if self.sphero_manager.search():
            self.ps3_manager.start()
            while True:
                pass
        else:
            print "NO DEVICES FOUND"

    def on_new_sphero(self, device):
        """
        Callback when new spheros are found
        @param device:
        @type device: sphero.SpheroAPI
        """
        print device.bt_name
        if device.connect():
            ps3_controller = self.ps3_manager.get_controllers()[0]
            sphero_controls = SpheroControls(device)
            sphero_controls.map_controls(ps3_controller)

if __name__ == "__main__":
    sphero_ps3 = SpheroPS3()
    sphero_ps3.run()