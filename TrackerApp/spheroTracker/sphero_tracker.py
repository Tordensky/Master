from bluetooth import BluetoothError
import time
import sys
import sphero
from sphero.core import SpheroError
import tracker


class SpheroTracker(object):
    def __init__(self):
        self.object_tracker = tracker.StrobeTracker()
        self.sphero_handler = sphero.SpheroHandler()

    def start_tracking(self):
        self.sphero_handler.set_sphero_found_callback(self.found_new_sphero_cb)
        self.sphero_handler.start_auto_search()

        while True:
            for sphero_dev in self.sphero_handler.get_connected_spheros():

                try:
                    sphero_dev.set_rgb(0xFF, 0xFF, 0xFF, True)
                    time.sleep(0.1)
                    self.object_tracker.track_object().get_pos()
                    sphero_dev.set_rgb(0, 0, 0, True)

                except BluetoothError as eb:
                    print "ERR NO;", eb.message
                    if eb.message == "(107, 'Transport endpoint is not connected')":
                        self.sphero_handler.remove_dev(sphero_dev)
                    print "BT error:", sys.exc_info()

                except SpheroError:
                    print "Message error"

                except:
                    print "Unexpected error:", sys.exc_info()

    @staticmethod
    def found_new_sphero_cb(device):
        print "FOUND NEW SPHERO"
        device.connect()

if __name__ == "__main__":
    sphero_tracker = SpheroTracker()
    sphero_tracker.start_tracking()