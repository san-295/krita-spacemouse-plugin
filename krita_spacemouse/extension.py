# extension.py - Main SpaceMouse extension controller
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QDockWidget
from PyQt5 import QtCore
from krita import Extension, Krita, DockWidgetFactory, DockWidgetFactoryBase
from .models.spnav import libspnav
from .event_handler import poll_spacenav

class SpacenavControlExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_event_handler)
        self.docker = None

    def setup(self):
        # Create factory function that captures extension reference
        def create_spacenav_docker():
            from .views.docker import SpacenavDocker
            return SpacenavDocker(self)
        
        # Create and register factory
        Krita.instance().addDockWidgetFactory(
            DockWidgetFactory("spacenavDocker", DockWidgetFactoryBase.DockRight, create_spacenav_docker)
        )

    def createActions(self, window):
        # Docker is now created with extension reference, no delayed search needed
        QtCore.qDebug("SpaceMouse extension initialized with direct docker connection")

    def timer_event_handler(self):
        poll_spacenav(self)

    def connect(self, device_num):
        # Connect to SpaceNavigator device directly
        result = libspnav.spnav_open(device_num)  # Use specified device number
        if result == -1:
            QMessageBox.warning(None, "SpaceMouse Error", f"No SpaceMouse device found at device #{device_num}.")
            return

        # Get poll rate from docker if available, otherwise use default
        poll_rate = 30  # Default fallback
        try:
            dockers = Krita.instance().dockers()
            for docker in dockers:
                if docker.objectName() == "spacenavDocker" and hasattr(docker, 'configuration_tab'):
                    poll_rate = docker.configuration_tab.get_poll_rate()
                    break
        except Exception as e:
            QtCore.qDebug(f"Could not get poll rate from docker, using default: {e}")
        
        self.timer.start(poll_rate)

    def disconnect(self):
        if self.timer.isActive():
            self.timer.stop()
        libspnav.spnav_close()

    def stop(self):
        self.disconnect()
