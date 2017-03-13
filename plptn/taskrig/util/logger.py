import json
from os.path import expanduser
from datetime import datetime
import numpy as np


class Logger(object):
    log_types = ("lever_signal", "lever_stamp", "sound_played", "sound_stamp")
    config = dict()
    other = list()

    def __init__(self):
        for log_type in self.log_types:
            self.__dict__[log_type] = list()

    def save(self, file_path: str):
        try:
            file = open(file_path, 'w')
        except OSError:
            file = open(expanduser("~/exp-log-{0}.json".format(datetime.now().isoformat())), 'w')
        data = dict()
        for log_type in self.log_types:
            if len(self.__dict__[log_type]) > 0:
                data[log_type] = np.hstack(self.__dict__[log_type]).tolist()
        data['config'] = self.config
        data['stamps'] = self.other
        json.dump(data, file)

    def clear(self):
        for log_type in self.log_types:
            self.__dict__[log_type] = list()
            self.other = list()
