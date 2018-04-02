import sys

from PyQt5.QtWidgets import QApplication, QDialog

from plptn.taskrig.dialog import Dialog
from plptn.taskrig.settings import Settings
from plptn.taskrig.mainwindow import MainWindow
from plptn.taskrig.window_controller import WindowController


def main():
    app = QApplication(sys.argv)
    dialog_data = Settings()
    dialog = Dialog(dialog_data)
    if dialog.exec() == QDialog.Accepted:
        window = MainWindow()
        WindowController(window, dialog_data)
        window.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
