import pygame
from pygame import joystick
import random
import sys
import time
import ps3

from controller.ps_controller import PS3C
import sphero
from sphero import SpheroAPI
from sphero.core import SpheroError


pygame.init()

if not joystick.get_init():
    joystick.init()

js = joystick.Joystick(0)
print joystick.get_count()
js.init()


js2 = joystick.Joystick(1)
js2.init()


# print js.get_numbuttons()

# for i in xrange(js.get_numaxes()):
#     print js.get_axis(i)

joystick_pos = {}

fwd = 0.0
turn = 0.0
heading = 0


def cb(msg):
    """
    @type msg: sphero.SensorStreamingResponse
    @param msg:
    """
    print msg.sensor_data
    #pass

#s = SpheroAPI(bt_name="Sphero-YGY", bt_addr="68:86:e7:02:3a:ae")
s = SpheroAPI(bt_name="Sphero-YGY", bt_addr="68:86:e7:03:24:54")  # SPHERO-YGY NO: 5


def deactivate_streaming():
    s.stop_data_streaming()


def activate_streaming():
    global ssc
    ssc = sphero.SensorStreamingConfig()
    ssc.stream_odometer()
    ssc.stream_acceleration_one()
    ssc.stream_velocity()
    ssc.n = 200
    s.set_sensor_streaming_cb(cb)
    s.set_data_streaming(ssc)


if not s.connect():
    sys.exit(1)
else:
    print "sphero connected"
    s.configure_locator(0, 0, 0)
    s.set_option_flags(tail_LED=True)

    activate_streaming()


def set_random_color():
    global r, g, b
    r = random.randrange(0, 255)
    g = random.randrange(0, 255)
    b = random.randrange(0, 255)
    s.set_rgb(r, g, b, True)


run = True
while run:
    for event in pygame.event.get():
        print event
        if event.type == pygame.JOYBUTTONDOWN:
            n = event.button
            if n == PS3C.BUTTON_TRIANGLE:
                s.disconnect()
                run = False

            elif n == PS3C.BUTTON_X:
                set_random_color()

            elif n == PS3C.BUTTON_SQUARE:
                s.set_rgb(0, 0, 0, True)

            elif n == PS3C.BUTTON_L1:
                s.configure_locator(0, 0, 0)

            elif n == PS3C.BUTTON_CIRCLE:
                print "PING success: ", s.ping().success

            elif n == PS3C.BUTTON_JOY_PAD_UP:
                activate_streaming()

            elif n == PS3C.BUTTON_JOY_PAD_DOWN:
                deactivate_streaming()

            elif n == PS3C.BUTTON_JOY_PAD_LEFT:
                pass
                #print s.read_locator()

            elif n == PS3C.BUTTON_JOY_PAD_RIGHT:
                print s.get_power_state()

            elif n == PS3C.BUTTON_L2:
                print "BOOOOOOOOOOOST"
                try:
                    s.set_boost_with_time(True)
                except SpheroError:
                    print "NOOO BOOST"

        elif event.type == pygame.JOYBUTTONUP:
            if n == PS3C.BUTTON_L2:
                print "NO BOOST =("
                s.set_boost_with_time(False)

        elif event.type == pygame.JOYAXISMOTION:
            new = event.value
            try:
                old = joystick_pos[event.axis]
            except KeyError:
                old = -1000

            if new != old:
                joystick_pos[event.axis] = new
                if event.axis == 1:
                    fwd = event.value
                    #print "fwd", event.value
                elif event.axis == 2:
                    turn = event.value
                    #print "turn", event.value

    speed = int(abs(fwd) * 0xFF)

    heading += turn * 15
    if fwd > 0.2:
        direct = (heading - 180) % 359
    else:
        direct = heading % 359

    #print speed, direct
    try:
        s.roll(speed, direct, 2)
    except SpheroError:
        print "FAILS TO EXECUTE ROLL"

    time.sleep(1.0 / 25.0)

if __name__ == "__main__":
    print "test"