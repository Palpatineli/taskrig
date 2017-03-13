from PyQt5.QtCore import QObject

from config import design_list, device_list
from device.arduino import list_ports


class Settings(QObject):
    design_idx = 0
    device_idx = 0
    port_idx = 0

    def __init__(self):
        super(Settings, self).__init__()
        self.design_list = design_list()
        self.device_list = device_list()
        self.port_list = list_ports()

    @property
    def port_list_str(self):
        return [port.location for port in self.port_list]

    @property
    def design_id(self):
        return self.design_list[self.design_idx]

    @property
    def device_id(self):
        return self.device_list[self.device_idx]

    @property
    def port_id(self):
        return self.port_list[self.port_idx]

    @property
    def port_id_str(self):
        return self.port_id.location
