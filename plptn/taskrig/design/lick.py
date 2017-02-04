from functools import partial
from PyQt5.QtCore import QStateMachine, pyqtSlot

from plptn.taskrig.controller import Controller, MyState
from plptn.taskrig.config import Design


class LickController(Controller):
    def __init__(self, ui_config):
        super(LickController, self).__init__(ui_config)
        machine = QStateMachine()
        self.design = Design(ui_config.data['design_type'])
        timing = self.design['timing']
        water_amount = ui_config.data['reward_amount']

        inter_trial = MyState(timing['inter_trial'])
        trial = MyState(timing['trial'])
        reward = MyState(timing['reward'])

        trial.entered.connect(partial(self.device.play_sound, 'start'))
        reward.entered.connect(partial(self.device.play_sound, 'reward'))
        reward.entered.connect(partial(self.device.give_water, water_amount))

        inter_trial.addTimedTransition(trial)
        trial.addTimedTransition(inter_trial)
        reward.addTimedTransition(inter_trial)
        inter_trial.addTransition(self.device.licked, inter_trial)
        trial.addTransition(self.device.licked, reward)

        machine.addState(inter_trial)
        machine.addState(trial)
        machine.addState(reward)
        machine.setInitialState(inter_trial)
        self.machine = machine

    @pyqtSlot()
    def on_start_exp(self):
        self.machine.start()

    @pyqtSlot()
    def on_stop_exp(self):
        self.machine.stop()
        super(LickController, self).on_stop_exp()
