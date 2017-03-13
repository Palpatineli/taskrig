from functools import partial
from PyQt5.QtCore import pyqtSlot

from plptn.taskrig.controller import Controller
from plptn.taskrig.device.arduino import Arduino
from plptn.taskrig.util.logger import Logger


class LickController(Controller):
    __controller_type = "lick"

    def __init__(self, settings: dict, device: Arduino, logger: Logger):
        super(LickController, self).__init__(settings, device, logger)
        self._initialize_design(self.__controller_type)
        states = self.states
        water_amount = float(self.design['reward'])

        states['inter_trial'].entered.connect(device.on_reset)
        states['trial'].entered.connect(partial(device.on_play_sound, 'start'))
        states['trial'].entered.connect(self.on_new_trial)
        states['reward'].entered.connect(partial(device.on_play_sound, 'reward'))
        states['reward'].entered.connect(self.on_new_reward)
        states['reward'].entered.connect(partial(device.on_give_water, water_amount))

        states['inter_trial'].addTimedTransition(states['trial'])
        states['trial'].addTimedTransition(states['inter_trial'])
        states['reward'].addTimedTransition(states['inter_trial'])
        states['inter_trial'].addTransition(device.licked, states['inter_trial'])
        states['trial'].addTransition(device.licked, states['reward'])

        self._initialize_machine(self.machine, states)

    @pyqtSlot()
    def on_new_trial(self):
        self.result['miss'] += 1
        self.update_result.emit(self.result)

    @pyqtSlot()
    def on_new_reward(self):
        self.result['miss'] -= 1
        self.result['hit'] += 1
        self.result['water_given'] += self.design['reward']
        self.update_result.emit(self.result)
