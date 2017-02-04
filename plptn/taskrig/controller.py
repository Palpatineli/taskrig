from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QState, QTimer

from plptn.taskrig.mainwindowdata import MainWindowData
from plptn.taskrig.device.arduino import Arduino
from plptn.taskrig.util.logger import Logger


class MyState(QState):
    def __init__(self, msec: int):
        super(MyState, self).__init__()
        self.timer = QTimer(self)
        self.timer.setInterval(msec)
        self.timer.setSingleShot(True)
        self.entered.connect(self.timer.start)

    def addTimedTransition(self, target: QState):
        self.addTransition(self.timer.timeout, target)


class Controller(QObject):
    finished = pyqtSignal(name="finished")
    stop_exp = pyqtSignal(name="stop_exp")
    update_result = pyqtSignal(dict, name="state_changed")
    update_state = pyqtSignal(str, name="state_changed")
    logger = Logger()
    config = dict()

    def __init__(self, ui_config: MainWindowData):
        super(Controller, self).__init__()
        self.config = ui_config
        self.device = Arduino.get_instance(ui_config.port, self.logger)
        """:type: Arduino"""
        thread = QThread()
        self.device.moveToThread(thread)
        thread.started.connect(self.device.on_start_exp)
        self.device.finished.connect(thread.quit)
        self.device.finished.connect(self.on_finished)
        thread.finished.connect(self.on_finished)
        self.stop_exp.connect(self.device.on_stop_exp)
        thread.start()

    @pyqtSlot(dict)
    def on_start_exp(self):
        raise NotImplementedError

    @pyqtSlot(str)
    def on_stop_exp(self):
        self.stop_exp.emit()
        self.logger.save(self.config.data['file_path'])

    @pyqtSlot()
    def on_finished(self):
        self.finished.emit()

    @pyqtSlot(float)
    def on_give_water(self, water_dose: float):
        Arduino.get_instance(self.config.port.device, self.logger).give_water(water_dose)
