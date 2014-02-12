import bluetooth
from threading import Thread
import threading
import time
from sphero import SpheroAPI
from sphero.core import SpheroError


class SpheroHandler:
    """
    A class for handling multiple spheros
    @version 1.0
    """

    BT_AUTO_SEARCH_INTERVAL_SEC = 10
    BT_DISCOVER_DEVICES_TIMEOUT_SEC = 10
    BT_NAME_LOOKUP_TIMEOUT_SEC = 5
    BT_NAME_LOOKUP_NUM_RETRIES = 100

    SPHERO_BASE_NAME = "Sphero-"

    def __init__(self):
        self._name_cache = {"68:86:E7:02:3A:AE": "Sphero-RWO",
                            "68:86:E7:03:22:95": "Sphero-ORB",
                            "68:86:E7:03:24:54": "Sphero-YGY"}

        self._known_spheros = {}

        # Auto connection of spheros
        self._sphero_lock = threading.RLock()
        self._run_auto_search = True
        self._search_thread = None

        self._new_sphero_found_cb = None
        self._new_sphero_connected_cb = None

    def get_all_devices(self):
        """
        Returns a list of all spheros that are registered as nearby.
        @rtype: list
        @return: List of registered nearby devices
        """
        nearby_spheros = []
        with self._sphero_lock:
            for name, sphero in self._known_spheros.iteritems():
                nearby_spheros.append(sphero)
        return nearby_spheros

    def get_connected_spheros(self):
        """
        Returns a list of the spheros that are registered as connected.
        @rtype: list
        @return: List of connected devices
        """
        connected_spheros = []
        with self._sphero_lock:
            for name, sphero in self._known_spheros.iteritems():
                if sphero.connected():
                    connected_spheros.append(sphero)
        return connected_spheros

    def start_auto_search(self):
        """
        Starts a thread that runs a auto search for nearby spheros
        Raises a SpheroError if auto search is already started
        @raise: SpheroError
        """
        print "Starts auto search"
        self._run_auto_search = True
        if self._search_thread is None:
            self._search_thread = Thread(target=self._auto_search)
            self._search_thread.start()
        else:
            raise SpheroError("Auto search is already running")

    def _auto_search(self):
        while self._run_auto_search:
            self.search()
            time.sleep(SpheroHandler.BT_AUTO_SEARCH_INTERVAL_SEC)
        self._search_thread = None
        print "Stops auto search"

    def stop_auto_search(self):
        """
        Stops auto search if auto search is activated
        @return:
        """
        if self._search_thread is not None:
            self._run_auto_search = False

    def search(self, async=False):
        """
        Starts a single search for nearby spheros
        @param async: Boolean. If set to True, search is run in a thread
        @return:
        """
        if async:
            thread = Thread(target=self._update_nearby_spheros)
            thread.start()
        else:
            self._update_nearby_spheros()

    def remove_dev(self, sphero):
        """
        Removes the given sphero device from connected and nearby devices
        @param sphero: The sphero object that should be removed
        @return:
        """
        with self._sphero_lock:
            self._known_spheros.pop(sphero.bt_name)
            sphero.disconnect()
        #self._connected_spheros.remove(sphero)
        print "REMOVES DEVICE THAT FAILED"

    def _update_nearby_spheros(self):
        for bdaddr in self._find_nearby_bt_devices():
            device_name = self._get_device_name(bdaddr, SpheroHandler.BT_NAME_LOOKUP_NUM_RETRIES)

            if self._is_sphero(device_name):
                self._add_nearby_sphero(bdaddr, device_name)

    def _add_nearby_sphero(self, bdaddr, device_name):
        with self._sphero_lock:
            if device_name not in self._known_spheros:
                new_sphero = SpheroAPI(device_name, bdaddr)
                self._known_spheros[device_name] = new_sphero
                self._notify_sphero_found(new_sphero)

    @staticmethod
    def _find_nearby_bt_devices():
        print "Searching for nearby bluetooth devices, please wait . . ."
        nearby_devices = bluetooth.discover_devices(duration=SpheroHandler.BT_DISCOVER_DEVICES_TIMEOUT_SEC,
                                                    flush_cache=False)
        print "Found %d nearby devices" % len(nearby_devices)
        return nearby_devices

    def _get_device_name(self, bdaddr, num_retries):
        if bdaddr in self._name_cache.iterkeys():
            return self._name_cache[bdaddr]

        for _ in xrange(num_retries):
            device_name = bluetooth.lookup_name(bdaddr, timeout=SpheroHandler.BT_NAME_LOOKUP_TIMEOUT_SEC)
            if device_name is not None and len(device_name):
                self._name_cache[bdaddr] = device_name
                return device_name
            time.sleep(0.1)
        return None

    @staticmethod
    def _is_sphero(device_name):
        return device_name is not None and SpheroHandler.SPHERO_BASE_NAME in device_name

    def set_sphero_found_callback(self, cb):
        """
        Allows for the uses of the class to set a callback when a new sphero is detected from the search method
        @param cb: the callback method that should be called when a new sphero is detected
        @return:
        """
        self._new_sphero_found_cb = cb

    def _notify_sphero_found(self, new_sphero):
        if self._new_sphero_found_cb is not None:
            thread = Thread(target=self._new_sphero_found_cb, args=(new_sphero,))
            thread.start()
        else:
            print "no callback registered"

## FOR TESTING
def callback(sphero):
    print "CALLBACK", sphero.bt_name
    sphero.connect()
    #try
    #print sphero.ping()
    #time.sleep(20)
    #print "ALL:", sm.get_all_devices()
    #print "CON:", sm.get_connected_spheros()
    #sphero.disconnect()
    print "ALL:", sm.get_all_devices()
    print "CON:", sm.get_connected_spheros()


if __name__ == "__main__":
    sm = SpheroHandler()
    sm.set_sphero_found_callback(callback)
    sm.start_auto_search()
