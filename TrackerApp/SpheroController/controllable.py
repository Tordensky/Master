import random
from threading import Thread
import time
import math
from SpheroController import vectormovement

from SpheroController.tracablesphero import TraceableSphero
import ps3
import sphero
from sphero import SensorStreamingConfig
from util import Vector2D
from tracker import ImageGraphics as Ig, DrawError
import util


class ControllableSphero(TraceableSphero):
    def __init__(self, device):
        """

        @param device: The device to control
        @type device: sphero.SpheroAPI
        """
        super(ControllableSphero, self).__init__(device, name=device.bt_name)
        self.border = 130
        self.dot_drive = False
        self.dot_speed_y = 0.0
        self.dot_speed_x = 0.0
        self.device = device

        self.vector_control = vectormovement.SpheroVectorMovement(self.device)
        self.vector_control.start()

        self._sphero_clean_up_cb = None
        self._cmd_retries = 5

        self._ps3_controller = None

        self.ball_thread = None

        self._motion_timeout = 5000

        # SENSOR STREAMING
        self._ssc = SensorStreamingConfig()

        # SPHERO TRACKING
        self.speed_vector = Vector2D(1, 0)

        self._run_bounce = True

        # SETUP
        self._setup_sphero()

        # Virtual Dot
        self._dot_pos = Vector2D(10, 10)

    def dot_x(self, value):
        self.dot_speed_x = value * 20.0

    def dot_y(self, value):
        self.dot_speed_y = -value * 20.0

    def activate_dot(self):
        self.dot_drive = True

    def deactivate_dot(self):
        self.dot_drive = False
        self.vector_control.speed = 0.0

    def update_dot(self):
        self._dot_pos.x += self.dot_speed_x
        if self._dot_pos.x >= self.screen_size[0]:
            self._dot_pos.x = self.screen_size[0]
        elif self._dot_pos.x <= 0:
            self._dot_pos.x = 0

        self._dot_pos.y += self.dot_speed_y
        if self._dot_pos.y >= self.screen_size[1]:
            self._dot_pos.y = self.screen_size[1]
        elif self._dot_pos.y <= 0:
            self._dot_pos.y = 0

        if self.pos is not None:
            path_to_dot = (self._dot_pos - self.pos)
            #print "Angle to dot", path_to_dot.angle,

            if self.dot_drive:
                self.vector_control.direction = path_to_dot.angle
                self.vector_control.speed = min(path_to_dot.magnitude / 3.0, 100)

    def draw_graphics(self, image):
        super(ControllableSphero, self).draw_graphics(image)

        try:
            self.update_dot()
            Ig.draw_circle(image, self._dot_pos, 10, util.Color((255, 100, 20)))
        except DrawError:
            pass

        if self.ball_thread:
            width = self.screen_size[0] - (2*self.border)
            height = self.screen_size[1] - (2*self.border)
            Ig.draw_rectangle(image, (self.border, self.border), width, height, util.Color((255, 0, 0)))

    def _configure_sensor_streaming(self):
        self._ssc.num_packets = SensorStreamingConfig.STREAM_FOREVER
        self._ssc.sample_rate = 50
        self._ssc.stream_odometer()
        self._ssc.stream_imu_angle()
        self._ssc.stream_velocity()
        self._ssc.stream_gyro()
        self._ssc.stream_gyro_raw()
        self.device.set_data_streaming(self._ssc)

    def _setup_sphero(self):
        self.device.set_option_flags(
            motion_timeout=True,
            tail_led=True,
            vector_drive=True
        )
        self.device.set_motion_timeout(self._motion_timeout)
        self.device.set_rgb(0xFF, 0xFF, 0xFF, True)

        self._configure_sensor_streaming()

    def start_bouncing_ball(self):
        if self.ball_thread is None:
            self._run_bounce = True
            self.ball_thread = Thread(target=self.bouncing_ball, name="Sphero Bounce")
            self.ball_thread.daemon = True
            self.ball_thread.start()

    def stop_bouncing_ball(self):
        self._run_bounce = False
        self.ball_thread = None

    def bouncing_ball(self):
        screen_x = self.screen_size[0]
        screen_y = self.screen_size[1]
        self.vector_control.speed = 60
        self.vector_control.direction = 45

        while self._run_bounce:
            #self.vector_control.speed = 60
            pos = self.last_valid_pos
            if pos.x >= screen_x-self.border:
                self.vector_control.vector.x = -abs(self.vector_control.vector.x)
            elif pos.x <= self.border:
                self.vector_control.vector.x = abs(self.vector_control.vector.x)

            if pos.y >= screen_y - self.border:
                self.vector_control.vector.y = -abs(self.vector_control.vector.y)

            elif pos.y <= self.border:
                self.vector_control.vector.y = abs(self.vector_control.vector.y)

            time.sleep(0.01)
        self.vector_control.speed = 0.0

    def set_ps3_controller(self, ps3_controller):
        """
        Used to set and map the PS3 controller to run the sphero commands

        @param ps3_controller:
        @type ps3_controller: ps3.PS3C
        """
        self._ps3_controller = ps3_controller
        self._map_controls(ps3_controller)

    def _map_controls(self, ps3_controller):
        ps3_controller.set_events(
            button_press={
                ps3.BUTTON_CIRCLE: self.calibrate,
                ps3.BUTTON_SQUARE: self.lights_on,
                ps3.BUTTON_CROSS: self.lights_random_color,
                ps3.BUTTON_START: self.disconnect,

                ps3.BUTTON_JOY_PAD_DOWN: self.reset_heading,
                ps3.BUTTON_JOY_PAD_UP: self.start_bouncing_ball,
                ps3.BUTTON_JOY_PAD_LEFT: self.stop_bouncing_ball,
                ps3.BUTTON_L1: self.heading_left,
                ps3.BUTTON_R1: self.heading_right,
                ps3.BUTTON_JOY_PAD_RIGHT: self.activate_dot
            },
            button_release={
                ps3.BUTTON_JOY_PAD_RIGHT: self.deactivate_dot
                #ps3.BUTTON_CIRCLE: self.stop_calibration
            },
            axis={
                ps3.AXIS_JOYSTICK_R_VER: self.set_y,
                ps3.AXIS_JOYSTICK_R_HOR: self.set_x,
                ps3.AXIS_JOYSTICK_L_HOR: self.dot_x,
                ps3.AXIS_JOYSTICK_L_VER: self.dot_y
            }
        )

    def heading_left(self):
        self.device.set_heading(350)
        self.device.roll(0, 0)

    def heading_right(self):
        self.device.set_heading(10)
        self.device.roll(0, 0)

    def calibrate(self):
        self.vector_control.stop()
        self.calibrate_direction()
        self.vector_control.start()

    # def start_calibration(self):
    #     print "starts calibration"
    #     try:
    #         self.traceable.start_linear_calibration()
    #     except IndexError:  # TODO: Add correcect exception - 4/24/14
    #         print "Start calibration failed"
    #     self.vector_control.stop()
    #
    #     self.device.roll(0, 0)
    #     time.sleep(2.0)
    #
    #     self.device.roll(50, 0)
    #     time.sleep(1.0)
    #
    #     self.device.roll(0, 0)
    #     time.sleep(2.0)
    #
    #     self.stop_calibration()
    #
    # def stop_calibration(self):
    #     try:
    #         tracked_direction, speed = self.traceable.stop_linear_calibration()
    #     except IndexError:  # TODO: Add correct exceptions - 4/23/14
    #         print "stop calibration failed"
    #     else:
    #         sphero_heading = sphero.device_to_host_angle(0)  # self.vector_control.direction
    #         heading_vector = Vector2D(1, 0).set_angle(sphero_heading)
    #         tracked_vector = Vector2D(1, 0).set_angle(tracked_direction)
    #
    #         offset = heading_vector.get_offset(tracked_vector)
    #
    #         print "Sphero", sphero_heading, "tracked", tracked_direction, "off_by", offset,
    #
    #         new_heading = (sphero_heading - offset) % 360
    #         new_zero = (0-(offset*-1)) % 360
    #         print "new heading:", new_heading, new_zero
    #         #self.vector_control.direction = new_heading
    #         #self.device.set_heading(new_zero)
    #
    #         #print "New zero should be", sphero.host_to_device_angle(off_by_dir)
    #
    #         #print self.device.configure_locator(0, 0, sphero.host_to_device_angle(new_zero))
    #
    #         self.device.roll(0, sphero.host_to_device_angle(-tracked_vector.rotate(180).angle))
    #         time.sleep(2.0)
    #         print self.device.set_heading(sphero.host_to_device_angle(0)).success
    #
    #         self.vector_control.direction = 90 # new_heading
    #         #self.vector_control.direction = calibration_vector.angle
    #
    #         self.vector_control.start()

    def reset_heading(self):  # TODO: REMOVE OR FIX - 4/24/14

        print "RESETS"
        self.device.set_heading(0)
        self.vector_control.direction = sphero.device_to_host_angle(0)

    def set_x(self, value):
        #self.vector_control.turn_rate = math.tan(value) * -5

        self.vector_control.vector.x = value * 75.0

    def set_y(self, value):
        #self.vector_control.speed = abs(value * 255.0)

        self.vector_control.vector.y = value * -75.0

    def disconnect(self):
        self.device.disconnect()
        self._on_sphero_disconnected()

    def lights_random_color(self):
        r = random.randrange(0, 255)
        g = random.randrange(0, 255)
        b = random.randrange(0, 255)
        print "Lights random color: ", self.device.set_rgb(r, g, b, True).success

    def lights_on(self):
        print "LIGHTS OFF:", self.device.set_rgb(255, 255, 255, True).success

    def ping(self):
        print "PING SUCCESSFUL:", self.device.ping().success

    def get_battery_state(self):
        print self.device.get_power_state()

    def set_sphero_disconnected_cb(self, cb):
        self._sphero_clean_up_cb = cb

    def _on_sphero_disconnected(self):
        self.vector_control.stop()
        print "PS3 / SPHERO clean up"
        if self._ps3_controller:
            self._ps3_controller.free()
        self._sphero_clean_up_cb(self.device)