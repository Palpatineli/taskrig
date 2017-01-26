import pyglet

from plptn.taskrig.config import device_config, Design
from plptn.taskrig.device.nidaq_in import LeverInput
from plptn.taskrig.device.nidaq_out import WaterReward
from plptn.taskrig.device.sound import QuickSound
from plptn.taskrig.util.stimless_window import StimlessWindow, State


class Start(State):
    __name__ = 'start'

    def on_timeout(self):
        return "inter_trial"


class InterTrial(State):
    __name__ = 'inter_trial'

    def on_lick(self):
        return "inter_trial"

    def on_timeout(self):
        return "trial"


class Trial(State):
    __name__ = 'trial'

    def __init__(self, timeout: float, sound: QuickSound):
        super(Trial, self).__init__(timeout)
        self.sound = sound

    def enter(self):
        super(Trial, self).enter()
        self.sound.play('start')

    def on_lick(self):
        return "reward"

    def on_timeout(self):
        return "inter_trial"


class Reward(State):
    __name__ = 'reward'

    def __init__(self, timeout: float, sound: QuickSound, reward: WaterReward):
        super(Reward, self).__init__(timeout)
        self.sound = sound
        self.reward = reward

    def enter(self):
        super(Reward, self).enter()
        self.sound.play('reward')
        self.reward.trigger()

    def on_timeout(self):
        return "inter_trial"


def main():
    device = device_config()
    design = Design('lick')
    sounds = QuickSound(design['sound_file'])
    water_reward = WaterReward(device["reward"], 6)
    timing = design['timing']
    states = [Start(0.25),
              InterTrial(timing['inter_trial']),
              Trial(timing['trial'], sounds),
              Reward(timing['reward'], sounds, water_reward)]
    window = StimlessWindow(states)
    pyglet.clock.schedule_interval(window.tick, 0.1)
    lever = LeverInput(window, device['lever'])
    lever.StartTask()
    pyglet.app.run()


if __name__ == '__main__':
    main()
