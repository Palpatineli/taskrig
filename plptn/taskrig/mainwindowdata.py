import json

from PyQt5.QtCore import QObject, pyqtSlot

from plptn.taskrig.config import design_list
from plptn.taskrig.device.arduino import list_ports
from plptn.taskrig.mainwindow import default_settings


class MainWindowData(QObject):
    def __init__(self):
        super(MainWindowData, self).__init__()
        self.data = json.load(open(default_settings))
        self.design_types = design_list()
        self.port_list = list_ports()
        self.port = self.port_list[0]

    def __getitem__(self, item):
        return self.data[item]

    @property
    def port_list_str(self):
        return [port.location for port in self.port_list]

    @pyqtSlot(int)
    def set_design_type(self, value: int):
        self.data['design_type'] = self.design_types[value]

    @pyqtSlot(int)
    def set_port(self, value: int):
        self.port = self.port_list[value]

    @pyqtSlot(str)
    def set_file_path(self, value: str):
        self.data['file_path'] = value

    @pyqtSlot(float)
    def set_reward_amount(self, value: float):
        self.data['reward_amount'] = value

    def __del__(self):
        json.dump(self.data, open(default_settings, 'w'))
