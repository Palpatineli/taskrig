import enum
from struct import Struct


@enum.unique
class SignalType(enum.IntEnum):
    """signal types"""
    WATER_START = 0
    WATER_END = 1
    PLAY_SOUND = 2
    SEND_TTL = 3
    LICK_TOUCH = 0x10
    SUPPORT_TOUCH = 0x11
    LEVER = 0x12


# noinspection PyTypeChecker
OTHER_SIGNALS = set(SignalType) - {SignalType.LEVER, SignalType.LICK_TOUCH, SignalType.SEND_TTL,
                                   SignalType.SEND_TTL, SignalType.SUPPORT_TOUCH, SignalType.PLAY_SOUND}

SIGNAL_NAME = dict()
for x in OTHER_SIGNALS:
    SIGNAL_NAME[x.value] = x.name

# signaling parameters
BAUDRATE = 115200
SEPARATOR = b'\xff'
SOUND_ID = {'start': 0, 'reward': 1, 'punish': 2}
SERIAL_SEGMENT = 500
PACKET_FMT = Struct(">xBIi")
PACKET_FMT_S = Struct(">BIi")
SEND_PACKET_FMT = Struct(">BB")
