class State(object):
    __name__ = "Error: using State object directly"
    _timeout = 0.0
    timer = 0.0

    def __init__(self, timeout: float):
        self._timeout = timeout

    def on_lever_push(self):
        pass

    def on_lever_flux(self):
        pass

    def on_lick(self):
        pass

    def on_timeout(self):
        pass

    def enter(self):
        self.timer = self._timeout

    def exit(self):
        pass
