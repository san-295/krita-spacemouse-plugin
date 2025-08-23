# extension.py - Ultra-minimal SpaceMouse extension
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QDockWidget
from PyQt5 import QtCore
from krita import Extension, Krita, DockWidgetFactory, DockWidgetFactoryBase
from .spnav import libspnav
from .docker import SpacenavDocker
from .event_handler import poll_spacenav

class SpacenavControlExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_event_handler)
        self.docker = None

    def setup(self):
        # Set extension class variable so docker can find it
        SpacenavDocker._extension_instance = self
        
        # Create and register factory
        Krita.instance().addDockWidgetFactory(
            DockWidgetFactory("spacenavDocker", DockWidgetFactoryBase.DockRight, SpacenavDocker)
        )

    def createActions(self, window):
        # Docker will already have extension reference, just find it
        def delayed_docker_search():
            dockers = Krita.instance().dockers()
            for docker in dockers:
                if docker.objectName() == "spacenavDocker":
                    self.docker = docker
                    QtCore.qDebug("SpaceMouse docker successfully found and linked")
                    break
        
        QTimer.singleShot(100, delayed_docker_search)

    def timer_event_handler(self):
        poll_spacenav(self)

    def connect(self, device_num):
        if self.docker and hasattr(self.docker, 'advanced_tab'):
            # Try to connect to SpaceNavigator device directly
            result = libspnav.spnav_open(device_num)  # Use specified device number
            if result == -1:
                QMessageBox.warning(None, "SpaceMouse Error", f"No SpaceMouse device found at device #{device_num}.")
                return

            self.timer.start(self.docker.advanced_tab.get_poll_rate())

    def disconnect(self):
        if self.timer.isActive():
            self.timer.stop()
        libspnav.spnav_close()

    def stop(self):
        self.disconnect()
