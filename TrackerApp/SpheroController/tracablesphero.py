import sphero
from tracker import TraceableObject, FilterGlow
from tracker import ImageGraphics as Ig
from tracker.graphics import DrawError
from util.vector import Vector2D
from util.color import Color


class AvgValueSampleHolder(object):
    def __init__(self):
        super(AvgValueSampleHolder, self).__init__()
        self.sum_samples = 0.0
        self.num_samples = 0

    def add_sample(self, value):
        self.sum_samples += value
        self.num_samples += 1

    def reset(self):
        self.num_samples = 0.0
        self.sum_samples = 0

    @property
    def avg(self):
        return self.sum_samples / self.num_samples


class TraceableSphero(TraceableObject):
    def __init__(self, name="no-name", device=None, speed_vector=Vector2D(0, 0)):
        super(TraceableSphero, self).__init__(name)
        self.filter = FilterGlow()

        self.device = device
        self._sphero_sensor_data = {}

        device.set_heading(0)
        device.configure_locator(0, 0, 0, auto=False)

        self.imu_vector = Vector2D(1.0, 1.0)
        self.control_vector = speed_vector
        self.velocity_vector = Vector2D(0, 0)

        self.device_offset = AvgValueSampleHolder()

    def do_before_tracked(self, *args, **kwargs):
        super(TraceableSphero, self).do_before_tracked(*args, **kwargs)
        if self.device:
            pass

    def do_after_tracked(self, *args, **kwargs):
        super(TraceableSphero, self).do_after_tracked(*args, **kwargs)

        # if self.device:
        #     #
        #     #if off_by > 20:
        #     if self.direction_vector.magnitude > 0.0:
        #         self.correct_heading = (360.0 - self.direction_vector.angle + 90) % 359
        #        imu_heading_sphero_format = (360.0 - self.imu_vector.angle + 90) % 359
        #print self.correct_heading - imu_heading_sphero_format
        #print "offsett overload", off_by, self.correct_heading, imu_heading_sphero_format
        #self.device.set_heading(correct_heading)
        #
        # if self.imu_vector.angle > self.direction_vector.angle:
        #     self.device.set_heading(imu_heading_sphero_format- 1)
        # else:
        #     self.device.set_heading(imu_heading_sphero_format + 1)

        #
        #
        # self.device.configure_locator(0, 0, off_by)
        # #self.device.set_heading(self.direction_vector.angle)

    def draw_sphero_velocity(self, image):
        try:
            vel_x = self._sphero_sensor_data[sphero.KEY_STRM_VELOCITY_X]
            vel_y = self._sphero_sensor_data[sphero.KEY_STRM_VELOCITY_Y]
        except KeyError:
            pass
        else:
            self.velocity_vector.set_values(vel_x, vel_y)
            self.velocity_vector.rotate(90)
            self.velocity_vector.invert()
            self.velocity_vector.set_length(30)  # = self.set_tail_length(self.velocity_vector, 30)
            Ig.draw_vector(image, self.pos, self.velocity_vector, Color((0, 255, 0)))

    def draw_imu_vector(self, image):
        try:
            self.imu_vector.angle = self._sphero_sensor_data[sphero.KEY_STRM_IMU_YAW_ANGLE]

            self.imu_vector.set_length(15)  # = self.set_tail_length(self.imu_vector, 15)
            try:
                Ig.draw_vector_with_label(image, str(round(self.imu_vector.angle, 2)), self.pos, self.imu_vector,
                                          Color((0, 0, 255)))
            except DrawError:
                print "exception in draw imu vector"
        except KeyError:
            pass

    def get_new_heading(self):
        off_by_avg = self.device_offset.avg

        return off_by_avg

    def draw_graphics(self, image):
        # TODO DESPERATE REFACTORING!!!
        super(TraceableSphero, self).draw_graphics(image)

        pos_space = 10
        pos_y = int(pos_space) + 10

        #self.draw_sphero_velocity(image)
        self.draw_imu_vector(image)

        if self.direction_vector.magnitude:
            off_by = self.imu_vector.get_offset(self.direction_vector)
            self.device_offset.add_sample(off_by)
            off_by_avg = self.device_offset.avg
            # print off_by, off_by_avg, self.get_new_heading()

        # Ig.draw_tracked_path(image, self.valid_samples(), 10) # TODO ADDS ALOT OF LATENCY

        # Ig.draw_vector_with_label(image, round(self.control_vector.angle, 2), self.pos, self.set_tail_length(self.control_vector, 40), Color((0, 255, 255)))

        Ig.draw_vector(image, (60, 60), self.control_vector.set_length(20), Color((255, 0, 255)))

    def set_data(self, sensor_data):
        self._sphero_sensor_data = sensor_data


if __name__ == "__main__":
    def get_offset(a, b, n_digits=4):
        """
        Gets the offset in fully 360 degrees between two vectors
        @param a: Vector A
         @type a: Vector2D
        @param b: Vector B
         @type b: Vector2D
        """
        angle = round(a.angle - b.angle, n_digits) % 360
        return angle

    vector_of_by = 90.0

    traced = Vector2D(1, 0)
    imu = Vector2D(1, 0)
    traced.angle = 250.0
    imu.angle = 260.0

    for x in range(0, 360):
        traced.angle += 1
        imu.angle += 1

        offset = get_offset(imu, traced)
        # print "imu:", imu.angle, "traced", traced.angle, "offset:", offset

