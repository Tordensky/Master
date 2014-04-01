import subprocess as sub
#                      brightness (int)    : min=0 max=255 step=1 default=128 value=117
#                        contrast (int)    : min=0 max=255 step=1 default=128 value=252
#                      saturation (int)    : min=0 max=255 step=1 default=128 value=128
#  white_balance_temperature_auto (bool)   : default=1 value=1
#                            gain (int)    : min=0 max=255 step=1 default=0 value=255
#            power_line_frequency (menu)   : min=0 max=2 default=2 value=2
# 				                                0: Disabled
# 			            	                    1: 50 Hz
#            				                    2: 60 Hz
#       white_balance_temperature (int)    : min=2000 max=6500 step=1 default=4000 value=4513 flags=inactive
#                       sharpness (int)    : min=0 max=255 step=1 default=128 value=128
#          backlight_compensation (int)    : min=0 max=1 step=1 default=0 value=0
#                   exposure_auto (menu)   : min=0 max=3 default=3 value=1
#        				                        1: Manual Mode
# 		        		                        3: Aperture Priority Mode
#               exposure_absolute (int)    : min=3 max=2047 step=1 default=250 value=80
#          exposure_auto_priority (bool)   : default=0 value=0
#                    pan_absolute (int)    : min=-36000 max=36000 step=3600 default=0 value=0
#                   tilt_absolute (int)    : min=-36000 max=36000 step=3600 default=0 value=0
#                  focus_absolute (int)    : min=0 max=250 step=5 default=0 value=0 flags=inactive
#                      focus_auto (bool)   : default=1 value=1
#                   zoom_absolute (int)    : min=100 max=500 step=1 default=100 value=100


