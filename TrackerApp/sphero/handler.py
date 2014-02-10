import bluetooth
from threading import Thread
import threading
import time
from sphero import Sphero


class SpheroProp(object):
    name = None
    bdaddr = None
    socket = None

    def __init__(self, name=None, bdaddr=None):
        self.name = name
        self.bdaddr = bdaddr

    def __repr__(self):
        return "%s @ %s" % (self.name, self.bdaddr)

    def set_socket(self, socket):
        self.socket = socket


class SpheroHandler:
    def __init__(self):
        self._name_cache = {}
        self._BASE_NAME = "Sphero-"
        self._spheros = {}

        self._sphero_lock = threading.RLock()

        self._run_auto_connect = True

        self._con_thread = None

    def start_auto_connect_spheros(self):
        if self._con_thread is None:
            self._con_thread = Thread(target=self._auto_connect_helper)
            self._con_thread.start()
        else:
            # TODO add exception
            print "Thread is already started"

    def _auto_connect_helper(self):
        while self._run_auto_connect:
            self._update_nearby_spheros(msg_cb=self._printer)
            self._connect_new_devices()
            time.sleep(10)

    def _connect_new_devices(self):
        with self._sphero_lock:
            for name, sphero in self._spheros.iteritems():
                if not sphero.connected():
                    sphero.connect()
                    print "CONNECTS NEW SPHERO"

    def get_connected_spheros(self):
        connected_spheros = []
        with self._sphero_lock:
            for name, sphero in self._spheros.iteritems():
                if sphero.connected():
                    connected_spheros.append(sphero)
        return connected_spheros

    def _update_nearby_spheros(self, msg_cb=None, num_retries=100):
        found_bt_devices = self._find_bt_devices(msg_cb)

        nearby_spheros = {}
        for bdaddr in found_bt_devices:
            device_name = self._get_device_name(bdaddr, num_retries)

            if self._is_sphero(device_name):
                msg = "Sphero with name: %s found" % device_name
                self._msg_caller(msg_cb, msg)

                nearby_spheros[device_name] = bdaddr

        for device_name, bdaddr in nearby_spheros.iteritems():
            print "device_name", device_name
            self._add_sphero(bdaddr, device_name)

        #self._update_sphero_list(nearby_spheros)

    def remove_dev(self, sphero_dev):
        with self._sphero_lock:
            print "REMOVES DEVICE THAT FAILED"
            self._spheros.pop(sphero_dev.bt_name)

    def _update_sphero_list(self, nearby_devices):
        # TODO possible not working and must be removed
        remove_items = []
        with self._sphero_lock:
            for sphero in self._spheros:
                if sphero not in nearby_devices.iterkeys():
                    remove_items.append(sphero)

            for dev in remove_items:
                print sphero, " no longer nearby"
                self._spheros.pop(dev)

    def _add_sphero(self, bdaddr, device_name):
        print "ADDDS NEW SPHERO!!!!!!!!!!!!!!!"
        with self._sphero_lock:
            if device_name not in self._spheros:
                self._spheros[device_name] = Sphero(device_name, bdaddr)

    def _find_bt_devices(self, msg_cb):
        msg = "Searching for nearby bluetooth devices, please wait . . ."
        self._msg_caller(msg_cb, msg)
        nearby_devices = bluetooth.discover_devices(duration=5)

        msg = "Found %d nearby devices" % len(nearby_devices)
        self._msg_caller(msg_cb, msg)
        return nearby_devices

    def _get_device_name(self, bdaddr, num_retries):
        if bdaddr in self._name_cache.iterkeys():
            return self._name_cache[bdaddr]

        for _ in xrange(num_retries):
            device_name = bluetooth.lookup_name(bdaddr, timeout=200)
            if device_name is not None and len(device_name):
                self._name_cache[bdaddr] = device_name
                return device_name
            time.sleep(0.1)
        return None

    def _is_sphero(self, device_name):
        return device_name is not None and self._BASE_NAME in device_name

    @staticmethod
    def _msg_caller(callback, msg):
        if callback is not None:
            callback(msg)

    @staticmethod
    def _printer(msg):
        print msg


if __name__ == "__main__":
    sm = SpheroHandler()
    sm._update_nearby_spheros(printer)