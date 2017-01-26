from typing import Sequence

import PyDAQmx as Daq
import numpy as np


class DaqDigitalOut(object):
    def __init__(self, params):
        if isinstance(params, Sequence):
            channel_name = ["{board_name}/port{port}/line{line}".format(**param) for param in
                            params]
            self.channel_no = len(params)
        elif isinstance(params, dict):
            channel_name = "{board_name}/port{port}/line{line}".format(**params)
            self.channel_no = 1
        else:
            raise ValueError("params has to be dict or list of dicts")
        self.task = Daq.Task()
        self.task.CreateDOChan(channel_name, "", Daq.DAQmx_Val_ChanForAllLines)
        self.bit0 = np.zeros((self.channel_no,), dtype=np.uint8)
        self.bit1 = np.ones((self.channel_no,), dtype=np.uint8)

    def start(self):
        self.task.StartTask()

    def __del__(self):
        self.task.WriteDigitalLine(1, True, 1.0, Daq.DAQmx_Val_GroupByChannel, self.bit0, None,
                                   None)  # reset line to low
        self.task.StopTask()
        self.task.ClearTask()


class WaterReward(DaqDigitalOut):
    def __init__(self, params: dict, water_amount: float):
        super(WaterReward, self).__init__(params)
        coef = params['time_coef']
        time = water_amount * coef[0] + coef[1]
        self.sequence = np.zeros(int(round(time)) + 1, dtype=np.uint8)
        self.sequence[-1] = 0
        self.task.CfgSampClkTiming(None, 1000.0, Daq.DAQmx_Val_Rising, Daq.DAQmx_Val_FiniteSamps,
                                   len(self.sequence))

    def trigger(self):
        self.task.WriteDigitalLines(len(self.sequence), True, 0.1, Daq.DAQmx_Val_GroupByChannel,
                                    self.sequence, None, None)
