import pyglet


class MyWindow(pyglet.window.Window):
    _text = "Started"
    status = 'still'

    def __init__(self):
        super(MyWindow, self).__init__()
        self.label = pyglet.text.Label(
            self._text, font_name='Arial', font_size=18, x=self.width // 2, y=self.height // 2,
            anchor_x='center', anchor_y='center')
        self.label_2 = pyglet.text.Label(
            self._text, font_name='Arial', font_size=18, x=self.width // 2, y=self.height // 2 + 18,
            anchor_x='center', anchor_y='center')

    def on_draw(self):
        self.clear()
        self.label.draw()
        self.label_2.text = self.status
        self.label_2.draw()

    def on_update(self, _):
        self.status = 'still'

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self._text = new_text
        self.label.text = chr(new_text)

    def on_key_press(self, symbol, _):
        self.text = symbol
        if symbol == ord('q'):
            self.close()
        elif symbol == ord('b'):
            self.dispatch_event('on_lever_push')

    def on_lever_push(self):
        self.status = 'pushed'


def main():
    MyWindow.register_event_type("on_lever_push")
    window = MyWindow()
    pyglet.clock.schedule_interval(window.on_update, 2.0)
    window.dispatch_event('on_lever_push')
    pyglet.app.run()


if __name__ == '__main__':
    main()
