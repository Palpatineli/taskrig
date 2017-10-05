from typing import Dict
from functools import partial
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QState, QTimer, QStateMachine

from plptn.taskrig.device.arduino import Arduino
from plptn.taskrig.util.logger import Logger
from plptn.taskrig.config import Design


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
    # signals for device
    stop = pyqtSignal(name='stop')
    start = pyqtSignal(name='start')
    # signals for GUI
    update_result = pyqtSignal(dict, name='update_result')
    update_state = pyqtSignal(str, name='update_state')
    finished = pyqtSignal(name='finished')

    result = {'hit': 0, 'miss': 0, 'early': 0, 'water_given': 0}

    def __init__(self, setting: dict, device: Arduino, logger: Logger):
        super(Controller, self).__init__()
        self.setting = setting
        self.machine = QStateMachine()
        self.device = device
        self.logger = logger
        self.total_trial = 0
        self.total_reward = 0

    def _initialize_design(self, exp_type: str) -> None:
        """sets self.design, self.states"""
        self.design = Design(exp_type)
        self.logger.config['design'] = self.design.to_dict()
        timing = self.design['timing']
        self.states = dict()
        for key, value in timing.items():
            self.states[key] = MyState(value)
            self.states[key].entered.connect(partial(self.on_update_state, key))

    @staticmethod
    def _initialize_machine(machine: QStateMachine, states: Dict[str, MyState]):
        for value in states.values():
            machine.addState(value)
        machine.setInitialState(states['inter_trial'])

    @pyqtSlot()
    def on_start(self):
        self.logger.clear()
        self.machine.start()
        self.start.emit()

    @pyqtSlot()
    def on_stop(self):
        self.stop.emit()
        self.machine.stop()
        self.logger.save(self.setting['file_path'])
        self.finished.emit()

    @pyqtSlot(str)
    def on_update_state(self, msg: str):
        self.update_state.emit(msg)
