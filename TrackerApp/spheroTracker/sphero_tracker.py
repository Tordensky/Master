import time
import sphero
import tracker


class SpheroTracker(object):
    def __init__(self):
        self.object_tracker = tracker.StrobeTracker()
        self.sphero_handler = sphero.SpheroHandler()

    def start_tracking(self):
        self.sphero_handler.update_nearby_spheros(msg_cb=self.msg_cb)
        for sp_name, sphero_dev in self.sphero_handler.spheros.iteritems():
            print sp_name, sphero_dev.connect()

        while True:
            for sp_name, sphero_dev in self.sphero_handler.spheros.iteritems():
                try:
                    sphero_dev.set_rgb(0xFF, 0xFF, 0xFF, True)
                    print sp_name, self.object_tracker.track_object().get_pos()
                    time.sleep(0.01)
                    sphero_dev.set_rgb(0, 0, 0, True)
                except:
                    print "ERROR"

    def msg_cb(self, msg):
        print msg


if __name__ == "__main__":
    sphero_tracker = SpheroTracker()
    sphero_tracker.start_tracking()