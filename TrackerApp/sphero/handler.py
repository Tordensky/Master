import bluetooth
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
        self._sphero_base_name = "Sphero-"
        self.spheros = {}

    def update_nearby_spheros(self, msg_cb=None, finish_cb=None, num_retries=100):
        found_bt_devices = self._find_bt_devices(msg_cb)

        for bdaddr in found_bt_devices:
            device_name = self._get_device_name(bdaddr, num_retries)

            if self._is_sphero(device_name):
                self._add_sphero(bdaddr, device_name)
                msg = "Sphero with name: %s found" % device_name
                self._feedback(msg_cb, msg)

        if self._no_nearby_spheros():
            pass

        elif finish_cb is not None:
            msg = "Found %d spheros: %s" % ((len(self.spheros), self.spheros))
            self._feedback(msg_cb, msg)

        finish_cb() if finish_cb is not None else None

    def _add_sphero(self, bdaddr, device_name):
        if device_name not in self.spheros:
            self.spheros[device_name] = Sphero(device_name, bdaddr)

    def _find_bt_devices(self, msg_cb):
        msg = "Searching for nearby bluetooth devices, please wait . . ."
        self._feedback(msg_cb, msg)
        nearby_devices = bluetooth.discover_devices(duration=20)

        msg = "Found %d nearby devices, searching for spheros . . ." % len(nearby_devices)
        self._feedback(msg_cb, msg)
        return nearby_devices

    def _get_device_name(self, bdaddr, num_retries):
        for _ in xrange(num_retries):
            device_name = bluetooth.lookup_name(bdaddr, timeout=200)
            if device_name is not None and len(device_name):
                return device_name
            time.sleep(0.1)
        return None

    def _no_nearby_spheros(self):
        return len(self.spheros) == 0

    def _is_sphero(self, device_name):
        return device_name is not None and self._sphero_base_name in device_name

    def _feedback(self, callback, msg):
        if callback is not None:
            callback(msg)


def printer(msg):
    print msg

if __name__ == "__main__":
    sm = SpheroHandler()
    sm.update_nearby_spheros(printer)