# coding: utf-8
import struct


class Response(object):
    SOP1 = 0
    SOP2 = 1
    MRSP = 2
    SEQ = 3
    DLEN = 4

    CODE_OK = 0

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
        return self.header[self.MRSP] == self.CODE_OK

    def seq(self):
        return self.header[self.SEQ]

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
         return '!hhhhHb'

