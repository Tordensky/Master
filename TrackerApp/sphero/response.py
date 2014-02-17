# coding: utf-8
import struct


class ResponseCode(object):
    CODE_OK = 0x00
    CODE_EGEN = 0x01
    CODE_ECHKSUM = 0x02
    CODE_EFRAG = 0x03
    CODE_EBAD_CMD = 0x04
    CODE_EUNSUPP = 0x05
    CODE_EBAD_MSG = 0x06
    CODE_EPARAM = 0x07
    CODE_EEXEC = 0x08
    CODE_EBAB_DID = 0x09
    CODE_MEM_BUSY = 0x0A
    CODE_BAD_PASSWORD = 0x0B
    CODE_POWER_NOGOOD = 0x31
    CODE_PAGE_ILLEGAL = 0x32
    CODE_FLASH_FAIL = 0x33
    CODE_MA_CORRUPT = 0x34
    CODE_MSG_TIMEOUT = 0x35

    _msg = {
        CODE_OK: "Command succeeded",
        CODE_EGEN: "General, non-specific error",
        CODE_ECHKSUM: "Received checksum failure",
        CODE_EFRAG: "Received command fragment",
        CODE_EBAD_CMD: "Unknown command ID",
        CODE_EUNSUPP: "Command currently unsupported",
        CODE_EBAD_MSG: "Bad message format",
        CODE_EPARAM: "Parameter value(s) invalid",
        CODE_EEXEC: "Failed to execute command",
        CODE_EBAB_DID: "Unknown device ID",
        CODE_MEM_BUSY: "Generic RAM access needed but it is busy",
        CODE_BAD_PASSWORD: "Supplied password incorrect",
        CODE_POWER_NOGOOD: "Voltage to low for re-flash operation",
        CODE_PAGE_ILLEGAL: "Illegal page number provided",
        CODE_FLASH_FAIL: "Page did not reprogram correctly",
        CODE_MA_CORRUPT: "Main application corrupt",
        CODE_MSG_TIMEOUT: "Msg state machine timed out"
    }

    @staticmethod
    def get_msg(response_code):
        """
        Returns the error message from the given error code.
        @param response_code:
        @type response_code: int
        @rtype: str
        @return: Error message string

        """
        msg = ResponseCode._msg[response_code] if response_code in ResponseCode._msg else "unknown response code"
        return msg


class Response(object):
    SOP1 = 0
    SOP2 = 1
    MRSP = 2
    SEQ = 3
    DLEN = 4

    def __init__(self, header, data):
        self.header = header
        self.data = data

    @property
    def fmt(self):
        return '%sB' % len(self.data)

    def empty(self):
        return self.header[self.DLEN] == 1

    @property
    def success(self):
        return self.header[self.MRSP] == ResponseCode.CODE_OK

    @property
    def seq(self):
        return self.header[self.SEQ]

    @property
    def msg(self):
        return ResponseCode.get_msg(self.header[self.MRSP])

    @property
    def body(self):
        return struct.unpack(self.fmt, self.data)


class GetRGB(Response):
    def __init__(self, header, data):
        super(GetRGB, self).__init__(header, data)
        self.r = self.body[0]
        self.g = self.body[1]
        self.b = self.body[2]


class GetBluetoothInfo(Response):
    def __init__(self, header, body):
        super(GetBluetoothInfo, self).__init__(header, body)
        self.name = self.data.split('\x00', 1)[0]
        self.bta = self.data[16:].split('\x00', 1)[0]


class ReadLocator(Response):
    def __init__(self, header, data):
        super(ReadLocator, self).__init__(header, data)
        self.x_pos = self.body[0]
        self.y_pos = self.body[1]
        self.x_vel = self.body[2]
        self.y_vel = self.body[3]
        self.sog = self.body[4]

    def __str__(self):
        return " xpos: %d \n ypos: %d \n xvel: %d cm/sec\n yvel: %d cm/sec\n sog: %d cm/sec\n" % (
            self.x_pos,
            self.y_pos,
            self.x_vel,
            self.y_vel,
            self.sog
        )

    @property
    def fmt(self):
        return '!4hHb'


class GetPowerState(Response):
    def __init__(self, header, data):
        super(GetPowerState, self).__init__(header, data)
        self.rec_ver = self.body[0]
        self._power_state = self.body[1]
        self.bat_voltage = self.body[2] / 100.0
        self.num_charges = self.body[3]
        self.time_since_last_charge = self.body[4]

    @property
    def power_state(self):
        if self._power_state == 1:
            return "Battery charging"
        elif self._power_state == 2:
            return "Battery OK"
        elif self._power_state == 3:
            return "Battery low"
        elif self._power_state == 4:
            return "Battery critical"
        else:
            return "Unknown battery state"

    @power_state.setter
    def power_state(self, value):
        self.power_state = value

    def __str__(self):
        return " RecVer: v.{} \n PowerState: {} \n Voltage: {} \n NumCharges {} \n Last charge: {} sec\n".format(
            self.rec_ver,
            self.power_state,
            self.bat_voltage,
            self.num_charges,
            self.time_since_last_charge
        )

    @property
    def fmt(self):
        return '!2B3Hb'


class GetOptionFlags(Response):
    def __init__(self, header, data):
        super(GetOptionFlags, self).__init__(header, data)
        print bin(self.body[0])
        flags = self.body[0]
        self.stay_on = bool(flags & 0x0001)
        self.vector_drive = bool(flags & 0x0002)
        self.leveling = bool(flags & 0x0004)
        self.tail_LED = bool(flags & 0x0008)
        self.motion_timeout = bool(flags & 0x0010)
        self.demo_mode = bool(flags & 0x0020)
        self.tap_light = bool(flags & 0x0040)
        self.tap_heavy = bool(flags & 0x0080)
        self.gyro_max = bool(flags & 0x0100)

    def __str__(self):
        return " Stay ON: {} \n Vector Drive: {} \n Leveling: {} \n Tail LED: {} \n " \
            "Motion Timeout: {} \n DemoMode: {} \n Tap light: {} \n tap heavy: {} \n gyro max: {} \n".format(
            self.stay_on,
            self.vector_drive,
            self.leveling,
            self.tail_LED,
            self.motion_timeout,
            self.demo_mode,
            self.tap_light,
            self.tap_heavy,
            self.gyro_max
        )

    @property
    def fmt(self):
        return '!Ib'