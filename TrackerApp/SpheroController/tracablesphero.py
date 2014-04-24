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
    def __init__(self, device, name="no-name", speed_vector=Vector2D(0, 0)):
        """

        @param name:
        @param device:
        @type device: sphero.SpheroAPI
        @param speed_vector:
        """
        super(TraceableSphero, self).__init__(name)
        self.filter = FilterGlow()

        self.device = device
    #    self._sphero_sensor_data = {}

        #device.set_heading(0)
        print "CONFIGURE LOCATOR: ", device.configure_locator(0, 0, 0, auto=True).success

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

    def draw_velocity_vector(self, image, pos):
        if self.device.sensors:
            try:
                vel_x = self.device.sensors.velocity.velocity.x  # self._sphero_sensor_data[sphero.KEY_STRM_VELOCITY_X]
                vel_y = self.device.sensors.velocity.velocity.y
            except KeyError:
                pass
            else:
                self.velocity_vector.set_values(vel_x, vel_y)
                self.velocity_vector.rotate(90)
                #self.velocity_vector.invert()
                if self.velocity_vector.magnitude:
                    # self.velocity_vector *= 5  #.set_length(30)  # = self.set_tail_length(self.velocity_vector, 30)
                    max_len = 20
                    if self.velocity_vector.magnitude > max_len:
                        self.velocity_vector.set_length(max_len)
                try:
                    Ig.draw_vector(image, pos, self.velocity_vector, Color((0, 255, 0)))
                except DrawError:
                    pass

    def draw_imu_vector(self, image, pos):
        if self.device.sensors:
            imu_yaw = self.device.sensors.imu.angle.yaw
            if imu_yaw:
                self.imu_vector.angle = imu_yaw

            self.imu_vector.set_length(15)  # = self.set_tail_length(self.imu_vector, 15)
            try:
                Ig.draw_vector_with_label(image, str(round(self.imu_vector.angle, 2)), pos, self.imu_vector,
                                          Color((0, 0, 255)))
            except DrawError as d:
                pass

    def get_new_heading(self):
        off_by_avg = self.device_offset.avg

        return off_by_avg

    def draw_graphics(self, image):
        # TODO DESPERATE REFACTORING!!!
        super(TraceableSphero, self).draw_graphics(image)

        pos_space = 10
        pos_y = int(pos_space) + 10

        self.draw_imu_vector(image, self.pos)
        self.draw_velocity_vector(image, self.pos)

        Ig.draw_circle(image, (50, 50), 5, Color((255, 50, 5)))
        self.draw_imu_vector(image, (50, 50))
        #self.draw_velocity_vector(image, (50, 50))
        self.draw_direction_vector(image, (50, 50))


        if self.device.sensors:
            txt = "rotation:{}".format(self.device.sensors.gyro.gyro_dps.z)
            Ig.draw_text(image, txt, (100, 100), 0.5, Color((255, 0, 0)))

        if self.direction.magnitude:
            off_by = self.velocity_vector.get_offset(self.direction)
            self.device_offset.add_sample(off_by)
            off_by_avg = self.device_offset.avg
            # print off_by, off_by_avg, self.get_new_heading()

        Ig.draw_tracked_path(image, self.get_valid_samples(), 10) # TODO ADDS ALOT OF LATENCY
        if self.device.sensors:
            turn_rate = self.device.sensors.gyro.gyro_dps.z
            if turn_rate:
                Ig.draw_tracked_path_pos(image, self.get_calculated_path(turn_rate), 10) # TODO ADDS ALOT OF LATENCY

        # Ig.draw_vector_with_label(image, round(self.control_vector.angle, 2), self.pos, self.set_tail_length(self.control_vector, 40), Color((0, 255, 255)))

        #Ig.draw_vector(image, (60, 60), self.control_vector.set_length(20), Color((255, 0, 255)))
