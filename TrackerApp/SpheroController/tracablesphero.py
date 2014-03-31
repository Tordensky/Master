import sphero
from tracker import Traceable, FilterGlow
from tracker import ImageGraphics as Ig
from util.vector import Vector2D
from util.color import Color


class SpheroTraceable(Traceable):
    def __init__(self, name="no-name", device=None):
        super(SpheroTraceable, self).__init__(name)
        self.imu_angle = 0.0
        self.filter = FilterGlow()
        self._sphero_sensor_data = {}

        self.device = device

    def do_before_tracked(self, *args, **kwargs):
        super(SpheroTraceable, self).do_before_tracked(*args, **kwargs)
        if self.device:
            pass

    def do_after_tracked(self, *args, **kwargs):
        super(SpheroTraceable, self).do_after_tracked(*args, **kwargs)
        if self.device:
            if abs(self.imu_angle - self.direction_angle) > 50:
                pass  # TODO Update
                print "heading offsett", abs(self.imu_angle - self.direction_angle)

                #if self.direction_angle != 0:
                #    self.device.set_heading(self.direction_angle)
                #self.device.configure_locator(int(self.direction_angle))

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
            self.draw_vector(image, self.pos, velocity_vector, Color((0, 255, 0)))

    def draw_graphics(self, image):
        # TODO DESPERATE REFACTORING!!!
        super(SpheroTraceable, self).draw_graphics(image)

        pos_space = 10
        pos_y = int(pos_space) + 10

        self._draw_sphero_velocity(image)

        try:
            imu_angle = self._sphero_sensor_data[sphero.KEY_STRM_IMU_YAW_ANGLE]
            imu_vector = Vector2D()
            imu_vector.set_angle(imu_angle)
            imu_vector.rotate(90)
            imu_vector = self.set_tail_length(imu_vector, 15)
            self.draw_vector(image, self.pos, imu_vector, Color((0, 0, 255)))
            self.imu_angle = imu_angle
        except KeyError:
            pass
        else:
            if imu_angle < 0:
                imu_angle = 365 - abs(imu_angle)
            Ig.text(image, "imu angle: "+str(imu_angle), self.pos+(15, pos_y), 0.30, Color((255, 255, 255)))

        pos_y += pos_space
        Ig.text(image, "tracked angle: "+str(self.direction_angle), self.pos+(15, pos_y), 0.30, Color((255, 255, 255)))

        pos_y += pos_space
        Ig.text(image, "direction_vector: "+str(self.direction_vector), self.pos+(15, pos_y), 0.30, Color((255, 255, 255)))

    def set_data(self, sensor_data):
        self._sphero_sensor_data = sensor_data