import pygame
from pygame import joystick
import random
import sys
import time

import sphero
from sphero import SpheroAPI


class PS3C(object):
    BUTTON_SQUARE = 15
    BUTTON_CIRCLE = 13
    BUTTON_X = 14
    BUTTON_TRIANGLE = 12

    BUTTON_UP = 4
    BUTTON_DOWN = 6
    BUTTON_LEFT = 7
    BUTTON_RIGHT = 5

    BUTTON_L1 = 10
    BUTTON_L2 = 8
    BUTTON_R1 = 11
    BUTTON_R2 = 9

    BUTTON_START = 3
    BUTTON_SELECT = 0
    BUTTON_PS = 16

    BUTTON_JOY_L = 1
    BUTTON_JOY_R = 2

    AXIS_SQUARE = 19
    AXIS_CIRCLE = 17
    AXIS_X = 18
    AXIS_TRIANGLE = 16

    AXIS_UP = 8
    AXIS_DOWN = 10
    AXIS_LEFT = None
    AXIS_RIGHT = 9

    AXIS_JOY_L_HOR = 0
    AXIS_JOY_L_VER = 1

    AXIS_JOY_R_HOR = 2
    AXIS_JOY_R_VER = 3

    AXIS_L1 = 14
    AXIS_L2 = 12

    AXIS_R1 = 15
    AXIS_R2 = 13

    AXIS_SIX_AXIS = 25


pygame.init()

if not joystick.get_init():
    joystick.init()
js = joystick.Joystick(0)
print joystick.get_count()
js.init()
print js.get_numbuttons()

for i in xrange(js.get_numaxes()):
    print js.get_axis(i)

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
    ssc.packet_cnt = 0
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
        if event.type == pygame.JOYBUTTONDOWN:
            n = event.button
            if n == PS3C.BUTTON_TRIANGLE:
                s.disconnect()
                run = False

            elif n == PS3C.BUTTON_X:
                set_random_color()

            elif n == PS3C.BUTTON_SQUARE:
                s.configure_locator(0, 0, 0)

            elif n == PS3C.BUTTON_CIRCLE:
                print "PING success: ", s.ping().success

            elif n == PS3C.BUTTON_UP:
                activate_streaming()

            elif n == PS3C.BUTTON_DOWN:
                deactivate_streaming()

            elif n == PS3C.BUTTON_LEFT:
                pass
                #print s.read_locator()

            elif n == PS3C.BUTTON_RIGHT:
                print s.get_power_state()

        elif event.type == pygame.JOYAXISMOTION:
            new = event.value
            try:
                old = joystick_pos[event.axis]
            except KeyError:
                old = -1000

            if new != old:
                print "axis", event.axis, event.value
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
    s.roll(speed, direct, 2)
    time.sleep(1.0 / 25.0)

if __name__ == "__main__":
    print "test"