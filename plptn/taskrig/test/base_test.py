import pyglet


class MyWindow(pyglet.window.Window):
    def __init__(self):
        super(MyWindow, self).__init__()
        self._text = "Started"
        self.label = pyglet.text.Label(
            self._text, font_name='Arial', font_size=18, x=self.width // 2, y=self.height // 2,
            anchor_x='center', anchor_y='center')

    def on_draw(self):
        self.clear()
        self.label.draw()

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


def main():
    _ = MyWindow()
    pyglet.app.run()


if __name__ == '__main__':
    main()
