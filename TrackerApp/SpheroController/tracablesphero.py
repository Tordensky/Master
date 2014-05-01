import time
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
    def __init__(self, device, name="no-name"):
        """

        @param name:
        @param device:
        @type device: sphero.SpheroAPI
        """
        super(TraceableSphero, self).__init__(name)

        # FILTER USED FOR TRACKING
        self.filter = FilterGlow()

        # THE OBJECT FOR THE DEVICE
        self.device = device

        device.configure_locator(0, 0, 0, auto=False)
        self.device.set_sensor_streaming_cb(self.on_sphero_data)

        # DRAW TRACKED PATCH ATTRIBUTES
        self.draw_tracked = True
        self.draw_n_max_tracked_samples = 5

        # VELOCITY ATTRIBUTES
        self.draw_velocity = True
        self.velocity_vector = Vector2D(0, 0)
        self.velocity_color = Color((0, 255, 0))
        self.max_velocity_len = 20

        # IMU ATTRIBUTES
        self.draw_imu = True
        self.imu_vector = Vector2D(1.0, 1.0)
        self.imu_yaw = None
        self.imu_vector_len = 15
        self.imu_color = Color((0, 0, 255))

    def on_sphero_data(self, data):
        """
        Callback when streaming data is received from device
        @param data:
        @type data: sphero.SensorStreamingResponse
        """
        self._update_imu_vector(data)
        self._update_velocity_vector(data)

    def _update_imu_vector(self, data):
        self.imu_yaw = data.imu.angle.yaw
        if self.imu_yaw:
            self.imu_vector.angle = self.imu_yaw
            self.imu_vector.rotate(90)
        self.imu_vector.set_length(self.imu_vector_len)

    def draw_imu_vector(self, image, pos):
        try:
            label = "IMU: {}".format(round(self.imu_yaw, 2))
            Ig.draw_vector_with_label(image, label, pos, self.imu_vector, self.imu_color)
        except (DrawError, TypeError):
            pass

    def _update_velocity_vector(self, data):
        try:
            vel_x = data.velocity.velocity.x
            vel_y = data.velocity.velocity.y
        except AttributeError:
            pass
        else:
            self.velocity_vector.set_values(vel_x, vel_y)
            if self.velocity_vector:
                if self.velocity_vector.magnitude > self.max_velocity_len:
                    self.velocity_vector.set_length(self.max_velocity_len)

    def draw_velocity_vector(self, image, pos):
        try:
            Ig.draw_vector(image, pos, self.velocity_vector, self.velocity_color)
        except DrawError:
            pass

    def draw_tracked_path(self, image):
        Ig.draw_tracked_path(image, self.get_valid_samples(), self.draw_n_max_tracked_samples)

    def draw_graphics(self, image):
        super(TraceableSphero, self).draw_graphics(image)

        # Draw the direction of the IMU on the device
        self.draw_imu_vector(image, self.pos) if self.draw_imu else None

        # Draws the vector of the received velocity data from det device
        self.draw_velocity_vector(image, self.pos) if self.draw_velocity else None

        # Draws the N previous tracked positions
        self.draw_tracked_path(image) if self.draw_tracked else None

    def calibrate_direction(self):
        # TODO: Refactor and verify calibration - 5/1/14

        print "starts calibration"
        try:
            self.start_linear_calibration()
        except IndexError:  # TODO: Add correct exception - 4/24/14
            print "Start calibration failed"

        # DEVICE TO HEADING ZERO
        self.device.roll(0, 0)
        time.sleep(2.0)

        # DEVICE DRIVE STRAIGHT LINE
        self.device.roll(70, 0)
        time.sleep(0.5)

        # DEVICE STOP
        self.device.roll(0, 0)
        time.sleep(2.0)

        try:
            tracked_direction, speed = self.stop_linear_calibration()
        except IndexError:  # TODO: Add correct exceptions - 4/23/14
            print "stop calibration failed"
        else:
            #sphero_heading = sphero.device_to_host_angle(0)  # self.vector_control.direction
            #heading_vector = Vector2D(1, 0).set_angle(sphero_heading)
            tracked_vector = Vector2D(1, 0).set_angle(tracked_direction)
            print "tracked direction is", tracked_direction

            #offset = heading_vector.get_offset(tracked_vector)

            #print "Sphero", sphero_heading, "tracked", tracked_direction, "off_by", offset,

            #new_heading = (sphero_heading - offset) % 360
            #new_zero = (0-(offset*-1)) % 360
            #print "new heading:", new_heading, new_zero
            #self.vector_control.direction = new_heading
            #self.device.set_heading(new_zero)

            #print "New zero should be", sphero.host_to_device_angle(off_by_dir)

            #print self.device.configure_locator(0, 0, sphero.host_to_device_angle(new_zero))

            self.device.roll(0, sphero.host_to_device_angle(-tracked_vector.rotate(180).angle))
            time.sleep(2.0)
            print self.device.set_heading(sphero.host_to_device_angle(0)).success
