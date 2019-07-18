from PySide2.QtCore import QObject, SIGNAL, SLOT
from PySide2.QtGui import QIcon

from PySide2.QtWidgets import QSystemTrayIcon, QMenu, QAction


class SystemTray(QSystemTrayIcon):
    def __init__(self, parent):
        super().__init__(QIcon("resources/translate-icon.svg"),)
        self.parent = parent
        self.show()

        self.clear_action = QAction("Clear", self)

        self.enable_action = QAction("Enable clipboard translation", self)
        self.enable_action.setCheckable(True)

        self.show_panel_action = QAction("Show panel", self)
        self.show_panel_action.setCheckable(True)

        self.on_top_action = QAction("Always on top", self)
        self.on_top_action.setCheckable(True)

        self.not_fix_action = QAction("Move to avoid mouse", self)
        self.not_fix_action.setCheckable(True)

        close_action = QAction("Exit", self)

        QObject.connect(self.clear_action, SIGNAL("triggered()"),
                        self.parent.clear_button, SLOT("click()"))

        QObject.connect(self.on_top_action, SIGNAL("triggered(bool)"),
                        self.parent, SLOT("set_on_top(bool)"))

        QObject.connect(self.show_panel_action, SIGNAL("triggered(bool)"),
                        self.parent, SLOT("show_interface(bool)"))

        QObject.connect(self.not_fix_action, SIGNAL("triggered(bool)"),
                        self.parent, SLOT("set_not_fix(bool)"))

        QObject.connect(close_action, SIGNAL("triggered()"),
                        self.parent, SLOT("close()"))

        menu = QMenu()
        menu.addActions([
            self.clear_action,
            self.enable_action,
            self.show_panel_action,
            self.on_top_action,
            self.not_fix_action,
            self.show_panel_action,
            close_action])
        self.setContextMenu(menu)

        QObject.connect(menu, SIGNAL("aboutToShow()"),
                        self, SLOT("refresh()"))

    def refresh(self):
        self.enable_action.setChecked(self.parent.is_enable)
        self.on_top_action.setChecked(self.parent.is_on_top)
        self.not_fix_action.setChecked(self.parent.is_not_fixed)
        self.show_panel_action.setChecked(self.parent.is_show_panel)
