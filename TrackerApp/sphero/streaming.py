import copy
from sphero import response


class MaskUtil(object):
    ZERO_MASK = 0x00000000
    ALL_MASK = 0xFFFFFFFF

    @staticmethod
    def add_field(mask, bitfield):
        return mask | bitfield

    @staticmethod
    def rem_field(mask, bitfield):
        return mask ^ bitfield

    @staticmethod
    def get_empty_mask():
        return MaskUtil.ZERO_MASK

    @staticmethod
    def set_all():
        return MaskUtil.ALL_MASK

    @staticmethod
    def set_if_true(mask, activate, bit_field):
        if activate:
            mask = MaskUtil.add_field(mask, bit_field)
        else:
            mask = MaskUtil.rem_field(mask, bit_field)
        return mask

    @staticmethod
    def set_list(mask):
        iter_mask = 0x80000000
        state_list = []
        for _ in xrange(32):
            state_list.append((iter_mask, bool(mask & iter_mask)))
            iter_mask >>= 1
        return state_list

    @staticmethod
    def print_mask(mask):
        for value, state in MaskUtil.set_list(mask):
            print "%08x %s" % (value, state)


class Mask1(MaskUtil):
    ACC_X_RAW = 0x80000000
    ACC_Y_RAW = 0x40000000
    ACC_Z_RAW = 0x20000000

    GYRO_X_RAW = 0x10000000
    GYRO_Y_RAW = 0x08000000
    GYRO_Z_RAW = 0x04000000

    EMF_RAW_RIGHT_MOTOR = 0x00400000
    EMF_RAW_LEFT_MOTOR = 0x00200000

    PWM_RAW_LEFT_MOTOR = 0x00100000
    PWM_RAW_RIGHT_MOTOR = 0x00080000

    IMU_PITCH_ANGLE = 0x00040000
    IMU_ROLL_ANGLE = 0x00020000
    IMU_YAW_ANGLE = 0x00010000

    ACC_X = 0x00008000
    ACC_Y = 0x00004000
    ACC_Z = 0x00002000

    GYRO_X = 0x00001000
    GYRO_Y = 0x00000800
    GYRO_Z = 0x00000400

    EMF_RIGHT_MOTOR = 0x00000040
    EMF_LEFT_MOTOR = 0x00000020

    def __init__(self):
        super(Mask1, self).__init__()
        self.mask1 = self.get_empty_mask()

    def stream_acc_raw(self, activate=True):
        acc_raw_mask = Mask1.ACC_X_RAW | Mask1.ACC_Y_RAW | Mask1.ACC_Z_RAW
        self.mask1 = self.set_if_true(self.mask1, activate, acc_raw_mask)

    def stream_acc(self, activate=True):
        acc_mask = Mask1.ACC_X | Mask1.ACC_Y | Mask1.ACC_Z
        self.mask1 = self.set_if_true(self.mask1, activate, acc_mask)

    def stream_gyro_raw(self, activate=True):
        gyro_raw_mask = Mask1.GYRO_X_RAW | Mask1.GYRO_Y_RAW | Mask1.GYRO_Z_RAW
        self.mask1 = self.set_if_true(self.mask1, activate, gyro_raw_mask)

    def stream_gyro(self, activate=True):
        gyro_mask = Mask1.GYRO_X | Mask1.GYRO_Y | Mask1.GYRO_Z
        self.mask1 = self.set_if_true(self.mask1, activate, gyro_mask)

    def stream_motor_data_raw(self, activate=True):
        motor_raw_mask = Mask1.EMF_RAW_LEFT_MOTOR | Mask1.EMF_RAW_RIGHT_MOTOR | Mask1.PWM_RAW_LEFT_MOTOR | \
                         Mask1.PWM_RAW_RIGHT_MOTOR
        self.mask1 = self.set_if_true(self.mask1, activate, motor_raw_mask)

    def stream_motor_data(self, activate=True):
        motor_mask = Mask1.EMF_LEFT_MOTOR | Mask1.EMF_RIGHT_MOTOR
        self.mask1 = self.set_if_true(self.mask1, activate, motor_mask)

    def stream_imu_angle(self, activate=True):
        imu_mask = Mask1.IMU_PITCH_ANGLE | Mask1.IMU_ROLL_ANGLE | Mask1.IMU_YAW_ANGLE
        self.mask1 = self.set_if_true(self.mask1, activate, imu_mask)

    def stream_all(self):
        self.stream_acc_raw()
        self.stream_acc()
        self.stream_gyro_raw()
        self.stream_gyro()
        self.stream_motor_data_raw()
        self.stream_motor_data()
        self.stream_imu_angle()

    def stream_none(self):
        self.stream_acc_raw(False)
        self.stream_acc(False)
        self.stream_gyro_raw(False)
        self.stream_gyro(False)
        self.stream_motor_data_raw(False)
        self.stream_motor_data(False)
        self.stream_imu_angle(False)

    def get_set_fields(self):
        return self.set_list(self.mask1)

    def print_mask1(self):
        self.print_mask(self.mask1)


