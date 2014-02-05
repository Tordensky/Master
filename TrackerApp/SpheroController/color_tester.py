from kivy.lang import Builder
from kivy.uix.widget import Widget
import random
import sphero

Builder.load_file("SpheroController/color_tester.kv")


class ColorController(Widget):
    def __init__(self, **kwargs):
        super(ColorController, self).__init__(**kwargs)
        self.sphero = None

    def find_nearby_spheros(self):
        self.sphero = sphero.Sphero()
        self.sphero.connect_all_spheros()

    def connect_to_all_spheros(self):
        self.sphero.connect_all_spheros()

    def sphero_flash(self):
        self.sphero.set_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


if __name__ == "__main__":
    pass
