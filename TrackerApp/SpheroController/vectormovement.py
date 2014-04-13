from threading import Thread
import time, sphero
from util import Vector2D

DEFAULT_UPDATE_RATE = 25.0


class SpheroVectorMovement(object):
    """
    A class for controlling the sphero device using vectors
    """

    def __init__(self, device):
        """

        @param device: Sphero to control
        @type device: sphero.SpheroAPI
        """

        super(SpheroVectorMovement, self).__init__()
        # Sphero device
        self.device = device

        # MOVEMENT
        self._is_running = False
        self._cmd_thread = None

        # UPDATE RATE
        self.achieved_fps = None
        self._time_delta = 1.0 / DEFAULT_UPDATE_RATE

        # MOVEMENT
        self._vector = Vector2D(0, 0)
        self._last_vector = self._vector.copy()

        self.turn_rate = 0.0

        # Keep track of last heading if speed vector is zero
        self._heading = Vector2D(1.0, 0)
        self._heading.angle = self._vector.angle

    @property
    def vector(self):
        """
        Returns a Vector2D rep of the speed and direction of the sphero device
        @return: A vector2d representation of speed and direction
        @rtype: Vector2D
        """
        return self._vector

    @vector.setter
    def vector(self, vector):
        """
        Sets the speed and direction of the device from a vector2d instance
        @param vector:
        @type vector: Vector2D
        """
        self._update_heading()
        self._vector = vector

    @property
    def direction(self):
        """
        Returns the current set direction for the device
        @return: direction in degrees
        @rtype: float or int
        """
        if self.vector.magnitude:
            return self.vector.angle
        return self._heading.angle

    @direction.setter
    def direction(self, value):
        """
        Sets a new direction for the device
        @param value: the new direction in degrees
        @type value: int or float
        """
        self.vector.angle = value
        self._heading.angle = value

    @property
    def speed(self):
        """
        Gets the current set speed for the device
        @return: Speed in the range of 0, 255
        """
        return min([self.vector.magnitude, 255])

    @speed.setter
    def speed(self, value):
        """
        Sets a new speed for the device. speed should be in the range from 0, 255
        @param value: the new speed
        @type value: int or float
        """
        self.vector.set_length(value)

    @property
    def fps(self):
        """
        The currently set max update rate for the device
        @return: update rate for the device
        @rtype: int or float
        """
        return 1.0 / self._time_delta

    @fps.setter
    def fps(self, value):
        """
        Set max update rate for device
        @param value: Update rate updates/sec
        @type value: int or float
        """
        self._time_delta = 1.0 / value

    def start(self):
        """
        Start the cmd loop for starting to execute movements commands to sphero
        @return: True if successfully started, False else
        @rtype: bool
        """
        if not self._cmd_thread:
            self._is_running = True
            self._cmd_thread = Thread(target=self._control_loop, name="SpheroVectorCtrlLoop")
            self._cmd_thread.daemon = True
            self._cmd_thread.start()
            return True
        return False

    def stop(self):
        """
        Stops sending movement commands to devcie
        """
        self._is_running = False

    def _sleep(self, t0, t1):
        """
        Helper method: Used to ctrl the correct update rate from the times used to perform cmd to device
        @param t0: Time before cmd
        @param t1: Time after cmd
        """
        time_used = t1 - t0
        sleep_time = self._time_delta - time_used
        if sleep_time > 0:
            time.sleep(sleep_time)

    @staticmethod
    def _calc_fps(t0, t2):
        """
        Helper method: Calculates the current update rate from the
        @param t0:
        @param t2:
        @return: current fps
        """
        try:
            return 1.0 / (t2 - t0)
        except ZeroDivisionError:
            return -1.

    def _control_loop(self):
        """
        Helper method: main loop for execution of motion commands to device.
        """
        while self._is_running:
            t0 = time.time()

            # Perform logic
            self._move_device()

            # Calculates correct update rate
            t1 = time.time()
            self._sleep(t0, t1)
            t2 = time.time()
            self.achieved_fps = self._calc_fps(t0, t2)

    def _move_device(self):
        """
        Helper method: handle updates to sphero
        """
        self._update_heading()
        if self._is_new_movement():
            speed = self._vector.magnitude
            direction = sphero.host_to_device_angle(self._heading.angle)
            if self.device:
                if self.device.connected():
                # TODO catch all exceptions from sphero and handle them!!!
                    self.device.roll(min([speed, 255]), direction)
            self._last_vector = self._vector.copy()

    def _update_heading(self):
        """
        Helper method: Updates the state of the class and calculates the new heading.
        """
        turn = self.turn_rate  # * self._time_delta         # TODO add turn rate per second?
        if self._vector.magnitude:
            self._vector.angle += turn
            self._heading.angle = self._vector.angle
        else:
            self._heading.angle += turn

    def _is_new_movement(self):
        """
        Helper method: checks if there has been some changes to the currently set movement for the device

        @return: True if movement has changed, False else
        @rtype: bool
        """
        speed_changed = self._last_vector != self._vector
        return speed_changed or self.turn_rate


if __name__ == "__main__":
    # create a device to connect to
    import sphero, random

    dev = sphero.SpheroAPI(bt_name="Sphero-YGY", bt_addr="68:86:e7:02:3a:ae")  # 2
    svm = SpheroVectorMovement(dev)
    svm.fps = 25.0
    svm.start()

    def on_collision(*args):
        print "COLLISION", args
        svm.vector.angle += 180
        svm.vector.set_length(255)
        time.sleep(1.0)
        svm.vector.set_length(55)

    dev.connect()
    dev.set_option_flags(motion_timeout=False)
    dev.set_collision_cb(on_collision)
    dev.configure_collision_detection()

    svm.vector.set_length(50)

    for _ in range(0, 1000):
        time.sleep(random.randrange(5, 20))
        svm.vector.angle = random.randrange(1, 360)
        svm.vector.set_length(random.randrange(60, 255))
        print "new angle"

    # svm.turn_rate = 1
    # svm.vector.set_length(10)
    # time.sleep(5)
    #
    # for _ in range(0, 2):
    #     svm.vector.set_length(40)
    #     for x in range(0, 360, 5):
    #         svm.vector.angle = x
    #         time.sleep(0.1)
    #     svm.vector.set_length(0)
    #
    # square_size_sec = 2.0
    # for _ in range(0, 2):
    #     svm.vector.set_values(40, 0)
    #     time.sleep(square_size_sec)
    #
    #     svm.vector.set_values(0, 40)
    #     time.sleep(square_size_sec)
    #
    #     svm.vector.set_values(-40, 0)
    #     time.sleep(square_size_sec)
    #
    #     svm.vector.set_values(0, -40)
    #     time.sleep(square_size_sec)
    #
    # svm.vector.set_values(0, 0)
    # time.sleep(1)
    time.sleep(600)
    svm.stop()



