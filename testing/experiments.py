import sphero
import util


class PacketTester(object):
    def __init__(self):
        super(PacketTester, self).__init__()
        self.sphero_manager = sphero.SpheroManager()
        self.sphero_manager.set_sphero_found_cb(self.on_new_sphero)

        self.devices = []

        self.iterations = 10000
        self.num_packets = 1
        self.num_devices = 1

        self.stop_watch = util.StopWatch()

    def start(self):
        self.sphero_manager.start_auto_search()

        while len(self.devices) < self.num_devices:
            pass

        #self.sphero_manager.stop_auto_search()
        # Test packets per second

        results = []

        for _ in xrange(self.iterations):
            self.stop_watch.start()
            for x in xrange(0, self.num_packets):
                self.devices[0].set_rgb(0, 0, x % 255, True)

            time_used = self.stop_watch.stop()
            time_per_packet = time_used / self.num_packets
            packets_per_second = self.num_packets / time_used

            results.append((self.num_packets, time_used, time_per_packet, packets_per_second))
            print "packets:", self.num_packets, "time used: ", time_used, "sec/packet: ", time_per_packet, "pack/sec: ", packets_per_second

        with open("measure/packets.txt", "w") as file:
            file.write("num_packets, time_used, sec/packet, packet/sec\n")
            for result in results:
                data = "{}, {}, {}, {}\n".format(*result)
                file.write(data)

    def end(self):
        pass

    def on_new_sphero(self, device):
        print "new device:", device.bt_name
        if device.connect():
            print "new device connected"
            self.devices.append(device)


if __name__ == "__main__":
    print "test start"
    packet_test = PacketTester()
    packet_test.start()