class C920WebCam(object):
    """
    Wrapper class to handle Logitech C920 WebCam adjustments.
    Note: Requires v2l2-util linux module
    """
    # Exposure values
    _auto_exposure_tag = "exposure_auto"
    exposure_tag = "exposure_absolute"
    exposure_min = 3
    exposure_max = 2047
    exposure_default = 250

    _exposure_manual_mode = 1
    _exposure_aperture_priority_mode = 3

    # Exposure values
    _auto_white_balance_tag = "white_balance_temperature_auto"
    auto_white_balance_default = True
    _white_balance_tag = "white_balance_temperature"
    white_balance_min = 2000
    white_balance_max = 6500
    white_balance_default = 4000

    # GAIN VALUES
    _gain_tag = "gain"
    gain_min = 0
    gain_max = 255
    gain_default = 0

    # BRIGHTNESS VALUES
    _brightness_tag = "brightness"
    brightness_max = 255
    brightness_min = 0
    brightness_default = 128

    # CONTRAST VALUES
    _contrast_tag = "contrast"
    contrast_max = 255
    contrast_min = 0
    contrast_default = 128

    # SATURATION VALUES
    _saturation_tag = "saturation"
    saturation_max = 255
    saturation_min = 0
    saturation_default = 128

    # SHARPNESS VALUES
    _sharpness_tag = "sharpness"
    sharpness_max = 255
    sharpness_min = 0
    sharpness_default = 128

    # ZOOM VALUES
    _zoom_tag = "zoom_absolute"
    zoom_max = 500
    zoom_min = 100
    zoom_default = 100

    # FOCUS VALUES
    _focus_tag = "focus_absolute"
    auto_focus_tag = "focus_auto"
    focus_max = 250
    focus_min = 0
    focus_default = 0

    # BACK LIGHT COMPENSATION
    _back_light_compensation_tag = "backlight_compensation"
    back_light_compensation_default = False

    # POWER LINE FREQUENCY
    _power_line_freq_tag = "power_line_frequency"

    def __init__(self, dev_num):
        super(C920WebCam, self).__init__()
        self.dev_num = dev_num

    @property
    def powerline_frequency(self):
        """
        Returns the current power line frequency
        0: Disabled
        1: 50 Hz
        2: 60 Hz
        @return: current value
        @rtype: int
        """
        return self._read_property(self._power_line_freq_tag)

    @powerline_frequency.setter
    def powerline_frequency(self, value):
        """
        Sets the power frequency
        0: Disabled
        1: 50 Hz
        2: 60 Hz
        @param value: new power frequency
        @type value: int
        """
        self._validate_range(0, 2, value)
        self._set_property(self._power_line_freq_tag, value)


    # ZOOM CONTROLS
    @property
    def zoom(self):
        """
        Get current zoom level
        min=0 max=255 step=1 default=128
        @return: current value
        @rtype: int
        """
        return self._read_property(self._zoom_tag)

    @zoom.setter
    def zoom(self, value):
        """
        Set zoom
        min=0 max=255 step=1 default=128
        @param value: new value
        @type value: int
        """
        self._validate_range(self.zoom_min, self.zoom_max, value)
        self._set_property(self._zoom_tag, value)


    # SHARPNESS CONTROLS
    @property
    def sharpness(self):
        """
        Get current sharpness
        min=0 max=255 step=1 default=128
        @return: current value
        @rtype: int
        """
        return self._read_property(self._sharpness_tag)

    @sharpness.setter
    def sharpness(self, value):
        """
        Set sharpness
        min=0 max=255 step=1 default=128
        @param value: new value
        @type value: int
        """
        self._validate_range(self.sharpness_min, self.sharpness_max, value)
        self._set_property(self._sharpness_tag, value)

    # SATURATION CONTROLS
    @property
    def saturation(self):
        """
        Get current saturation
        min=0 max=255 step=1 default=128
        @return: current value
        @rtype: int
        """
        return self._read_property(self._saturation_tag)

    @saturation.setter
    def saturation(self, value):
        """
        Set saturation
        min=0 max=255 step=1 default=128
        @param value: new value
        @type value: int
        """
        self._validate_range(self.saturation_min, self.saturation_max, value)
        self._set_property(self._saturation_tag, value)

    # CONTRAST CONTROLS
    @property
    def contrast(self):
        """
        Get current contrast
        min=0 max=255 step=1 default=128 value=117
        @return: current value
        @rtype: int
        """
        return self._read_property(self._contrast_tag)

    @contrast.setter
    def contrast(self, value):
        """
        Set contrast
        min=0 max=255 step=1 default=128 value=117
        @param value: new value
        @type value: int
        """
        self._validate_range(self.contrast_min, self.contrast_max, value)
        self._set_property(self._contrast_tag, value)

    # BRIGHTNESS CONTROLS
    @property
    def brightness(self):
        """
        Get current brightness
        min=0 max=255 step=1 default=128 value=117
        @return: current brightness
        @rtype: int
        """
        return self._read_property(self._brightness_tag)

    @brightness.setter
    def brightness(self, value):
        """
        Set brightens
        min=0 max=255 step=1 default=128 value=117
        @param value: new brightness value
        @type value: int
        """
        self._validate_range(self.brightness_min, self.brightness_max, value)
        self._set_property(self._brightness_tag, value)

    # GAIN CONTROLS
    @property
    def gain(self):
        """
        Get current gain
        min=0 max=255 step=1 default=0 value=255
        @return: current gain
        @rtype: int
        """
        return self._read_property(self._gain_tag)

    @gain.setter
    def gain(self, value):
        """
        Set gain
        min=0 max=255 step=1 default=0 value=255
        @param: current gain
        @type: int
        """
        self._validate_range(self.gain_min, self.gain_max, value)
        self._set_property(self._gain_tag, value)

    # EXPOSURE CONTROLS
    @property
    def exposure(self):
        """
        Get current set exposure from device
        min=3 max=2047 step=1 default=250 value=250 flags=inactive
        @return: current exposure
        @rtype: int
        """
        return self._read_property(self.exposure_tag)

    @exposure.setter
    def exposure(self, exposure):
        """
        Sets a new exposure if auto exposure is disabled
        exposure_absolute: min=3 max=2047 step=1 default=250 value=250 flags=inactive
        @param exposure: The new exposure range:
        @type exposure: int
        """
        self._validate_range(self.exposure_min, self.exposure_max, exposure)
        self._set_property(self.exposure_tag, exposure)

    @property
    def auto_exposure(self):
        """
        Get current state of auto exposure.
        @return: True if activated false ig deactivated
        @rtype: bool
        """
        value = self._read_property(self._auto_exposure_tag)
        return False if value is self._exposure_manual_mode else True

    @auto_exposure.setter
    def auto_exposure(self, state):
        """
        Activate or deactivate auto exposure
        @param state: True for activate, false for deactivate
        @type state: bool
        """
        mode = self._exposure_aperture_priority_mode if state else self._exposure_manual_mode
        self._set_property(self._auto_exposure_tag, mode)

    # FOCUS CONTROLS
    @property
    def focus(self):
        """
        Get current focus value
        @return: current value
        @rtype: int
        """
        return self._read_property(self._focus_tag)

    @focus.setter
    def focus(self, value):
        """
        Sets focus value
        @param value: Focus value
        @type value: int
        """
        self._validate_range(self.focus_min, self.focus_max, value)
        self._set_property(self._focus_tag, value)

    @property
    def auto_focus(self):
        """
        Get current state of auto focus.
        @return: True if activated false if deactivated
        @rtype: bool
        """
        return bool(self._read_property(self.auto_focus_tag))

    @auto_focus.setter
    def auto_focus(self, state):
        """
        Activate or deactivate auto focus
        @param state: True for activate, false for deactivate
        @type state: bool
        """
        self._set_property(self.auto_focus_tag, int(state))

    # BACK LIGHT COMPENSATION
    @property
    def backlight_compensation(self):
        """
        Get current state of back light compensation.
        @return: True if activated false if deactivated
        @rtype: bool
        """
        return bool(self._read_property(self._back_light_compensation_tag))

    @backlight_compensation.setter
    def backlight_compensation(self, state):
        """
        Activate or deactivate back light compensation
        @param state: True for activate, false for deactivate
        @type state: bool
        """
        self._set_property(self._back_light_compensation_tag, int(state))

    # WHITE BALANCE
    @property
    def auto_white_balance(self):
        """
        Get current state of auto white balance.
        @return: True if activated false if deactivated
        @rtype: bool
        """
        return bool(self._read_property(self._auto_white_balance_tag))

    @auto_white_balance.setter
    def auto_white_balance(self, state):
        """
        Activate or deactivate automatic white balance
        @param state: True for activate, false for deactivate
        @type state: bool
        """
        self._set_property(self._auto_white_balance_tag, int(state))

    @property
    def white_balance(self):
        """
        Get current white balance
        @return: current value
        @rtype: int
        """
        return self._read_property(self._white_balance_tag)

    @white_balance.setter
    def white_balance(self, value):
        """
        Sets white balance value
        @param value: Focus value
        @type value: int
        """
        self._validate_range(self.white_balance_min, self.white_balance_max, value)
        self._set_property(self._white_balance_tag, value)

    # HELPER CODE
    def _read_property(self, property_id):
        """
        Helper method: reads a given property from WebCam
        """
        cmd_str = "v4l2-ctl -d %d -C %s" % (self.dev_num, property_id)
        return self._parse_response(self._run_cmd(cmd_str), property_id)

    def _set_property(self, property_id, value):
        """
        Helper method: writes a given property to WebCam
        """
        cmd_str = "v4l2-ctl -d %d -c %s=%d" % (self.dev_num, property_id, value)
        return self._run_cmd(cmd_str)

    @staticmethod
    def _run_cmd(cmd_str):
        """
        Helper method: writes command to system
        """
        p = sub.Popen(cmd_str.split(), stdout=sub.PIPE, stderr=sub.PIPE)
        output, errors = p.communicate()
        return output, errors

    @staticmethod
    def _parse_response(response, property_id):
        """
        Helper method: tries to parse out the number
        """
        # TODO add error handling
        msg, err = response
        if property_id in msg:
            msg = msg.strip()
            msg = msg.split()
            msg = int(msg[1])
        return msg

    @staticmethod
    def _validate_range(min_val, max_val, val):
        """
        Helper method: validates that the given number is in the given range
        """
        # TODO Add check to check that value is integer or float
        if not min_val <= val <= max_val:
            error_msg = "Value %d is not in the valid range from %d->%d" % (val, min_val, max_val)
            raise ValueError(error_msg)


