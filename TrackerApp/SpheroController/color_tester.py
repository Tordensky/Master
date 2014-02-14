from kivy.lang import Builder
from kivy.uix.widget import Widget
from threading import Thread
import sphero

Builder.load_file("SpheroController/color_tester.kv")


class ColorController(Widget):
    def __init__(self, **kwargs):
        super(ColorController, self).__init__(**kwargs)
        self.sphero_handler = sphero.SpheroManager()

        self._update_running = False

    def on_button_click(self, action):
        print action
        self.search_for_nearby_spheros()

    def search_for_nearby_spheros(self):
        if not self._update_running:
            thread = Thread(target=self.sphero_handler._update_nearby_spheros,
                            kwargs={"msg_cb": self._display_msg, "finish_cb": self.on_search_complete})
            thread.start()
        self._update_running = True

    def on_search_complete(self):
        self._update_running = False
        print self.sphero_handler._known_spheros

    def _display_msg(self, msg):
        print msg

if __name__ == "__main__":
    pass
