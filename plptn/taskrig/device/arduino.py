"""serial communication with arduino"""
from typing import Iterable, Tuple
from itertools import chain
import numpy as np
from serial import Serial
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QObject
from plptn.taskrig.util.logger import Logger
from plptn.taskrig.util.timeseries import despike
from plptn.taskrig.config import DeviceConfig
from plptn.taskrig.device.protocol import *


# process result
LEVER_FLUX = 1
LEVER_RISE = 2
LICKED = 3

DEVICE_NAME = 'Arduino MKRZero'


def list_ports():
    filtered_ports = list()
    for port in comports():
        if port.pid == 32847 and port.vid == 9025:
            filtered_ports.append(port)
    if not filtered_ports:
        raise IOError("please plug in your {0} device!\n".format("Arduino MKRZero"))
    return filtered_ports


def _read_packets(port: Serial) -> Iterable[Tuple]:
    while port.read(1) != SEPARATOR:
        continue
    remaining = port.in_waiting - PACKET_FMT_S.size
    to_read = remaining - remaining % PACKET_FMT.size
    return chain([PACKET_FMT_S.unpack(port.read(PACKET_FMT_S.size))],
                 PACKET_FMT.iter_unpack(port.read(to_read)))


class Arduino(QObject):
    lever_pushed = pyqtSignal(name="lever_pushed")
    lever_fluxed = pyqtSignal(name="lever_fluxed")
    send_message = pyqtSignal(str, name="send_message")
    licked = pyqtSignal(name="licked")
    finished = pyqtSignal(name="finished")
    timer = None

    def __init__(self, device_id: str, port: ListPortInfo, logger: Logger):
        super(Arduino, self).__init__()
        self.logger = logger
        device_cfg = DeviceConfig(device_id)
        logger.config['device'] = device_cfg.to_dict()
        self.port_address = port.location
        self.port = Serial(port=port.device, baudrate=BAUDRATE)
        self.lever_processor = LeverProcessor(device_cfg['lever'])
        self.lick_processor = LickProcessor(device_cfg['lick'])
        self._water_convert = RewardControl(*device_cfg['reward']['time_coef'])
        self.waiting_for_ttl = False

    @pyqtSlot()
    def on_start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.work_once)
        self.port.reset_input_buffer()
        self.timer.start(25)

    @pyqtSlot()
    def work_once(self):
        port = self.port
        logger = self.logger
        if port.in_waiting > SERIAL_SEGMENT:
            signal_types, timestamps, signals = map(np.array, zip(*_read_packets(port)))
            # lever
            lever_mask = signal_types == SignalType.LEVER
            if np.count_nonzero(lever_mask) > 0:
                lever_signal = signals[lever_mask]
                lever_stamp = timestamps[lever_mask]
                logger.lever_stamp.append(lever_stamp)
                logger.lever_signal.append(lever_signal)
                result, lever_event_stamp = self.lever_processor(lever_signal, lever_stamp)
                if result == LEVER_FLUX:
                    self.lever_fluxed.emit()
                elif result == LEVER_RISE:
                    self.lever_pushed.emit()
            lick_mask = signal_types == SignalType.LICK_TOUCH
            if np.count_nonzero(lick_mask) > 0:
                result = self.lick_processor(signals[lick_mask])
                if result == LICKED:
                    self.licked.emit()
            if self.waiting_for_ttl and SignalType.SEND_TTL in signal_types:
                logger.other.append(("SEND_TTL", timestamps[np.argmax(
                    np.equal(signal_types, int(SignalType.SEND_TTL)))]))
            sound_mask = signal_types == SignalType.PLAY_SOUND
            if np.count_nonzero(sound_mask) > 0:
                logger.sound_played.append(signals[sound_mask])
                logger.sound_stamp.append(timestamps[sound_mask])
            for signal_type in OTHER_SIGNALS:
                mask = signal_types == signal_type
                if np.count_nonzero(mask) > 0:
                    logger.other.append((SIGNAL_NAME[signal_type], int(timestamps[mask][0])))

    @pyqtSlot()
    def on_stop(self):
        if self.timer is not None:
            self.timer.stop()
        self.finished.emit()

    @pyqtSlot(float)
    def on_give_water(self, amount: float):
        self.port.write(SEPARATOR + SEND_PACKET_FMT.pack(SignalType.WATER_START,
                                                         self._water_convert(amount)))

    @pyqtSlot()
    def on_start_water(self):
        sent_bytes = SEPARATOR + SEND_PACKET_FMT.pack(SignalType.WATER_START, 0)
        self.port.write(sent_bytes)

    @pyqtSlot()
    def on_reset(self):
        self.port.reset_input_buffer()

    @pyqtSlot()
    def on_stop_water(self):
        self.port.write(SEPARATOR + SEND_PACKET_FMT.pack(SignalType.WATER_END, 0))

    @pyqtSlot(int)
    def on_play_sound(self, sound_id: str):
        self.port.write(SEPARATOR + SEND_PACKET_FMT.pack(SignalType.PLAY_SOUND, SOUND_ID[sound_id]))

    @pyqtSlot()
    def on_give_ttl(self):
        self.port.write(SEPARATOR + SEND_PACKET_FMT.pack(SignalType.SEND_TTL, 0))
        self.waiting_for_ttl = True


class RewardControl(object):
    """convert ml to ms with the reward delivery system in current rig"""
    def __init__(self, linear_coef: float, startup_time: float):
        self.linear_coef = linear_coef
        self.startup_time = startup_time

    def __call__(self, volume):
        return int(self.linear_coef * volume + self.startup_time)


class LeverProcessor(object):
    previous = 0
    baseline = 0

    def __init__(self, lever_config):
        super(LeverProcessor, self).__init__()
        self.min_rise = lever_config['min_rise']
        self.max_flux = lever_config['max_flux']
        self.max_std = lever_config['max_std']

    def __call__(self, trace, timestamps):
        trace = despike(trace)
        max_idx = trace.argmax()
        if trace[max_idx] - self.previous > self.min_rise:
            return_value = LEVER_RISE
        elif abs(trace.mean() - self.previous) > self.max_flux or trace.std() > self.max_std:
            return_value = LEVER_FLUX
        else:
            return_value = 0
        self.previous = trace.mean()
        return return_value, timestamps[max_idx]


class LickProcessor(object):
    def __init__(self, lick_config):
        self.lick_threshold = lick_config['threshold']

    def __call__(self, trace):
        if np.diff(trace).max() > self.lick_threshold:
            return LICKED
        else:
            return 0
