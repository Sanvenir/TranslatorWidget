import os
import re
import sys

import PySide2
from PySide2 import QtCore
from PySide2.QtCore import QObject, SIGNAL, SLOT, QFile, QPoint
from PySide2.QtGui import QGuiApplication
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QCheckBox, QFrame, QLabel, QSlider, QMessageBox, QPushButton, QDesktopWidget, \
    QMainWindow

import config_parser
import threads
import web_api
from exceptions import TranslatorException
from system_tray import SystemTray


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            loader = QUiLoader()
            file = QFile(os.path.abspath("forms/MainWindow.ui"))
            file.open(QFile.ReadOnly)
            ui = loader.load(file, self)
            file.close()
            self.setLayout(ui.layout())

            # Components
            self.clipboard = QGuiApplication.clipboard()
            self.desktop = QDesktopWidget()
            self.trans_label = self.findChild(QLabel, "transLabel")
            self.transparent_slider = self.findChild(QSlider, "transparentSlider")
            self.interface_frame = self.findChild(QFrame, "interfaceFrame")
            self.hide_button = self.findChild(QPushButton, "hideButton")
            self.enable_box = self.findChild(QCheckBox, "enableBox")
            self.on_top_box = self.findChild(QCheckBox, "onTopBox")
            self.clear_button = self.findChild(QPushButton, "clearButton")

            self.system_tray = SystemTray(self)

            self.currentScreen = 0
            self.currentPosition = 0

            self.is_on_top = True
            self.is_enable = True
            self.is_show_panel = True
            self.is_not_fixed = True
            self.is_grab = False

            # Instances
            self.config = config_parser.Configuration()
            self.trans_request = web_api.YouDaoRequest(self.config)
            self.translate_thread = threads.TranslatorThread(
                self.config, self.trans_request, self.get_clip_text, self)

            # initialize
            self._initialize()
            # self.trans_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True);

            # register
            QObject.connect(self.enable_box, SIGNAL("stateChanged(int)"),
                            self, SLOT("_set_enabled(int)"))
            QObject.connect(self.on_top_box, SIGNAL("stateChanged(int)"),
                            self, SLOT("_set_on_top(int)"))
            QObject.connect(self.translate_thread, SIGNAL("finished()"),
                            self, SLOT("_translate()"))
            QObject.connect(self.transparent_slider, SIGNAL("valueChanged(int)"),
                            self, SLOT("_set_transparent(int)"))
            QObject.connect(self.clipboard, SIGNAL("dataChanged()"),
                            self, SLOT("translate()"))
            QObject.connect(self.desktop, SIGNAL("resized(int)"),
                            self, SLOT("_set_geometry()"))
            QObject.connect(self.hide_button, SIGNAL("clicked()"),
                            self, SLOT("hide_interface()"))

        except TranslatorException as e:
            err_box = QMessageBox(self.parent())
            err_box.setText(str(e))
            err_box.exec_()
            sys.exit(-1)

    def translate(self):
        assert isinstance(self.trans_label, QLabel)
        if not self.get_clip_text():
            return
        self.trans_label.setText("Translating...")
        if self.translate_thread.isRunning():
            self.translate_thread.exit(self.translate_thread.exec_())
        self.translate_thread.start()

    def update_text(self):
        self.origin_text.setText(self.get_clip_text())

    def get_clip_text(self):
        text = self.clipboard.text()
        text = re.sub(r"[#]+ ", " ", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n", "%linebreak", text)
        text = re.sub(r"[ \n]+", " ", text)
        text = re.sub(r"(%linebreak)+", "\n", text)
        return text

    def mousePressEvent(self, event: PySide2.QtGui.QMouseEvent):
        self.is_grab = True

    def mouseMoveEvent(self, event: PySide2.QtGui.QMouseEvent):
        if not self.is_grab:
            return
        pos = event.screenPos().toPoint()

        currentScreen = self.currentScreen
        for i in range(self.desktop.screenCount()):
            if self.desktop.screenGeometry(i).left() < pos.x() < self.desktop.screenGeometry(i).right():
                currentScreen = i
                break
        if currentScreen != self.currentScreen:
            self.currentScreen = currentScreen
            screen = self.desktop.screenGeometry(currentScreen)
            self.setGeometry(self.x(), screen.top(), self.width(), screen.height())

        if pos.x() < self.geometry().left():
            self.move(self.pos() + QPoint(pos.x() - self.geometry().left(), 0))
        elif pos.x() > self.geometry().right():
            self.move(self.pos() + QPoint(pos.x() - self.geometry().right(), 0))

    def mouseReleaseEvent(self, event: PySide2.QtGui.QMouseEvent):
        self.is_grab = False

    def enterEvent(self, event: PySide2.QtGui.QMouseEvent):
        if self.is_show_panel or not self.is_not_fixed:
            return
        screen = self.desktop.screenGeometry(self.currentScreen)
        if self.currentPosition == 0:
            self.move(screen.right() - self.width() - 100, self.y())
            self.currentPosition = 1
        else:
            self.move(screen.left() + 100, self.y())
            self.currentPosition = 0

    def closeEvent(self, event: PySide2.QtGui.QCloseEvent):
        sys.exit(0)

    def _initialize(self):
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        # self.trans_label.enterEvent = self.mouse_move_in
        self._set_geometry()
        self._set_transparent(self.transparent_slider.value())
        self.set_on_top(True)
        self.set_enable(True)
        self.show_interface(False)
        self.show()

    def _set_geometry(self):
        screen = self.desktop.screenGeometry(self.currentScreen)
        self.setGeometry(
            screen.left(),
            screen.top(),
            max(500, screen.width() // 5),
            screen.height())
        self.move(screen.right() - self.width() - 100, self.y())

    def _translate(self):
        assert isinstance(self.trans_label, QLabel)
        text = self._get_translate()
        self.trans_label.setText(text)
        self.trans_label.setSelection(0, len(text))

    def _get_translate(self):
        result = self.translate_thread.result
        if result is None:
            return "No result"
        return result

    def _set_transparent(self, value):
        self.setWindowOpacity(1 - value / 100)

    def _set_on_top(self, state):
        self.is_on_top = state
        self.hide()
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, state)
        self.show()

    def set_on_top(self, state):
        self.on_top_box.setChecked(state)

    def _set_enabled(self, state):
        assert isinstance(self.enable_box, QCheckBox)
        self.is_enable = state
        self.clipboard.blockSignals(not state)

    def set_enable(self, state):
        self.enable_box.setChecked(state)

    def set_not_fix(self, state):
        self.is_not_fixed = state

    def show_interface(self, state):
        assert isinstance(self.interface_frame, QFrame)
        self.is_show_panel = state
        if state:
            self.interface_frame.show()
        else:
            self.interface_frame.hide()

    def hide_interface(self):
        self.show_interface(False)