class Mask2(MaskUtil):
    Q0 = 0x80000000
    Q1 = 0x40000000
    Q2 = 0x20000000
    Q3 = 0x10000000

    ODOMETER_X = 0x08000000
    ODOMETER_Y = 0x04000000

    ACCEL_ONE = 0x02000000

    VELOCITY_X = 0x01000000
    VELOCITY_Y = 0x00800000

    def __init__(self):
        super(Mask2, self).__init__()
        self.mask2 = 0x00000000

    def stream_odometer(self, activate=True):
        odometer = Mask2.ODOMETER_X | Mask2.ODOMETER_Y
        self.mask2 = self.set_if_true(self.mask2, activate, odometer)

    def stream_velocity(self, activate=True):
        velocity = Mask2.VELOCITY_X | Mask2.VELOCITY_Y
        self.mask2 = self.set_if_true(self.mask2, activate, velocity)

    def stream_acceleration_one(self, activate=True):
        self.mask2 = self.set_if_true(self.mask2, activate, Mask2.ACCEL_ONE)

    def stream_quaternion(self, activate=True):
        quaternion = Mask2.Q0 | Mask2.Q1 | Mask2.Q2 | Mask2.Q3
        self.mask2 = self.set_if_true(self.mask2, activate, quaternion)

    def stream_all(self):
        self.stream_odometer()
        self.stream_velocity()
        self.stream_acceleration_one()
        self.stream_quaternion()

    def stream_none(self):
        self.stream_odometer(False)
        self.stream_velocity(False)
        self.stream_acceleration_one(False)
        self.stream_quaternion(False)

    def get_set_fields(self):
        return self.set_list(self.mask2)

    def print_mask2(self):
        self.print_mask(self.mask2)


class SensorStreamingConfig(Mask1, Mask2):
    STREAM_FOREVER = 0
    def __init__(self):
        super(SensorStreamingConfig, self).__init__()
        self.n = 20
        self.m = 1
        self.pcnt = 1

    def stream_all(self):
        Mask1.stream_all(self)
        Mask2.stream_all(self)

    def stream_none(self):
        Mask1.stream_none(self)
        Mask2.stream_none(self)

    def print_masks(self):
        print "MASK 1"
        Mask1.print_mask1(self)
        print "MASK 2"
        Mask2.print_mask2(self)

    def get_set_mask1(self):
        return Mask1.get_set_fields(self)

    def get_set_mask2(self):
        return Mask2.get_set_fields(self)


class SensorStreamingResponse(response.AsyncMsg):
    def __init__(self, header, data, current_ssc):
        super(SensorStreamingResponse, self).__init__(header, data)
        self.sensor_data = {}
        self.ssc = current_ssc
        self._parse_data()
        print self.sensor_data

    def _parse_data(self):
        self.sensor_data = {}
        data_iter = 0
        for value, is_set in self.ssc.get_set_mask1():
            if is_set:
                self.sensor_data["1:%0.8x" % value] = self.body[data_iter]
                data_iter += 1

        for value, is_set in self.ssc.get_set_mask2():
            if is_set:
                self.sensor_data["1:%0.8x" % value] = self.body[data_iter]
                data_iter += 1

    @property
    def fmt(self):
        return '!%dhb' % ((self.dlen - 1) / 2)


if __name__ == "__main__":
    ssc = SensorStreamingConfig()
    ssc.stream_all()
    ssc.print_masks()
    ssc.stream_none()
    ssc.print_masks()
    ssc.stream_gyro()
    ssc.stream_odometer()
    ssc.print_masks()

    print ssc.mask1
    print ssc.mask2

