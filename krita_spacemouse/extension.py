# extension.py - Ultra-minimal SpaceMouse extension
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
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
        Krita.instance().addDockWidgetFactory(
            DockWidgetFactory("spacenavDocker", DockWidgetFactoryBase.DockRight, SpacenavDocker)
        )

    def createActions(self, window):
        from PyQt5.QtWidgets import QDockWidget
        self.docker = window.findChild(QDockWidget, "spacenavDocker")
        if self.docker:
            self.docker.set_extension(self)

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