import time
from controllable import ControllableSphero
import ps3
import sphero
import tracker


class SpheroPS3Controls(object):
    # TODO on controller disconnected or, sphero failed handling

    def __init__(self):
        super(SpheroPS3Controls, self).__init__()
        self._ps3_manager = ps3.PS3manager()
        self._sphero_manager = sphero.SpheroManager()

        self._tracker = tracker.ColorTracker()

        self._controllable_devices = []

        self._init_sphero()

    def _init_sphero(self):
        self._sphero_manager.set_sphero_found_cb(self.on_new_sphero)

    def run(self):
        self._sphero_manager.start_auto_search()
        self._ps3_manager.start()
        while True:
            traceable_objects = []
            for controllable in self._controllable_devices:
                traceable_objects.append(controllable.traceable)

            self._tracker.track_objects(traceable_objects)
            time.sleep(1.0 / 25.0)

    def on_new_sphero(self, device):
        """
        Callback when new spheros are found
        @param device:
        @type device: sphero.SpheroAPI
        """
        print "NEW Sphero: ", device.bt_name
        ps3_ctrl = self._ps3_manager.get_available_controller()
        if ps3_ctrl:
            if device.connect():
                controllable_sphero = ControllableSphero(device)
                controllable_sphero.set_sphero_disconnected_cb(self.clean_up_sphero_dev)
                controllable_sphero.set_ps3_controller(ps3_ctrl)

                self._controllable_devices.append(controllable_sphero)
                print "Controls successfully setup"
                return
        else:
            print "No free PS3 controller available"

        self.clean_up_sphero_dev(device)

    def clean_up_sphero_dev(self, device):
        device.disconnect()
        try:
            self._controllable_devices.remove(device)
        except ValueError:
            pass
        self._sphero_manager.remove_sphero(device)


if __name__ == "__main__":
    sphero_ps3 = SpheroPS3Controls()
    sphero_ps3.run()