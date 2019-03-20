#############################################################################
##
## Copyright (C) 2016 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################
import re
import sys

import PySide2
from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import QFile, SIGNAL, SLOT, QObject, QPoint
from PySide2.QtGui import QGuiApplication
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QTextEdit, QMessageBox, QCheckBox, QSlider, QApplication, QLabel, QFrame, \
    QDesktopWidget

import config_parser
import threads
import web_api
from exceptions import TranslatorException


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            loader = QUiLoader()
            file = QFile("forms/MainWindow.ui")
            file.open(QFile.ReadOnly)
            ui = loader.load(file, self)
            file.close()
            self.setLayout(ui.layout())

            # Components
            self.clipboard = QGuiApplication.clipboard()
            self.desktop = QDesktopWidget()
            self.origin_text = self.findChild(QTextEdit, "originEdit")
            self.trans_label = self.findChild(QLabel, "transLabel")
            self.enable_box = self.findChild(QCheckBox, "enableBox")
            self.on_top_box = self.findChild(QCheckBox, "onTopBox")
            self.transparent_slider = self.findChild(QSlider, "transparentSlider")
            self.show_box = self.findChild(QCheckBox, "showBox")
            self.interface_frame = self.findChild(QFrame, "interfaceFrame")

            # Instances
            self.config = config_parser.Configuration()
            self.trans_request = web_api.YouDaoRequest(self.config)
            self.translate_thread = threads.TranslatorThread(
                self.config, self.trans_request, self.get_origin_text, self)

            assert isinstance(self.trans_label, QLabel)
            assert isinstance(self.origin_text, QTextEdit)
            assert isinstance(self.enable_box, QCheckBox)
            assert isinstance(self.on_top_box, QCheckBox)
            assert isinstance(self.transparent_slider, QSlider)
            assert isinstance(self.show_box, QCheckBox)
            assert isinstance(self.interface_frame, QFrame)

            # initialize
            self._initialize()

            # register
            QObject.connect(self.enable_box, SIGNAL("stateChanged(int)"),
                            self, SLOT("_set_enabled()"))
            QObject.connect(self.on_top_box, SIGNAL("stateChanged(int)"),
                            self, SLOT("_set_on_top()"))
            QObject.connect(self.origin_text, SIGNAL("textChanged()"),
                            self, SLOT("translate()"))
            QObject.connect(self.translate_thread, SIGNAL("finished()"),
                            self, SLOT("_translate()"))
            QObject.connect(self.transparent_slider, SIGNAL("valueChanged(int)"),
                            self, SLOT("_set_transparent()"))
            QObject.connect(self.clipboard, SIGNAL("dataChanged()"),
                            self, SLOT("update_text()"))
            QObject.connect(self.show_box, SIGNAL("stateChanged(int)"),
                            self, SLOT("_show_interface()"))
            QObject.connect(self.desktop, SIGNAL("resized(int)"),
                            self, SLOT("_set_geometry()"))

            # Properties
            self.is_grab = False

        except TranslatorException as e:
            err_box = QMessageBox(self.parent())
            err_box.setText(str(e))
            err_box.exec_()
            sys.exit(-1)

    def get_origin_text(self):
        return self.origin_text.toPlainText()

    def translate(self):
        assert isinstance(self.trans_label, QLabel)
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

    def mousePressEvent(self, event:PySide2.QtGui.QMouseEvent):
        self.is_grab = True

    def mouseMoveEvent(self, event:PySide2.QtGui.QMouseEvent):
        if not self.is_grab:
            return
        pos = event.screenPos().toPoint()
        if pos.x() < self.geometry().left():
            self.move(self.pos() + QPoint(pos.x() - self.geometry().left(), 0))
        elif pos.x() > self.geometry().right():
            self.move(self.pos() + QPoint(pos.x() - self.geometry().right(), 0))
        # if pos.y() > self.geometry().bottom():
        #     self.move(self.pos() + QPoint(0, pos.y() - self.geometry().bottom()))
        # elif pos.y() < self.geometry().top():
        #     self.move(self.pos() + QPoint(0, pos.y() - self.geometry().top()))

    def mouseReleaseEvent(self, event:PySide2.QtGui.QMouseEvent):
        self.is_grab = False

    def closeEvent(self, event: PySide2.QtGui.QCloseEvent):
        app.exit()

    def _show_interface(self):
        assert isinstance(self.show_box, QCheckBox)
        assert isinstance(self.interface_frame, QFrame)
        if self.show_box.isChecked():
            self.interface_frame.show()
        else:
            self.interface_frame.hide()

    def _initialize(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self._set_geometry()
        self._set_enabled()
        self._set_on_top()
        self._set_transparent()
        self._show_interface()
        self.show()

    def _set_geometry(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, max(500, screen.width() // 5), screen.height())

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

    def _set_transparent(self):
        assert isinstance(self.transparent_slider, QSlider)
        self.setWindowOpacity(1 - self.transparent_slider.value() / 100)

    def _set_on_top(self):
        assert isinstance(self.on_top_box, QCheckBox)
        self.hide()
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, self.on_top_box.isChecked())
        self.show()

    def _set_enabled(self):
        assert isinstance(self.enable_box, QCheckBox)
        self.clipboard.blockSignals(not self.enable_box.isChecked())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
