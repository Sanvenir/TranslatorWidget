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

import json
import sys

from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import QFile, SIGNAL, SLOT, QObject
from PySide2.QtGui import QGuiApplication
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QTextEdit

import config_parser
import threads


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loader = QUiLoader()
        file = QFile("forms/MainWindow.ui")
        file.open(QFile.ReadOnly)
        ui = loader.load(file, self)
        file.close()
        self.setLayout(ui.layout())

        # Components
        self.clipboard = QGuiApplication.clipboard()
        self.origin_text = self.findChild(QTextEdit, "originEdit")
        self.trans_text = self.findChild(QTextEdit, "transEdit")
        self.config = config_parser.Configuration()
        self.translate_thread = threads.TranslatorThread(self.config, self._get_origin_text, self)

        assert isinstance(self.trans_text, QTextEdit)
        assert isinstance(self.origin_text, QTextEdit)

        # initialize
        self._initialize()

        # register
        QObject.connect(self.origin_text, SIGNAL("textChanged()"),
                        self, SLOT("translate()"))
        QObject.connect(self.clipboard, SIGNAL("dataChanged()"),
                        self, SLOT("_update_text()"))
        QObject.connect(self.translate_thread, SIGNAL("finished()"),
                        self, SLOT("_translate()"))

    def _get_origin_text(self):
        return self.origin_text.toPlainText()

    def translate(self):
        self.trans_text.setText("Translating...")
        if self.translate_thread.isRunning():
            self.translate_thread.exit(self.translate_thread.exec_())
        self.translate_thread.start()

    def _translate(self):
        self.trans_text.setText(self._get_translate())

    def _get_translate(self):
        if self.translate_thread.result is None:
            return "No result"
        result = self.translate_thread.result
        result = json.loads(result, encoding="utf8")
        if not result.get("translation"):
            self.trans_text.setText("No result")
            return "No result"
        return result.get("translation")[0]

    def _initialize(self):
        self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.WindowStaysOnTopHint)

    def _update_text(self):
        self.origin_text.setText(self.get_clip_text())

    def get_clip_text(self):
        text = self.clipboard.text()
        text = " ".join(text.split())
        return text


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
