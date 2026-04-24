# SPDX-License-Identifier: GPL-2.0-or-later
import sys
import time

from PyQt5.QtCore import Qt, QTimer, QCoreApplication, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QProgressBar, QDialog, QApplication

from widgets.keyboard_widget import KeyboardWidget
from util import tr


class Unlocker(QDialog):

    def __init__(self, layout_editor, keyboard):
        super().__init__()

        self.setStyleSheet("background-color: {}".format(
            QApplication.palette().color(QPalette.Button).lighter(130).name()))

        self.keyboard = keyboard

        layout = QVBoxLayout()

        self.progress = QProgressBar()

        layout.addWidget(QLabel(tr("Unlocker", "要继续操作，必须将键盘设置为解锁模式.\n"
                                               "此操作只应在您信任的计算机上执行.")))
        layout.addWidget(QLabel(tr("Unlocker", "要退出此模式，您需要重新插拔键盘\n"
                                               "或从菜单中选择“安全”->“锁定”.")))
        layout.addWidget(QLabel(tr("Unlocker", "按住以下按键，直到下方的进度条填满:")))

        self.keyboard_reference = KeyboardWidget(layout_editor)
        self.keyboard_reference.set_enabled(False)
        self.keyboard_reference.set_scale(0.5)
        layout.addWidget(self.keyboard_reference)
        layout.setAlignment(self.keyboard_reference, Qt.AlignHCenter)

        layout.addWidget(self.progress)

        self.setLayout(layout)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)

        self.update_reference()
        self.timer = QTimer()
        self.timer.timeout.connect(self.unlock_poller)
        self.perform_unlock()

    def update_reference(self):
        """ Updates keycap reference image """

        self.keyboard_reference.set_keys(self.keyboard.keys, self.keyboard.encoders)

        # use "active" background to indicate keys to hold
        lock_keys = self.keyboard.get_unlock_keys()
        for w in self.keyboard_reference.widgets:
            if (w.desc.row, w.desc.col) in lock_keys:
                w.setOn(True)

        self.keyboard_reference.update_layout()
        self.keyboard_reference.update()
        self.keyboard_reference.updateGeometry()

    def unlock_poller(self):
        data = self.keyboard.unlock_poll()
        unlocked = data[0]
        unlock_counter = data[2]

        self.progress.setMaximum(max(self.progress.maximum(), unlock_counter))
        self.progress.setValue(self.progress.maximum() - unlock_counter)

        if sys.platform == "emscripten":
            import vialglue
            vialglue.unlock_status(unlock_counter)

        if unlocked == 1:
            if sys.platform == "emscripten":
                import vialglue
                vialglue.unlock_done()

            self.accept()

    def perform_unlock(self):
        self.progress.setMaximum(1)
        self.progress.setValue(0)

        self.keyboard.unlock_start()
        self.timer.start(200)

        if sys.platform == "emscripten":
            import vialglue

            pixmap = self.keyboard_reference.grab()

            # convert QPixmap to bytes
            ba = QByteArray()
            buff = QBuffer(ba)
            buff.open(QIODevice.WriteOnly)
            pixmap.save(buff, "PNG")
            pixmap_bytes = ba.data()

            vialglue.unlock_start(pixmap_bytes, pixmap.width(), pixmap.height())

    @classmethod
    def on_dialog_finished(cls, retval):
        cls.dlg_retval = retval

    @classmethod
    def unlock(cls, keyboard):
        if keyboard.get_unlock_status() == 1:
            return True

        cls.dlg_retval = None
        dlg = cls(cls.global_layout_editor, keyboard)
        dlg.finished.connect(cls.on_dialog_finished)
        cls.global_main_window.lock_ui()
        dlg.setModal(True)
        dlg.show()
        while cls.dlg_retval is None:
            time.sleep(0.05)
            QCoreApplication.processEvents()
        ret = cls.dlg_retval
        cls.global_main_window.unlock_ui()
        return ret

    def keyPressEvent(self, ev):
        """ Ignore all key presses, e.g. Esc should not close the window """
        pass
