from bluetooth import BluetoothError
import time
import sys
import sphero
from sphero.core import SpheroError
import tracker


class SpheroTracker(object):
    def __init__(self):
        self.object_tracker = tracker.StrobeTracker()
        self.sphero_manager = sphero.SpheroManager()

    def start_tracking(self):
        self.sphero_manager.set_sphero_found_cb(self.on_found_new_sphero_cb)
        self.sphero_manager.start_auto_search()

        while True:
            for sphero_dev in self.sphero_manager.get_connected_spheros():

                try:
                    sphero_dev.set_rgb(0xFF, 0xFF, 0xFF, True)
                    time.sleep(0.1)
                    self.object_tracker.track_object().get_pos()
                    sphero_dev.set_rgb(0, 0, 0, True)

                except BluetoothError as eb:
                    print "ERR NO;", eb.message
                    # Ugly fix because the BluetoothError does not serve a nice way to
                    # check the exception type or number
                    if eb.message == "(107, 'Transport endpoint is not connected')":
                        self.sphero_manager.remove_dev(sphero_dev)
                    print "BT error:", sys.exc_info()

                except SpheroError:
                    print "Message error"

    @staticmethod
    def on_found_new_sphero_cb(device):
        print "FOUND NEW SPHERO"
        device.connect()

if __name__ == "__main__":
    sphero_tracker = SpheroTracker()
    sphero_tracker.start_tracking()