import pyglet
from plptn.taskrig.device.input import LeverInput
from plptn.taskrig.device.output import WaterReward
from plptn.taskrig.util.sound import QuickSound

from plptn.taskrig.config import device_config, Design
from plptn.taskrig.util.stimless_window import StimlessWindow, State


class Start(State):
    __name__ = 'start'

    def enter(self):
        self.timer = 0.25

    def on_timeout(self):
        return "inter_trial"


class InterTrial(State):
    __name__ = 'inter_trial'

    def on_timeout(self):
        return "delay"

    def on_lever_flux(self):
        return "inter_trial"

    def on_lever_push(self):
        return "inter_trial"


class Delay(State):
    __name__ = 'delay'

    def __init__(self, timeout: float, sound: QuickSound):
        super(Delay, self).__init__(timeout)
        self.sound = sound

    def enter(self):
        super(Delay, self).enter()
        self.sound.play('start')

    def on_lever_push(self):
        return 'punish'

    def on_timeout(self):
        return 'trial'


class Trial(State):
    __name__ = 'trial'

    def on_lever_push(self):
        return "reward"

    def on_timeout(self):
        return "inter_trial"


class Reward(State):
    __name__ = 'reward'

    def __init__(self, timeout: float, sound: QuickSound, water_reward: WaterReward):
        super(Reward, self).__init__(timeout)
        self.sound = sound
        self.reward = water_reward

    def enter(self):
        super(Reward, self).enter()
        self.sound.play('reward')
        self.reward.trigger()

    def on_timeout(self):
        return "inter_trial"


class Punish(State):
    __name__ = 'punish'

    def __init__(self, timeout: float, sound: QuickSound):
        super(Punish, self).__init__(timeout)
        self.sound = sound

    def enter(self):
        super(Punish, self).enter()
        self.sound.play('punish')

    def on_timeout(self):
        return "inter_trial"


def main():
    device = device_config()
    design = Design('lever_push')
    sounds = QuickSound(design['sound_file'])
    reward = WaterReward(device['reward'], 6)
    timing = design['timing']
    states = [Start(0.25),
              InterTrial(timing['inter_trial']),
              Delay(timing['delay'], sounds),
              Trial(timing['trial']),
              Reward(timing['reward'], sounds, reward),
              Punish(timing['punish'], sounds)]
    window = StimlessWindow(states)
    pyglet.clock.schedule(window.tick, 0.1)
    lever = LeverInput(window, device['lever'])
    lever.StartTask()
    pyglet.app.run()


if __name__ == '__main__':
    main()
