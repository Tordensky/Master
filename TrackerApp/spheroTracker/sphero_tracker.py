import sphero
from sphero.core import SpheroError
import time
import tracker
import random


class SpheroTracker(object):
    def __init__(self):
        self.object_tracker = tracker.StrobeTracker()
        self.sphero_manager = sphero.SpheroManager()

        self.spheros = []

    def start_tracking(self):
        self.sphero_manager.set_sphero_found_cb(self.on_new_sphero)
        self.sphero_manager.start_auto_search()

        while True:
            for sphero_dev in self.spheros:
                try:
                    sphero_dev.set_rgb(random.randrange(0, 255),
                                       random.randrange(0, 255),
                                       random.randrange(0, 255), True)

                except SpheroError as e:
                    print "ERROR: ", e
                    self.spheros.remove(sphero_dev)
                    self.sphero_manager.remove_sphero(sphero_dev)

    def on_new_sphero(self, device):
        """
        @param device: The found sphero device
        @type device: sphero.SpheroAPI
        """
        try:
            print "Found ", device.bt_name, "tries to connect"
            device.connect()
            self.spheros.append(device)
            print "connected", device.bt_name
        except SpheroError as e:
            print e, device.bt_name
            self.sphero_manager.remove_sphero(device)

if __name__ == "__main__":
    sphero_tracker = SpheroTracker()
    sphero_tracker.start_tracking()