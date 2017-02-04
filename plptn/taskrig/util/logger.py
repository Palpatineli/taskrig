import json
from os.path import expanduser
from datetime import datetime
import numpy as np


class Logger(object):
    lever_signal = list()
    lever_stamp = list()
    water_stamp = list()
    sound_played = list()
    sound_stamp = list()
    config = dict()

    def save(self, file_path: str):
        try:
            file = open(file_path, 'w')
        except OSError:
            file = open(expanduser("~/exp-log-{0}.json".format(datetime.now().isoformat())), 'w')
        data = {'lever': np.vstack([np.hstack(self.lever_stamp), np.hstack(self.lever_signal)]),
                'water': np.hstack(self.water_stamp),
                'sound': np.vstack([np.hstack(self.sound_stamp), np.hstack(self.sound_played)]),
                'config': self.config}
        json.dump(data, file)

    def clear(self):
        self.lever_signal = list()
        self.lever_stamp = list()
        self.water_stamp = list()
        self.sound_played = list()
        self.sound_stamp = list()
