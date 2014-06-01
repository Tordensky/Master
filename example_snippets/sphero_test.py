from threading import Thread
import time
import sphero


class SpheroTest(object):
    def __init__(self, device):
        """

        @param device:
         @type device: sphero.SpheroAPI
        """
        super(SpheroTest, self).__init__()
        self.device = device

    def start(self):
        #self.device.connect()
        #self.spam_cmds(10)
        self.test_multi_threading()

        # self.test_not_connected()

        # self.test_multiple_connects_disconnects()

    def test_multiple_connects_disconnects(self):
        if self.device.connected:
            self.device.disconnect()
        for x in range(0, 1):
            if self.device.connect():
                print "successfully connects"
            result = True
            for y in range(0, 255):
                result = result and self.device.set_rgb(y, y, y).success
                result = result and self.device.ping().success
                result = result and self.device.read_locator().success
            print x, "sets rgb", result
            if self.device.disconnect():
                print "successfully disconnects"

    def test_not_connected(self):
        if self.device.connected():
            self.device.disconnect()
        try:
            self.device.set_rgb(255, 0, 0, persistent=True)
        except sphero.SpheroConnectionError:
            print "Device is not connected, tries to connect"
            if self.device.connect():
                print "successfully connects"
        finally:
            if self.device.disconnect():
                print "successfully disconnects"

    def test_multi_threading(self):
        threads = []
        if not self.device.connected():
            if self.device.connect():
                for x in range(0, 300):
                    thread = Thread(target=self.spam_cmds, args=(x, ), name="spam_thread: %d" % x)
                    threads.append(thread)
                    thread.start()
                    time.sleep(0.01)
                for thread in threads:
                    thread.join()
            print "All finished"
        self.device.disconnect()

    def spam_cmds(self, thread_id):
        print "Starts thread:", thread_id
        result = True
        for y in range(0, 10):
            try:
                result = result and self.device.ping().success
                time.sleep(0.1)
                # if y % 10 == 0:
                #     print id, "successfully", result
            except sphero.SpheroRequestError as e:
                print "thread: ", thread_id, y,  "REQ FAIL:", e.message
                time.sleep(1.0)
        print "thread", thread_id, "success:", result

if __name__ == "__main__":
    s2 = sphero.SpheroAPI(bt_name="Sphero-YGY", bt_addr="68:86:e7:03:22:95")  # SPHERO-ORB NO: 4
    s3 = sphero.SpheroAPI(bt_name="Sphero-YGY", bt_addr="68:86:e7:02:3a:ae")  # 2
    tester1 = SpheroTest(s2)

    tester1.start()