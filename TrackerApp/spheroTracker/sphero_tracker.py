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
        self.sphero_handler.start_auto_connect_spheros()

        while True:
            for sphero_dev in self.sphero_handler.get_connected_spheros():
                try:
                    sphero_dev.set_rgb(0xFF, 0xFF, 0xFF, True)
                    time.sleep(0.8)
                    print self.object_tracker.track_object().get_pos()
                    sphero_dev.set_rgb(0, 0, 0, True)
                except BluetoothError:
                    try:
                        sphero_dev.ping()
                    except:
                        self.sphero_handler.remove_dev(sphero_dev)
                        print "COULD NOT PING"
                    # TODO disconnect sphero if its not communicating
                    print "BT error:", sys.exc_info()[1][0]
                except SpheroError:
                    print "Message error"
                except:
                    print "Unexpected error:", sys.exc_info()



if __name__ == "__main__":
    sphero_tracker = SpheroTracker()
    sphero_tracker.start_tracking()