from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from webcam import C920WebCam


class SimpleValueSlider(BoxLayout):
    def __init__(self, value_property, **kwargs):
        """

        @param value_property:
        @type value_property: c920.AdjustableProperty
        """
        super(SimpleValueSlider, self).__init__(**kwargs)
        self._property = value_property

        # Title Label
        self.title_label = Label(text=value_property.name)

        # Value slider
        self.slider = Slider(step=1)
        self.slider.value = value_property.value
        self.slider.range = value_property.min, value_property.max
        self.slider.bind(value=self.on_slider_value_changed)
        # self.on_value_cb = on_value_cb

        # Value title
        self.value_label = Label(text=str(self._property))

        # Default button
        self.button = Button(text="reset")
        self.button.bind(on_press=self.on_button_press)

        # SETUP LAYOUT
        self.add_widget(self.title_label)
        self.add_widget(self.slider)
        self.add_widget(self.value_label)
        self.add_widget(self.button)

    def on_button_press(self, *args):
        self.slider.value = self._property.default

    def on_slider_value_changed(self, *args):
        self.value_label.text = str(args[1])
        self._property.value = args[1]


class SimpleAutoModeValueSlider(BoxLayout):
    def __init__(self, value_property, **kwargs):
        """

        @param value_property:
        @type value_property: c920.AutoAdjustableCamProperty
        @param kwargs:
        """
        super(SimpleAutoModeValueSlider, self).__init__(**kwargs)
        self._property = value_property

        self.simple_value_slider = SimpleValueSlider(value_property)
        self.simple_value_slider.disabled = value_property.auto

        auto_menu = BoxLayout()
        label = Label(text="auto mode:")

        self.check_box = CheckBox(active=value_property.auto)
        self.check_box.size_hint_x = 0.4
        self.check_box.bind(active=self.on_switch_changed)

        auto_menu.add_widget(label)
        auto_menu.add_widget(self.check_box)
        auto_menu.size_hint_x = 0.2

        self.add_widget(self.simple_value_slider)
        self.add_widget(auto_menu)

    def on_switch_changed(self, *args):
        self.simple_value_slider.disabled = args[1]
        self._property.auto = args[1]


class CameraController(BoxLayout):
    def __init__(self, **kwargs):
        super(CameraController, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.webcam = C920WebCam(0)  # TODO change device number

        self.exposure_ctrl = SimpleAutoModeValueSlider(self.webcam.exposure)
        self.wb_ctrl = SimpleAutoModeValueSlider(self.webcam.white_balance)
        self.focus_ctrl = SimpleAutoModeValueSlider(self.webcam.focus)
        self.zoom_ctrl = SimpleValueSlider(self.webcam.zoom)
        self.gain_ctrl = SimpleValueSlider(self.webcam.gain)
        self.brightness_ctrl = SimpleValueSlider(self.webcam.brightness)
        self.contrast_ctrl = SimpleValueSlider(self.webcam.contrast)
        self.saturation_ctrl = SimpleValueSlider(self.webcam.saturation)
        self.sharpness_ctrl = SimpleValueSlider(self.webcam.sharpness)

        # # ADD Camera controls to screen
        self.camera_controls = self.build_camera_ctrl()
        self.add_widget(self.camera_controls)

    def build_camera_ctrl(self):
        camera_controls = BoxLayout(orientation="vertical")
        camera_controls.add_widget(self.exposure_ctrl)
        camera_controls.add_widget(self.wb_ctrl)
        camera_controls.add_widget(self.focus_ctrl)
        camera_controls.add_widget(self.zoom_ctrl)
        camera_controls.add_widget(self.brightness_ctrl)
        camera_controls.add_widget(self.contrast_ctrl)
        camera_controls.add_widget(self.gain_ctrl)
        camera_controls.add_widget(self.saturation_ctrl)
        camera_controls.add_widget(self.sharpness_ctrl)
        return camera_controls


class CameraAPP(App):
    def build(self):
        return CameraController()


if __name__ == "__main__":
    CameraAPP().run()
