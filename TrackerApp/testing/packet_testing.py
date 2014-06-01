from threading import Thread
import time
import sphero
from util.timer import StopWatch


class PacketTester(object):
    def __init__(self, num_devices, num_samples):
        super(PacketTester, self).__init__()

        self.num_samples = num_samples
        self.manager = sphero.SpheroManager()
        self.devices = []

        self.num_devices = num_devices

        self.results = []

        self.num_streams = 0

    def init(self):
        while len(self.devices) < self.num_devices:
            device = self.manager.get_available_device()
            if device and device.connect():
                device.set_option_flags(stay_on=True)
                print "new device connected"
                self.devices.append(device)

        # init samples
        for x in xrange(self.num_samples):
            self.results.append({"sample": x})

    @staticmethod
    def test_name(name, num_devices):
        return "%s n_dev: %d" % (name, num_devices)

    def _create_test_device_lists(self):
        devices_to_test = []
        for x in xrange(len(self.devices)):
            devices_to_test.append(self.devices[:x+1])
        return devices_to_test

    def save_results(self, filename):
        lines = []
        line = ""
        for key in sorted(self.results[0]):
            line += "{},".format(key)



        lines.append(line[:-1])
        for result in self.results:
            line = ""
            data_list = []
            for key in sorted(result):
                data_list.append(result[key])
                line += "{},".format(result[key])
            lines.append(line[:-1])

        print "avg:", sum(data_list) / len(data_list)
        print "max:", max(data_list)
        print "min:", min(data_list)

        with open(filename, "w") as file:
            for line in lines:
                print line
                file.write(line+"\n")

    def activate_streaming(self, sample_rate):
        print "activate streaming"
        for device in self.devices:
            #device.stop_data_streaming()
            ssc = sphero.SensorStreamingConfig()
            ssc.num_packets = ssc.STREAM_FOREVER
            ssc.sample_rate = sample_rate
            ssc.stream_all()
            device.set_data_streaming(ssc)

    def test_max_packets_sequential(self, name="seq"):
        print "SEQ MAX"


        stop_watch = StopWatch()
        for devices in self._create_test_device_lists():
            for result in self.results:

                # PERFORM TEST
                stop_watch.start()
                for device in devices:
                    self._sphero_test_command(device)

                time = stop_watch.stop()
                result[self.test_name(name, len(devices))] = time

    def test_max_packets_threads(self):
        print "THREAD MAX"

        name = "threads"
        stop_watch = StopWatch()

        for devices in self._create_test_device_lists():
            for result in self.results:

                # PERFORM TEST
                threads = []
                stop_watch.start()
                for device in devices:
                    thread = Thread(target=self._sphero_test_command, args=(device, ))
                    threads.append(thread)
                    thread.start()
                    self._sphero_test_command(device)

                for thread in threads:
                    thread.join()

                time = stop_watch.stop()
                result[self.test_name(name, len(devices))] = time

    def streaming_test(self, sample_rate):
        stop_watch = StopWatch()
        self.devices[0].set_sensor_streaming_cb(self.on_streaming)
        name = "streaming n-per_sec", sample_rate
        for sample in self.results:
            stop_watch.start()
            self.num_streams = 0
            while self.num_streams < sample_rate:
                pass
            time = stop_watch.stop()
            sample[name] = time

    def on_streaming(self, *args):
        self.num_streams += 1

    @staticmethod
    def _sphero_test_command(device):
        device.ping()

    def clean_up(self):
        for device in self.devices:
            device.disconnect()


if __name__ == "__main__":
    tester = PacketTester(num_devices=1, num_samples=1000)
    tester.init()

    # RUN TEST
    # for x in [1, 5, 10, 20, 50, 75, 100, 200, 400]:
    #     print "test stream n", x
    #     tester.activate_streaming(x)
    #     time.sleep(1.0)
    #     tester.streaming_test(x)

    tester.test_max_packets_sequential()
    #tester.activate_streaming(20)
    #tester.test_max_packets_sequential(name="with-streaming")
    #
    #tester.test_max_packets_threads()

    tester.save_results("packet_testingAfterFix.txt")
    tester.clean_up()