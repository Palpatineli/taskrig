"""set up the main window"""
import sys
from os import path

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

from plptn.taskrig.data.uiform import Ui_Form
from plptn.taskrig.mainwindowdata import MainWindowData

default_settings = path.join(path.dirname(__file__), 'default.json')


class MainWindow(QMainWindow, Ui_Form):
    stop_exp = pyqtSignal(name="stop_exp")
    give_water = pyqtSignal(dict, str, name="give_water")
    controller = None

    def __init__(self, data: MainWindowData):
        super(MainWindow, self).__init__()
        self.data = data
        self.setupUi(self)
        self.reward_amount.valueChanged.connect(data.set_reward_amount)
        self.design.currentIndexChanged.connect(data.set_design_type)
        self.port.currentIndexChanged.connect(data.set_port)
        self.file_path.textChanged.connect(data.set_file_path)
        self.water_button.setDisabled(True)
        self._populate()

    def _populate(self):
        data = self.data
        self.design.addItems(data.design_types)
        self.design.setCurrentText(data['design_type'])
        self.port.addItems(data.port_list_str)
        self.port.setCurrentText(data.port.location)
        self.reward_amount.setValue(data['reward_amount'])
        self.file_path.setText(data['file_path'])

    @pyqtSlot(bool)
    def on_start_trigger_toggled(self, is_checked: bool):
        if is_checked:
            exp_module = __import__("plptn.taskrig.design.{0}".format(self.data['design_type']),
                                    fromlist=["plptn.taskrig.design"])
            self.controller = exp_module.Controller(self.data)
            self.controller.update_result.connect(self.on_state_change)
            self.controller.update_state.connect(self.statusBar.showMessage)
            self.stop_exp.connect(self.controller.on_stop_exp)
            self.water_button.setEnabled(True)
        else:
            self.stop_exp.emit()
            self.water_button.setEnabled(False)

    @pyqtSlot(dict)
    def on_state_change(self, new_state: dict):
        self.raw_result.setText("{0:2d}/{1:2d}/{2:2d}".format(
            new_state["hit"], new_state["miss"], new_state["early"]))
        self.progress_bar.setValue(int(round(
            new_state["hit"] / (new_state["hit"] + new_state["miss"] + new_state["early"]) * 100)))
        self.water_given.setText("{0:.2f}".format(
            float(self.water_given.text()) + new_state["water_given"]))

    @pyqtSlot()
    def on_exp_finished(self):
        self.start_trigger.setChecked(False)
        self.water_button.setDisabled(True)

    # button events
    @pyqtSlot()
    def on_water_button_clicked(self):
        self.give_water.emit(float(self.reward_amount.text()))
        self.water_given.setText("{0:.2f}".format(float(self.water_given.text()) +
                                                  self.reward_amount.value()))

    @pyqtSlot()
    def on_browse_clicked(self):
        # noinspection PyCallByClass
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Log File as...", path.dirname(self.data['file_path']),
            "Config File (*.json)", options=QFileDialog.options(self))
        self.file_path.setText(file_name)


def main():
    app = QApplication(sys.argv)
    data = MainWindowData()
    window = MainWindow(data)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
