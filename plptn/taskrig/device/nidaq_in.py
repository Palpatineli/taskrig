from typing import Dict, Union

import PyDAQmx as Daq
import numpy as np
from PyDAQmx import Task
from scipy.signal import gaussian, convolve


class LeverInput(Task):
    channel_no = 2
    baseline = 0
    previous = 0
    lever_data = list()
    licker_data = list()

    def __init__(self, parent_window, device_config: Dict[str, Union[str, int]]):
        super(LeverInput, self).__init__()
        self.parent_window = parent_window
        self.sample_rate = device_config['sample_rate']
        self.batch_size = self.sample_rate // device_config['poll_rate']
        self.buffer = np.zeros(self.batch_size * self.channel_no)
        self.CreateAIVoltageChan(
            "{0}/ai0:{1}".format(device_config['board_name'], self.channel_no - 1), "",
            Daq.DAQmx_Val_Cfg_Default, 0, 5.0, Daq.DAQmx_Val_Volts, None)
        self.CfgSampClkTiming("", self.sample_rate, Daq.DAQmx_Val_Rising, Daq.DAQmx_Val_ContSamps,
                              self.batch_size * 2)
        self.AutoRegisterEveryNSamplesEvent(Daq.DAQmx_Val_Acquired_Into_Buffer, self.batch_size, 0)
        self.filter = gaussian(10, 0.3)
        self.min_rise = device_config['lever']['min_rise']
        self.max_flux = device_config['lever']['max_flux']
        self.max_std = device_config['lever']['max_std']
        self.lick_threshold = device_config['lick']['threshold']

    # noinspection PyPep8Naming
    def EveryNCallback(self) -> int:
        read_sample_no = Daq.int32()
        self.ReadAnalogF64(self.batch_size, 1.0, Daq.DAQmx_Val_GroupByChannel, self.buffer,
                           self.batch_size * self.channel_no, Daq.byref(read_sample_no), None)
        if read_sample_no == 0:
            return 0
        self.lever_data.append(self.buffer[0: self.batch_size].copy())
        self.licker_data.append(self.buffer[self.batch_size:].copy())
        self._process_licker(self.lever_data[-1])
        self._process_lever(self.licker_data[-1])
        return 0  # The function should return an integer

    def _process_lever(self, time_series: np.ndarray):
        if convolve(time_series, self.filter).max() - self.previous > self.min_rise:
            self.parent_window.dispatch_event('on_lever_push')
        elif time_series.mean() - self.previous > self.max_flux \
            and time_series.std() > self.max_std:
            self.parent_window.dispatch_event('on_lever_flux')
        self.previous = time_series.mean()

    def _process_licker(self, time_series: np.ndarray):
        if time_series.max() > self.lick_threshold:
            self.parent_window.dispatch_event('on_lick')

    @property
    def data(self):
        return np.hstack(self.lever_data), np.hstack(self.licker_data)

    def __del__(self):
        self.StopTask()
        self.ClearTask()
        super(LeverInput, self).__del__()
