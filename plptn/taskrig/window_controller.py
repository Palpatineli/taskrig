from functools import partial
from importlib import import_module
import json
from pkg_resources import resource_filename
from os import path
from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QFileDialog

from plptn.taskrig.settings import Settings
from plptn.taskrig.device.arduino import Arduino
from plptn.taskrig.util.logger import Logger
from plptn.taskrig.mainwindow import MainWindow


def contract_path(file_name: str) -> str:
    home_dir = path.expanduser("~/")
    if file_name.startswith(home_dir):
        file_name = '~/' + file_name[len(home_dir):]
    return file_name


class WindowController(QObject):
    device = None
    device_thread = None
    stop = pyqtSignal(name="stop")

    def __init__(self, ui: MainWindow, basic_settings: Settings):
        super(WindowController, self).__init__()
        self.default_path = resource_filename('plptn.taskrig', 'data/settings.json')
        self.setting = json.load(open(self.default_path))
        self.setting['file_path'] = path.expanduser(self.setting['file_path'])
        self.logger = Logger()
        self.ui = ui
        ui.controller = self
        self.__populate(ui)
        self.__start_device(basic_settings)
        self.__start_controller(basic_settings)
        self.device_thread.start()

    def __populate(self, ui: MainWindow):
        ui.file_path.setText(self.setting['file_path'])
        ui.file_path.textChanged.connect(self.set_file_path)
        ui.browse.released.connect(self.browse_file_path)

    @pyqtSlot(name='browser_file_path')
    def browse_file_path(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self.ui, "Save Log File as...", path.dirname(self.setting['file_path']),
            "Config File (*.json)", options=QFileDialog.Options())
        self.ui.file_path.setText(file_name)

    @pyqtSlot(str, name='set_file_path')
    def set_file_path(self, value: str):
        self.setting['file_path'] = value

    def __start_device(self, basic_settings: Settings):
        self.device = Arduino(basic_settings.device_id, basic_settings.port_id, self.logger)
        self.device_thread = QThread()
        self.device.moveToThread(self.device_thread)
        self.stop.connect(self.device_thread.quit)
        # noinspection PyUnresolvedReferences
        self.device.send_message.connect(self.ui.status_bar.showMessage)
        self.ui.stop_exp.connect(self.device.on_stop)
        self.ui.give_water.connect(partial(self.device.on_give_water, 6.0))
        self.ui.start_water.connect(self.device.on_start_water)
        self.ui.stop_water.connect(self.device.on_stop_water)

    def __start_controller(self, basic_settings: Settings):
        exp_module = import_module("plptn.taskrig.design.{0}".format(basic_settings.design_id))
        # noinspection PyPep8Naming
        Controller = getattr(
            exp_module, "{0}Controller".format(basic_settings.design_id.title()))
        self.controller = Controller(self.setting, self.device, self.logger)
        self.controller.update_result.connect(self.ui.on_update_result)
        self.controller.update_state.connect(self.ui.status_bar.showMessage)
        self.ui.start_exp.connect(self.controller.on_start)
        self.controller.start.connect(self.device.on_start)
        self.ui.stop_exp.connect(self.controller.on_stop)
        self.controller.stop.connect(self.device.on_stop)

    def on_stop(self):
        self.stop.emit()
        self.setting['file_path'] = contract_path(self.setting['file_path'])
        json.dump(self.setting, open(self.default_path, 'w'))
        self.device_thread.wait(1)
