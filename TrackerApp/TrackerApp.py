import kivy

from kivy.app import App
from kivy.app import Builder
from kivy.uix.widget import Widget
import SpheroController as sp


kivy.require("1.7.2")
Builder.load_file("TrackerApp.kv")


class MainScreen(Widget):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)


class TrackerApp(App):
    def build(self):
        return sp.ColorController()

if __name__ == "__main__":
    TrackerApp().run()