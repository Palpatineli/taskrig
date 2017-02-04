"""serial communication with arduino"""
from itertools import chain
from struct import unpack, iter_unpack, pack
from serial import Serial
from serial.tools.list_ports import comports
from scipy.signal import gaussian, convolve
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
from plptn.taskrig.util.logger import Logger
from plptn.taskrig.config import device_config


DEVICE_TYPE = "Arduino MKRZero"
# outgoing
GIVE_WATER = 0x00
STOP_WATER = 0x01
PLAY_SOUND = 0x02
SOUND_ID = {'start': 0, 'reward': 1, 'punish': 2}

# incoming
SERIAL_SEGMENT = 500
PACKET_SIZE = 10
PACKET_FMT = ">xBIi"
PACKET_FMT_S = ">BIi"
SEPARATOR = 0xff
WATER_STAMP = 0x00
SOUND_STAMP = 0x02
TOUCH_CHAN_0 = 0x03
TOUCH_CHAN_1 = 0x04
LEVER = 0x05


def list_ports():
    ports = comports()
    filtered_ports = [port for port in ports if port.description == DEVICE_TYPE]
    if not filtered_ports:
        raise IOError("please plug in your {0} device!\n".format(DEVICE_TYPE))
    return filtered_ports


class Arduino(QObject):
    _instance = None
    buffer_size = 50000
    baudrate = 115200
    lever_pushed = pyqtSignal(name="lever_pushed")
    lever_fluxed = pyqtSignal(name="lever_fluxed")
    licked = pyqtSignal(int, name="licked")
    finished = pyqtSignal(name="finished")
    running = False
    timer = None

    def __init__(self, port_name, logger: Logger):
        device_cfg = device_config()
        super(Arduino, self).__init__()
        self.port_name = port_name
        self.port = Serial(port=port_name, baudrate=self.baudrate)
        self.lever_processor = Lever(device_cfg['lever'], self.lever_pushed, self.lever_fluxed)
        self.lick_processor = Lick(device_cfg['lick'], self.licked)
        water_a, water_b = device_cfg['device_reward']['time_coef']
        self.water_convert = lambda x: water_a * x + water_b
        self.logger = logger

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    @pyqtSlot()
    def on_start_exp(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.work_once)
        self.timer.start(25)

    @pyqtSlot()
    def work_once(self):
        port = self.port
        logger = self.logger
        if port.in_waiting > SERIAL_SEGMENT:
            signal_type, timestamp, signal = zip(*self._read_packets(port))
            lever_mask = signal_type == LEVER
            lick_mask = signal_type == TOUCH_CHAN_0
            sound_mask = signal_type == SOUND_STAMP
            lever_signal = signal[lever_mask]
            lever_stamp = timestamp[lever_mask]
            self.lever_processor.process(lever_signal, lever_stamp)
            logger.lever_signal.append(lever_signal)
            logger.lever_stamp.append(lever_stamp)
            self.lick_processor.process(signal[lick_mask])
            logger.water_stamp.append(timestamp[signal_type == WATER_STAMP])
            logger.sound_played.append(signal[sound_mask])
            logger.sound_stamp.append(timestamp[sound_mask])

    @pyqtSlot()
    def on_stop_exp(self):
        if self.timer:
            self.timer.stop()
        self.finished.emit()

    @staticmethod
    def _read_packets(port: Serial):
        while port.read(1) != SEPARATOR:
            continue
        return chain([unpack(PACKET_FMT_S, port.read(2))],
                     iter_unpack(PACKET_FMT, port.read(port.in_waiting // 3 - 1)))

    @pyqtSlot(int)
    def give_water(self, amount: float):
        self.port.write(pack('>BBB', SEPARATOR, GIVE_WATER, self.water_convert(amount)))

    @pyqtSlot(int)
    def play_sound(self, sound_id: str):
        self.port.write(pack('>BBB', SEPARATOR, PLAY_SOUND, SOUND_ID[sound_id]))


class Lever(object):
    previous = 0
    baseline = 0

    def __init__(self, lever_config, rise_signal, flux_signal):
        super(Lever, self).__init__()
        self.min_rise = lever_config['min_rise']
        self.max_flux = lever_config['max_flux']
        self.max_std = lever_config['max_std']
        self.rise_signal = rise_signal
        self.flux_signal = flux_signal
        self.filter = gaussian(10, 0.3)

    def process(self, trace, timestamps):
        filtered = convolve(trace, self.filter)
        max_idx = filtered.argmax()
        if filtered[max_idx] - self.previous > self.min_rise:
            self.rise_signal.emit(timestamps[max_idx])
        elif trace.mean() - self.previous > self.max_flux and trace.std() > self.max_std:
            self.flux_signal.emit()
        self.previous = trace.mean()


class Lick(object):
    def __init__(self, lick_config, lick_signal):
        self.lick_threshold = lick_config['threshold']
        self.lick_signal = lick_signal

    def process(self, trace):
        if trace.max() > self.lick_threshold:
            self.lick_signal.emit()