if __name__ == "__main__":
    import time

    c = C920WebCam(0)
    print c.exposure

    c.exposure = 250
    c.exposure = 500
    print c.auto_exposure
    c.auto_exposure = False
    print c.auto_exposure
    c.gain = c.gain_default
    print "gain", c.gain

    c.brightness = 255
    print c.brightness
    c.brightness = c.brightness_default

    c.contrast = 255
    print "contrast", c.contrast
    c.contrast = c.contrast_default

    c.saturation = 255
    print "sat", c.saturation
    c.saturation = c.saturation_default

    c.sharpness = 255
    print "sharpness", c.sharpness
    c.sharpness = c.sharpness_default

    # TEST ZOOM
    for x in xrange(c.zoom_min, c.zoom_max, 10):
        c.zoom = x
        print "zoom", c.zoom

    for y in reversed(range(c.zoom_min, c.zoom_max, 10)):
        c.zoom = y
        print "zoom", c.zoom

    c.zoom = c.zoom_default

    c.auto_focus = False
    print "autofocus", c.auto_focus
    for x in xrange(c.focus_min, c.focus_max, 200):
        c.focus = x
        print "focus", c.focus
    c.focus = c.focus_default
    c.auto_focus = True

    c.backlight_compensation = True
    print "bl-comp", c.backlight_compensation

    c.auto_white_balance = False
    print "auto-wb", c.auto_white_balance

    for x in xrange(c.white_balance_min, c.white_balance_max):
        c.white_balance = x
        print "wb", c.white_balance

    c.auto_white_balance = True
    print "auto-wb", c.auto_white_balance

    print "power-freq", c.powerline_frequency
    c.powerline_frequency = 1
    print "power-freq", c.powerline_frequency
