import sphero
from tracker import Traceable, FilterGlow
from tracker import ImageGraphics as Ig
from util.vector import Vector2D
from util.color import Color


class SpheroTraceable(Traceable):
    def __init__(self, name="no-name", device=None, speed_vector=Vector2D(0, 0)):
        super(SpheroTraceable, self).__init__(name)
        self.imu_angle = 0.0
        self.filter = FilterGlow()
        self._sphero_sensor_data = {}

        self.device = device
        device.configure_locator(0, 0, 90, auto=False)

        self.imu_vector = Vector2D(1, 1)

        self.speed_vector = speed_vector

        self.correct_heading = 0.0

    def do_before_tracked(self, *args, **kwargs):
        super(SpheroTraceable, self).do_before_tracked(*args, **kwargs)
        if self.device:
            pass

    def do_after_tracked(self, *args, **kwargs):
        super(SpheroTraceable, self).do_after_tracked(*args, **kwargs)
        if self.device:
            #off_by = self.imu_vector.angle_between(self.direction_vector)
            #if off_by > 20:
            if self.direction_vector.magnitude > 0.0:
                self.correct_heading = (360.0 - self.direction_vector.angle + 90) % 359
                imu_heading_sphero_format = (360.0 - self.imu_vector.angle + 90) % 359
                print self.correct_heading - imu_heading_sphero_format
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

    def _draw_sphero_velocity(self, image):
        try:
            vel_x = self._sphero_sensor_data[sphero.KEY_STRM_VELOCITY_X]
            vel_y = self._sphero_sensor_data[sphero.KEY_STRM_VELOCITY_Y]
        except KeyError:
            print "VELOCITY KEY ERROR"
        else:
            velocity_vector = Vector2D(vel_x, vel_y)
            velocity_vector = self.set_tail_length(velocity_vector, 30)
            velocity_vector.invert()
            Ig.draw_vector(image, self.pos, velocity_vector, Color((0, 255, 0)))

    def draw_graphics(self, image):
        # TODO DESPERATE REFACTORING!!!
        super(SpheroTraceable, self).draw_graphics(image)

        pos_space = 10
        pos_y = int(pos_space) + 10

        self._draw_sphero_velocity(image)

        try:
            self.imu_angle = self._sphero_sensor_data[sphero.KEY_STRM_IMU_YAW_ANGLE]
            # if self.imu_angle < 0:
            #     self.imu_angle = - 360 - (360 - abs(self.imu_angle))

            self.imu_vector.angle = self.imu_angle

            self.imu_vector = self.set_tail_length(self.imu_vector, 15)
            Ig.draw_vector_with_label(image, round(self.imu_vector.angle, 2), self.pos, self.imu_vector, Color((0, 0, 255)))
            #self.imu_angle = imu_angle
        except KeyError:
            pass
        else:

            Ig.text(image, "imu angle: "+str(self.imu_angle), (15, pos_y), 0.30, Color((255, 255, 255)))

            # pos_y += pos_space
            # Ig.text(image, "imu angle raw: "+str(imu_angle), (15, pos_y), 0.30, Color((255, 255, 255)))

        pos_y += pos_space

        angles = ("traced: {}, imu: {}, off: {}").format(self.direction_vector.angle, self.imu_vector.angle, self.imu_vector.angle_between(self.direction_vector))

        Ig.text(image, angles, (15, pos_y), 0.30, Color((255, 255, 255)))

        # pos_y += pos_space
        # Ig.text(image, "direction_vector: "+str(self.direction_vector), (15, pos_y), 0.30, Color((255, 255, 255)))

        pos_y += pos_space
        Ig.text(image, "pos: "+str(self.pos), (15, pos_y), 0.30, Color((255, 255, 255)))

        #Ig.draw_tracked_path(image, self.valid_samples(), 10) # TODO ADDS ALOT OF LATENCY


        Ig.draw_vector_with_label(image, round(self.speed_vector.angle, 2), self.pos, self.set_tail_length(self.speed_vector, 40), Color((0, 255, 255)))

        Ig.draw_vector(image, (60, 60), self.set_tail_length(self.speed_vector, 20), Color((255, 0, 255)))

        #print self.speed

    def set_data(self, sensor_data):
        self._sphero_sensor_data = sensor_data