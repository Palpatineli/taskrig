from functools import partial

from PyQt5.QtCore import pyqtSlot

from plptn.taskrig.controller import Controller
from plptn.taskrig.device.arduino import Arduino
from plptn.taskrig.util.logger import Logger


class LeverpushController(Controller):
    __controller_type = "leverpush"

    def __init__(self, settings: dict, device: Arduino, logger: Logger):
        super(LeverpushController, self).__init__(settings, device, logger)
        self._initialize_design(self.__controller_type)
        water_amount = float(self.design['reward'])
        states = self.states

        states['inter_trial'].entered.connect(device.on_reset)
        states['inter_trial'].addTransition(device.lever_fluxed, states['inter_trial'])
        states['inter_trial'].addTransition(device.lever_pushed, states['inter_trial'])
        states['inter_trial'].addTimedTransition(states['delay'])

        states['delay'].entered.connect(partial(device.on_play_sound, 'start'))
        states['delay'].entered.connect(self.on_new_delay)
        states['delay'].addTransition(device.lever_pushed, states['punish'])
        states['delay'].addTimedTransition(states['trial'])

        states['trial'].entered.connect(self.on_new_trial)
        states['trial'].addTransition(device.lever_pushed, states['reward'])
        states['trial'].addTimedTransition(states['inter_trial'])

        states['reward'].entered.connect(partial(device.on_play_sound, 'reward'))
        states['reward'].entered.connect(self.on_new_reward)
        states['reward'].entered.connect(partial(device.on_give_water, water_amount))
        states['reward'].addTimedTransition(states['inter_trial'])

        states['punish'].entered.connect(partial(device.on_play_sound, 'punish'))
        states['punish'].addTimedTransition(states['inter_trial'])

        self._initialize_machine(self.machine, states)

    @pyqtSlot()
    def on_new_delay(self):
        self.result['early'] += 1
        self.update_result.emit(self.result)

    @pyqtSlot()
    def on_new_trial(self):
        self.result['early'] -= 1
        self.result['miss'] += 1
        self.update_result.emit(self.result)

    @pyqtSlot()
    def on_new_reward(self):
        self.result['miss'] -= 1
        self.result['hit'] += 1
        self.result['water_given'] += self.design['reward']
        self.update_result.emit(self.result)
