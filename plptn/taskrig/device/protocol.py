"""Define the usb serial protocol with arduino for the lever-push chip"""
import enum
from struct import Struct
__all__ = ['SignalType', 'OTHER_SIGNALS', 'SIGNAL_NAME', 'BAUDRATE', 'SEPARATOR', 'SERIAL_SEGMENT', 'PACKET_FMT',
           'PACKET_FMT_S', 'SEND_PACKET_FMT']


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


OTHER_SIGNALS: set = set(SignalType) - {SignalType.LEVER, SignalType.LICK_TOUCH, SignalType.SEND_TTL,
                                        SignalType.SEND_TTL, SignalType.SUPPORT_TOUCH, SignalType.PLAY_SOUND}

SIGNAL_NAME = dict()
for x in OTHER_SIGNALS:
    SIGNAL_NAME[x.value] = x.name

# signaling parameters
BAUDRATE = 115200
SEPARATOR = b'\xff'
SERIAL_SEGMENT = 500
PACKET_FMT = Struct(">xBIi")
PACKET_FMT_S = Struct(">BIi")
SEND_PACKET_FMT = Struct(">BB")
