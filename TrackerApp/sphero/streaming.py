from sphero import response
import core


class MaskUtil(object):
    ZERO_MASK = 0x00000000
    ALL_MASK = 0xFFFFFFFF

    @staticmethod
    def add_field(mask, bitfield):
        return mask | bitfield

    @staticmethod
    def rem_field(mask, bitfield):
        return mask - bitfield

    @staticmethod
    def empty_mask():
        return MaskUtil.ZERO_MASK

    @staticmethod
    def set_all():
        return MaskUtil.ALL_MASK

    @staticmethod
    def set_value_active(mask, activate, bit_field):
        if activate:
            mask = MaskUtil.add_field(mask, bit_field)
        else:
            mask = MaskUtil.rem_field(mask, bit_field)
        return mask

    @staticmethod
    def is_set(mask, base_mask):
        return bool(base_mask & mask)

    @staticmethod
    def value_state_list(mask):
        iter_mask = 0x80000000
        state_list = []
        for _ in xrange(iter_mask.bit_length()):
            state_list.append((iter_mask, MaskUtil.is_set(iter_mask, mask)))
            iter_mask >>= 1
        return state_list

    @staticmethod
    def add_names(value_state_list, value_names):
        named_state_list = []
        for value_id, value in value_state_list:
            try:
                named_state_list.append((value_names[value_id], value))
            except KeyError:
                pass
        return named_state_list

    @staticmethod
    def print_mask(mask, value_names):
        named_state = MaskUtil.add_names(MaskUtil.value_state_list(mask), value_names)
        for name, state in named_state:
            print "{} set: {}".format(name, state)


class Mask1(object):
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

    mask1_names = {
        ACC_X_RAW: "ACC_X_RAW",
        ACC_Y_RAW: "ACC_Y_RAW",
        ACC_Z_RAW: "ACC_Z_RAW",

        GYRO_X_RAW: "GYRO_X_RAW",
        GYRO_Y_RAW: "GYRO_Y_RAW",
        GYRO_Z_RAW: "GYRO_Z_RAW",

        EMF_RAW_RIGHT_MOTOR: "EMF_RAW_RIGHT_MOTOR",
        EMF_RAW_LEFT_MOTOR: "EMF_RAW_LEFT_MOTOR",

        PWM_RAW_LEFT_MOTOR: "PWM_RAW_LEFT_MOTOR",
        PWM_RAW_RIGHT_MOTOR: "PWM_RAW_RIGHT_MOTOR",

        IMU_PITCH_ANGLE: "IMU_PITCH_ANGLE",
        IMU_ROLL_ANGLE: "IMU_ROLL_ANGLE",
        IMU_YAW_ANGLE: "IMU_YAW_ANGLE",

        ACC_X: "ACC_X",
        ACC_Y: "ACC_Y",
        ACC_Z: "ACC_Z",

        GYRO_X: "GYRO_X",
        GYRO_Y: "GYRO_Y",
        GYRO_Z: "GYRO_Z",
    }

    def __init__(self):
        super(Mask1, self).__init__()
        self.mask1 = MaskUtil.empty_mask()

    def stream_acc_raw(self, activate=True):
        acc_raw_mask = Mask1.ACC_X_RAW | Mask1.ACC_Y_RAW | Mask1.ACC_Z_RAW
        self.mask1 = MaskUtil.set_value_active(self.mask1, activate, acc_raw_mask)

    def stream_acc(self, activate=True):
        acc_mask = Mask1.ACC_X | Mask1.ACC_Y | Mask1.ACC_Z
        self.mask1 = MaskUtil.set_value_active(self.mask1, activate, acc_mask)

    def stream_gyro_raw(self, activate=True):
        gyro_raw_mask = Mask1.GYRO_X_RAW | Mask1.GYRO_Y_RAW | Mask1.GYRO_Z_RAW
        self.mask1 = MaskUtil.set_value_active(self.mask1, activate, gyro_raw_mask)

    def stream_gyro(self, activate=True):
        gyro_mask = Mask1.GYRO_X | Mask1.GYRO_Y | Mask1.GYRO_Z
        self.mask1 = MaskUtil.set_value_active(self.mask1, activate, gyro_mask)

    def stream_motor_data_raw(self, activate=True):
        motor_raw_mask = Mask1.EMF_RAW_LEFT_MOTOR | Mask1.EMF_RAW_RIGHT_MOTOR | Mask1.PWM_RAW_LEFT_MOTOR | \
                         Mask1.PWM_RAW_RIGHT_MOTOR
        self.mask1 = MaskUtil.set_value_active(self.mask1, activate, motor_raw_mask)

    def stream_motor_data(self, activate=True):
        motor_mask = Mask1.EMF_LEFT_MOTOR | Mask1.EMF_RIGHT_MOTOR
        self.mask1 = MaskUtil.set_value_active(self.mask1, activate, motor_mask)

    def stream_imu_angle(self, activate=True):
        imu_mask = Mask1.IMU_PITCH_ANGLE | Mask1.IMU_ROLL_ANGLE | Mask1.IMU_YAW_ANGLE
        self.mask1 = MaskUtil.set_value_active(self.mask1, activate, imu_mask)

    def stream_all(self):
        self.stream_acc_raw()
        self.stream_acc()
        self.stream_gyro_raw()
        self.stream_gyro()
        self.stream_motor_data_raw()
        self.stream_motor_data()
        self.stream_imu_angle()

    def stream_none(self):
        self.mask1 = MaskUtil.empty_mask()

    def get_values(self):
        state_lst = MaskUtil.value_state_list(self.mask1)
        return MaskUtil.add_names(state_lst, self.mask1_names)

    def print_mask(self):
        MaskUtil.print_mask(self.mask1, self.mask1_names)


