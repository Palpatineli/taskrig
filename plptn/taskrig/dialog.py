from PyQt5.QtWidgets import QDialog

from settings import Settings
from plptn.taskrig.data.ui_dialog import Ui_Dialog


class Dialog(QDialog, Ui_Dialog):
    def __init__(self, settings: Settings):
        super(Dialog, self).__init__()
        self.settings = settings
        self.setupUi(self)
        self.__populate()

    def __populate(self):
        self.port_id.addItems(self.settings.port_list_str)
        self.device_id.addItems(self.settings.device_list)
        self.design_id.addItems(self.settings.design_list)

    def on_button_box_accepted(self):
        self.settings.design_idx = self.design_id.currentIndex()
        self.settings.device_idx = self.device_id.currentIndex()
        self.settings.port_idx = self.port_id.currentIndex()
