from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from webcam import C920WebCam


class SimpleValueSlider(BoxLayout):
    def __init__(self, title, value, min_val, max_val, default_val, on_value_cb, **kwargs):
        super(SimpleValueSlider, self).__init__(**kwargs)

        # Title Label
        self.title_label = Label(text=title)

        # Value slider
        self.slider = Slider(step=1)
        self.slider.value = value
        self.slider.range = min_val, max_val
        self.slider.bind(value=self.on_slider_value_changed)
        self.on_value_cb = on_value_cb

        # Value title
        self.value_label = Label(text=str(value))

        # Default button
        self.button = Button(text="reset")
        self.button.bind(on_press=self.on_button_press)
        self.default_value = default_val

        # SETUP LAYOUT
        self.add_widget(self.title_label)
        self.add_widget(self.slider)
        self.add_widget(self.value_label)
        self.add_widget(self.button)

    def on_button_press(self, *args):
        self.slider.value = self.default_value

    def on_slider_value_changed(self, *args):
        self.value_label.text = str(args[1])
        self.on_value_cb(*args)


class SimpleAutoModeValueSlider(BoxLayout):
    def __init__(self, title, value, min_val, max_val, default_val, on_value_cb, active, on_activate, **kwargs):
        super(SimpleAutoModeValueSlider, self).__init__(**kwargs)
        self.simple_value_slider = SimpleValueSlider(title, value, min_val, max_val, default_val, on_value_cb)
        self.simple_value_slider.disabled = active

        auto_menu = BoxLayout()
        label = Label(text="auto mode:")

        self.check_box = CheckBox(active=active)
        self.check_box.size_hint_x = 0.4
        self.check_box.bind(active=self.on_switch_changed)
        self.on_activate = on_activate

        auto_menu.add_widget(label)
        auto_menu.add_widget(self.check_box)
        auto_menu.size_hint_x = 0.2

        self.add_widget(self.simple_value_slider)
        self.add_widget(auto_menu)

    def on_switch_changed(self, *args):
        self.simple_value_slider.disabled = args[1]
        self.on_activate(*args)


class CameraController(BoxLayout):
    def __init__(self, **kwargs):
        super(CameraController, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.webcam = C920WebCam(0)  # TODO change device number
        self.camera_controls = BoxLayout(orientation="vertical")

        self.exposure_ctrl = SimpleAutoModeValueSlider(title="Exposure",
                                                       value=self.webcam.exposure,
                                                       min_val=self.webcam.exposure_min,
                                                       max_val=self.webcam.exposure_max,
                                                       default_val=self.webcam.exposure_default,
                                                       on_value_cb=self.on_exposure,
                                                       active=self.webcam.auto_exposure,
                                                       on_activate=self.on_exposure_auto)

        self.wb_ctrl = SimpleAutoModeValueSlider(title="WB",
                                                 value=self.webcam.white_balance,
                                                 min_val=self.webcam.white_balance_min,
                                                 max_val=self.webcam.white_balance_max,
                                                 default_val=self.webcam.white_balance_default,
                                                 on_value_cb=self.on_white_balance,
                                                 active=self.webcam.auto_white_balance,
                                                 on_activate=self.on_wb_auto)

        self.focus_ctrl = SimpleAutoModeValueSlider(title="FOCUS",
                                                    value=self.webcam.focus,
                                                    min_val=self.webcam.focus_min,
                                                    max_val=self.webcam.focus_max,
                                                    default_val=self.webcam.focus_default,
                                                    on_value_cb=self.on_focus,
                                                    active=self.webcam.auto_focus,
                                                    on_activate=self.on_focus_auto)

        self.zoom_ctrl = SimpleValueSlider(title="ZOOM",
                                           value=self.webcam.zoom,
                                           min_val=self.webcam.zoom_min,
                                           max_val=self.webcam.zoom_max,
                                           default_val=self.webcam.zoom_default,
                                           on_value_cb=self.on_zoom)

        self.gain_ctrl = SimpleValueSlider(title="GAIN",
                                           value=self.webcam.gain,
                                           min_val=self.webcam.gain_min,
                                           max_val=self.webcam.gain_max,
                                           default_val=self.webcam.gain_default,
                                           on_value_cb=self.on_gain)

        self.brightness_ctrl = SimpleValueSlider(title="BRIGHTNESS",
                                                 value=self.webcam.brightness,
                                                 min_val=self.webcam.brightness_min,
                                                 max_val=self.webcam.brightness_max,
                                                 default_val=self.webcam.brightness_default,
                                                 on_value_cb=self.on_brightness)

        self.contrast_ctrl = SimpleValueSlider(title="CONTRAST",
                                               value=self.webcam.contrast,
                                               min_val=self.webcam.contrast_min,
                                               max_val=self.webcam.contrast_max,
                                               default_val=self.webcam.contrast_default,
                                               on_value_cb=self.on_contrast)

        self.saturation_ctrl = SimpleValueSlider(title="SATURATION",
                                                 value=self.webcam.saturation,
                                                 min_val=self.webcam.saturation_min,
                                                 max_val=self.webcam.saturation_max,
                                                 default_val=self.webcam.saturation_default,
                                                 on_value_cb=self.on_saturation)

        self.sharpness_ctrl = SimpleValueSlider(title="SHARPNESS",
                                                value=self.webcam.sharpness,
                                                min_val=self.webcam.sharpness_min,
                                                max_val=self.webcam.sharpness_max,
                                                default_val=self.webcam.sharpness_default,
                                                on_value_cb=self.on_sharpness)

        # ADD Camera controls to screen
        self.camera_controls.add_widget(self.exposure_ctrl)
        self.camera_controls.add_widget(self.wb_ctrl)
        self.camera_controls.add_widget(self.focus_ctrl)

        self.camera_controls.add_widget(self.zoom_ctrl)
        self.camera_controls.add_widget(self.brightness_ctrl)
        self.camera_controls.add_widget(self.contrast_ctrl)
        self.camera_controls.add_widget(self.gain_ctrl)
        self.camera_controls.add_widget(self.saturation_ctrl)
        self.camera_controls.add_widget(self.sharpness_ctrl)
        self.add_widget(self.camera_controls)

    # WHITE BALANCE
    def on_wb_auto(self, *args):
        self.webcam.auto_white_balance = args[1]

    def on_white_balance(self, *args):
        self.webcam.white_balance = args[1]

    # EXPOSURE
    def on_exposure_auto(self, *args):
        self.webcam.auto_exposure = args[1]

    def on_exposure(self, *args):
        self.webcam.exposure = args[1]

    # FOCUS
    def on_focus_auto(self, *args):
        self.webcam.auto_focus = args[1]

    def on_focus(self, *args):
        self.webcam.focus = args[1]

    def on_brightness(self, *args):
        self.webcam.brightness = args[1]

    def on_zoom(self, *args):
        self.webcam.zoom = args[1]

    def on_gain(self, *args):
        self.webcam.gain = args[1]

    def on_contrast(self, *args):
        self.webcam.contrast = args[1]

    def on_saturation(self, *args):
        self.webcam.saturation = args[1]

    def on_sharpness(self, *args):
        self.webcam.sharpness = args[1]


class CameraAPP(App):
    def build(self):
        return CameraController()


if __name__ == "__main__":
    CameraAPP().run()
