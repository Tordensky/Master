from sphero.core import SpheroAPI


class AsyncSphero(object):
    def __init__(self, bdname=None, bdaddr=None):
        self.bdname = bdname
        self.bdaddr = bdaddr

        self._spheroAPI = SpheroAPI(bdname, bdaddr)

    def connect(self, on_success, on_failure):
        pass