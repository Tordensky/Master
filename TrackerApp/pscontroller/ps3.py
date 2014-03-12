import pygame


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

    EVENT_AXIS_CHANGE = pygame.JOYAXISMOTION
    EVENT_BUTTON_DOWN = pygame.JOYBUTTONDOWN
    EVENT_BUTTON_UP = pygame.JOYBUTTONUP

    def __init__(self):
        self._button_down_cb = {}
        self._button_up_cb = {}
        self._axis_cb = {}

    def set_events(self, button_down={}, button_up={}, axis={}):
        self.set_button_down_events(button_down)
        self.set_button_up_events(button_up)
        self.set_axis_change_events(axis)

    def set_button_down_events(self, event_dict):
        for button_id, cb in event_dict.iteritems():
            self.set_button_down_event(button_id, cb)

    def set_button_down_event(self, button_id, cb):
        self._button_down_cb[button_id] = cb

    def set_button_up_events(self, event_dict):
        for button_id, cb in event_dict.iteritems():
            self.set_button_up_event(button_id, cb)

    def set_button_up_event(self, button_id, cb):
        self._button_up_cb[button_id] = cb

    def set_axis_change_events(self, event_dict):
        for axis_id, cb in event_dict.iteritems():
            self.set_axis_change_event(axis_id, cb)

    def set_axis_change_event(self, axis_id, cb):
        self._axis_cb[axis_id] = cb

    def handle_event(self, e):
        if e.type == PS3C.EVENT_BUTTON_DOWN:
            self._on_button_down(e)
        elif e.type == PS3C.EVENT_BUTTON_UP:
            self._on_button_up(e)
        elif e.type == PS3C.EVENT_AXIS_CHANGE:
            self._on_axis_event(e)

    def _on_button_down(self, e):
        try:
            self._button_down_cb[e.button]()
        except KeyError:
            pass

    def _on_button_up(self, e):
        try:
            self._button_up_cb[e.button]()
        except KeyError:
            pass

    def _on_axis_event(self, e):
        try:
            self._axis_cb[e.axis](e.value)
        except KeyError:
            pass

if __name__ == "__main__":
    # EXAMPLE CODE TO USE THE PS3 JOYSTICK CLASS

    from pygame import joystick
    pygame.init()
    if not joystick.get_init():
        joystick.init()

    def button_down_cb():
        print "Button down"

    def button_up_cb():
        print "Button up"

    def axis_cb(value):
        print "axis:", value

    js1 = joystick.Joystick(0)
    js2 = joystick.Joystick(1)

    js1.init()
    js2.init()

    ps1 = PS3C()
    ps1.set_button_down_event(PS3C.BUTTON_CIRCLE, button_down_cb)
    ps1.set_button_up_event(PS3C.BUTTON_CIRCLE, button_up_cb)

    ps1.set_events(
        button_down={
            PS3C.BUTTON_SQUARE: button_down_cb
        },
        button_up={
            PS3C.BUTTON_DOWN: button_up_cb
        },
        axis={
            PS3C.AXIS_RIGHT: axis_cb
        }
    )

    ps2 = PS3C()
    ps2.set_button_down_event(PS3C.BUTTON_CIRCLE, button_down_cb)
    ps2.set_axis_change_event(PS3C.AXIS_JOY_R_VER, axis_cb)

    run = True
    while run:
        for event in pygame.event.get():
            if event.type in [pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYAXISMOTION]:
                if event.joy == 0:
                    ps1.handle_event(event)
                elif event.joy == 1:
                    ps2.handle_event(event)