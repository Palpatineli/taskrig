try:
    import serial
except ImportError as e:
    print("PySerial is need for Arduino functionality")
    serial = None
    raise e


class Arduino(object):
    buffer_size = 50000
    baudrate = 115200

    def __init__(self, port_name):
        self.port = serial.Serial(port=port_name, baudrate=self.baudrate)

    def __del__(self):
        # TODO: find out how to turn arduino off
        raise NotImplementedError
