"""set up the main window"""
from os import path

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QMainWindow

from plptn.taskrig.data.ui_mainwindow import Ui_TaskRigMainWindow


class MainWindow(QMainWindow, Ui_TaskRigMainWindow):
    start_exp = pyqtSignal(name="start_exp")
    stop_exp = pyqtSignal(name="stop_exp")
    give_water = pyqtSignal(name="give_water")
    start_water = pyqtSignal(name="start_water")
    stop_water = pyqtSignal(name="stop_water")
    controller = None

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

    @pyqtSlot(bool)
    def on_start_trigger_clicked(self, is_checked: bool):
        if is_checked:
            self.start_exp.emit()
        else:
            self.stop_exp.emit()

    @pyqtSlot(dict)
    def on_update_result(self, new_state: dict):
        self.raw_result.setText("{0:2d}/{1:2d}/{2:2d}".format(
            new_state["hit"], new_state["miss"], new_state["early"]))
        self.progress_bar.setValue(int(round(
            new_state["hit"] / (new_state["hit"] + new_state["miss"] + new_state["early"]) * 100)))
        self.water_given.setText("{0:.2f}".format(new_state["water_given"]))

    @pyqtSlot()
    def on_exp_finished(self):
        self.status_bar.showMessage('exp finished')
        self.start_trigger.isChecked(False)

    # button events
    @pyqtSlot()
    def on_water_button_clicked(self):
        self.give_water.emit()

    @pyqtSlot(bool)
    def on_water_start_clicked(self, is_checked: bool):
        if is_checked:
            self.water_button.setEnabled(False)
            self.start_water.emit()
        else:
            self.stop_water.emit()
            self.water_button.setEnabled(True)

    @pyqtSlot(QCloseEvent)
    def closeEvent(self, x: QCloseEvent):
        if self.controller:
            self.controller.on_stop()
        super(MainWindow, self).closeEvent(x)
