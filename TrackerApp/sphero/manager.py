import bluetooth
from threading import Thread
import threading
import time
from sphero import SpheroAPI
from sphero.core import SpheroError


class SpheroManager:
    """
    A class for handling searching for spheros
    @version 0.2
    """

    BT_AUTO_SEARCH_INTERVAL_SEC = 5
    BT_NAME_LOOKUP_TIMEOUT_SEC = 10
    BT_NAME_LOOKUP_NUM_RETRIES = 10

    SPHERO_BASE_NAME = "Sphero-"

    # TODO Get Sphero by name
    # TODO Get Sphero by address
    # TODO Get any available sphero device

    def __init__(self):
        self._name_cache = {"68:86:E7:02:3A:AE": "Sphero-RWO",
                            "68:86:E7:03:22:95": "Sphero-ORB",
                            "68:86:E7:03:24:54": "Sphero-YGY"}

        self._spheros = {}

        self._sphero_lock = threading.RLock()
        self._run_auto_search = True
        self._search_thread = None

        self._sphero_found_cb = None  # TODO add support for multiple callbacks?

    def get_all_devices(self):
        """
        Returns a list of all spheros that are registered as nearby.
        @rtype: list
        @return: List of registered nearby devices
        """
        with self._sphero_lock:
            return [sphero for sphero in self._spheros.values()]

    def get_connected_spheros(self):
        """
        Returns a list of the spheros that are registered as connected.
        @rtype: list
        @return: List of connected devices
        """
        return [sphero for sphero in self.get_all_devices() if sphero.connected()]

    def start_auto_search(self):
        """
        Starts a thread that runs a auto search for nearby spheros
        Raises a SpheroError if auto search is already started
        @raise: SpheroError
        """
        # TODO could make so an argument could set the number of times to search 0 is search forever
        print "Starts auto search"
        self._run_auto_search = True
        if self._search_thread is None:
            self._search_thread = Thread(target=self._auto_search_loop)
            self._search_thread.start()
        else:
            raise SpheroError("Auto search is already running")

    def stop_auto_search(self):
        """
        Stops auto search if auto search is activated
        @return:
        """
        if self._search_thread is not None:
            self._run_auto_search = False

    def _auto_search_loop(self):
        """
        Helper method that runs the asynchronous automatic search loop
        """
        # TODO: Make it possible to stop the search immediately
        while self._run_auto_search:
            self.search()
            time.sleep(SpheroManager.BT_AUTO_SEARCH_INTERVAL_SEC)

        self._search_thread = None

    def search(self):
        """
        Starts a search for nearby spheros. When nearby spheros is found
        the pre set found_nearby_sphero_cb is triggered
        """
        for bdaddr in self._find_nearby_bt_devices():
            device_name = self._get_device_name(bdaddr)

            if self._is_sphero(device_name):
                self.add_sphero(bdaddr, device_name)

    def add_sphero(self, bdaddr, device_name):
        """
        Creates a new spheroAPI instance and adds this to the collection of spheros
        @param bdaddr: The Sphero bt_addr
        @param device_name: The Sphero device name
        """
        if device_name not in self._spheros:
            new_sphero = SpheroAPI(device_name, bdaddr)
            self._spheros[device_name] = new_sphero
            self._notify_sphero_found(new_sphero)

    def remove_sphero(self, sphero):
        """
        Removes the given sphero device from connected and nearby devices and disconnects it.
        @param sphero: The sphero object that should be removed
        """
        with self._sphero_lock:
            self._spheros.pop(sphero.bt_name)
        sphero.disconnect()

    @staticmethod
    def _find_nearby_bt_devices():
        """
        Helper method that finds nearby bluetooth devices
        @return: A list of tuples of nearby device (bt_addr, bt_name)
        @rtype: list
        """
        nearby_devices = []
        try:
            nearby_devices = bluetooth.discover_devices()
        except bluetooth.BluetoothError as e:
            print "Error when searching for nearby devices", e
        return nearby_devices

    def flush_name_cache(self):
        """
        Flush the bt device name cache
        """
        self._name_cache = {}

    def _get_device_name(self, bdaddr):
        """
        Helper method for looking up bt device names. Implements a cache so previously looked up names
        are cached to minimize lookup time.
        @param bdaddr:
        @return:
        """
        if bdaddr in self._name_cache.iterkeys():
            return self._name_cache[bdaddr]

        sleep = 0.1
        for _ in xrange(SpheroManager.BT_NAME_LOOKUP_NUM_RETRIES):
            device_name = bluetooth.lookup_name(bdaddr, timeout=SpheroManager.BT_NAME_LOOKUP_TIMEOUT_SEC)
            if device_name is not None and len(device_name):
                self._name_cache[bdaddr] = device_name
                return device_name
            time.sleep(sleep)
        return None

    @staticmethod
    def _is_sphero(device_name):
        """
        Helper method that checks if the given name matches the one of a sphero.
        @param device_name: The name of the device
        @return: True if device name matches the sphero name pattern
        @rtype: bool
        """
        return device_name is not None and SpheroManager.SPHERO_BASE_NAME in device_name

    def set_sphero_found_cb(self, cb):
        """
        Allows for the uses of the class to set a callback when a new sphero is detected from the search method
        @param cb: the callback method that should be called when a new sphero is detected
        """
        self._sphero_found_cb = cb

    def _notify_sphero_found(self, new_sphero):
        """
        Helper method that triggers the cb set to be triggered when a new Sphero is discovered
        @param new_sphero: The instance of the Sphero found
        @type new_sphero: SpheroAPI
        """
        if self._sphero_found_cb is not None:
            self._sphero_found_cb(new_sphero)


if __name__ == "__main__":
    ## FOR TESTING
    def callback(sphero):
        print "CALLBACK", sphero.bt_name
        sphero.connect()
        print "ALL:", sm.get_all_devices()
        print "CON:", sm.get_connected_spheros()


    sm = SpheroManager()
    sm.set_sphero_found_cb(callback)
    sm.start_auto_search()