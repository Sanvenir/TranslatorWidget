import sys
from time import sleep

from PySide2.QtCore import QThread
from PySide2.QtWidgets import QErrorMessage, QMessageBox

import config_parser
import web_api


class TranslatorThread(QThread):
    def __init__(
            self,
            config: config_parser.Configuration,
            query_method,
            parent=None
    ):
        super().__init__(parent)
        self.config = config
        self.query = query_method
        self.result = None

    def run(self):
        sleep(2)

        app_key = self.config.APP_KEY
        app_secret = self.config.APP_SECRET
        query = self.query()

        if not (app_key and app_secret):
            err_box = QMessageBox(self.parent())
            err_box.setText("Config file is not set correctly")
            err_box.exec_()
            return
        if not query:
            return
        self.result = web_api.connect(
            self.config.APP_KEY, self.config.APP_SECRET, query)
