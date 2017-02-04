from typing import List, Union

from PyQt5.QtWidgets import QWidget

from plptn.taskrig.util.statemachine import State


class StimlessWindow(QWidget):
    def __init__(self):
        super(StimlessWindow, self).__init__()
        self._text = "start"
        self.label = pyglet.text.Label(
            self._text, font_name='Arial', font_size=18, x=self.width // 2, y=self.height // 2,
            anchor_x='center', anchor_y='center')

        self.states = {state.__name__: state for state in states}
        self.state = self.states['start']
        self.state.enter()
        self.__init_ui__()

    def __init_ui__(self):
        self.resize(100, 150)
        self.move(300, 300)
        self.setWindowTitle()

    def _step(self, state: Union[None, str]):
        if state is not None:
            self.state.exit()
            self.state = self.states[state]
            # self.text = state
            self.state.enter()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text_in):
        self._text = text_in
        self.label.text = text_in

    def on_lick(self):
        result = self.state.on_lick()
        self._step(result)

    def on_lever_push(self):
        result = self.state.on_lever_push()
        self._step(result)

    def on_lever_flux(self):
        result = self.state.on_lever_flux()
        self._step(result)

    def tick(self, dt):
        self.state.timer -= dt
        if self.state.timer > 0:
            return
        result = self.state.on_timeout()
        self._step(result)

    def on_key_release(self, symbol, modifier):
        del modifier
        if symbol == ord('q'):
            self.close()
        elif symbol == ord('b'):
            self.dispatch_event('on_lick')

    def on_draw(self):
        self.clear()
        self.label.draw()


StimlessWindow.register_event_type("on_lever_push")
StimlessWindow.register_event_type("on_lever_flux")
StimlessWindow.register_event_type("on_lick")