class Mask2(object):
    Q0 = 0x80000000
    Q1 = 0x40000000
    Q2 = 0x20000000
    Q3 = 0x10000000

    ODOMETER_X = 0x08000000
    ODOMETER_Y = 0x04000000

    ACCEL_ONE = 0x02000000

    VELOCITY_X = 0x01000000
    VELOCITY_Y = 0x00800000

    mask2_names = {
        Q0: "Q0",
        Q1: "Q1",
        Q2: "Q2",
        Q3: "Q3",

        ODOMETER_X: "ODOMETER_X",
        ODOMETER_Y: "ODOMETER_Y",

        ACCEL_ONE: "ACCEL_ONE",

        VELOCITY_X: "VELOCITY_X",
        VELOCITY_Y: "VELOCITY_Y"
    }

    def __init__(self):
        super(Mask2, self).__init__()
        self.mask2 = MaskUtil.empty_mask()

    def stream_odometer(self, activate=True):
        odometer = Mask2.ODOMETER_X | Mask2.ODOMETER_Y
        self.mask2 = MaskUtil.set_value_active(self.mask2, activate, odometer)

    def stream_velocity(self, activate=True):
        velocity = Mask2.VELOCITY_X | Mask2.VELOCITY_Y
        self.mask2 = MaskUtil.set_value_active(self.mask2, activate, velocity)

    def stream_acceleration_one(self, activate=True):
        self.mask2 = MaskUtil.set_value_active(self.mask2, activate, Mask2.ACCEL_ONE)

    def stream_quaternion(self, activate=True):
        quaternion = Mask2.Q0 | Mask2.Q1 | Mask2.Q2 | Mask2.Q3
        self.mask2 = MaskUtil.set_value_active(self.mask2, activate, quaternion)

    def stream_all(self):
        self.stream_odometer()
        self.stream_velocity()
        self.stream_acceleration_one()
        self.stream_quaternion()

    def stream_none(self):
        self.mask2 = MaskUtil.empty_mask()

    def get_values(self):
        state_lst = MaskUtil.value_state_list(self.mask2)
        return MaskUtil.add_names(state_lst, self.mask2_names)

    def print_mask(self):
        MaskUtil.print_mask(self.mask2, self.mask2_names)


class SensorStreamingConfig(Mask1, Mask2):
    STREAM_FOREVER = 0
    MAX_SAMPLE_RATE_SPHERO = 400

    def __init__(self):
        super(SensorStreamingConfig, self).__init__()
        self.n = 400
        self.m = 1
        self.num_packets = 0

    @property
    def sample_rate(self):
        return ssc.MAX_SAMPLE_RATE_SPHERO / self.n

    @sample_rate.setter
    def sample_rate(self, packets_sec):
        try:
            if packets_sec <= 0:
                raise core.SpheroError("Sample rate must be a number larger than 0")
            self.n = int(self.MAX_SAMPLE_RATE_SPHERO / packets_sec)
        except ZeroDivisionError:
            self.n = self.STREAM_FOREVER

    def stream_all(self):
        Mask1.stream_all(self)
        Mask2.stream_all(self)

    def stream_none(self):
        Mask1.stream_none(self)
        Mask2.stream_none(self)

    print_mask1 = Mask1.print_mask
    print_mask2 = Mask2.print_mask

    def print_streaming_config(self):
        print "MASK 1"
        Mask1.print_mask(self)
        print "MASK 2"
        Mask2.print_mask(self)

    def get_streaming_config(self):
        return Mask1.get_values(self) + Mask2.get_values(self)


class SensorStreamingResponse(response.AsyncMsg):
    def __init__(self, header, data, ss_config):
        super(SensorStreamingResponse, self).__init__(header, data)
        self.sensor_data = {}
        self.ssc = ss_config
        self.sensor_data = self._parse_sensor_data(ss_config)

    def _parse_sensor_data(self, ss_conf):
        sensor_data = {}

        streaming_config = ss_conf.get_streaming_config()

        data_offset = 0
        for sensor_name, is_activated in streaming_config:
            if is_activated:
                sensor_data[sensor_name] = self.body[data_offset]
                data_offset += 1
        return sensor_data

    @property
    def fmt(self):
        return '!%dhb' % ((self.dlen - 1) / 2)


if __name__ == "__main__":
    ssc = SensorStreamingConfig()
    ssc.sample_rate = 0.1
    print ssc.n, ssc.sample_rate
    ssc.sample_rate = 1
    print ssc.n, ssc.sample_rate
    print ssc.n, ssc.sample_rate




