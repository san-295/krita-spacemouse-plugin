# docker.py - Ultra-minimal for SpaceMouse Wireless
from PyQt5.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from krita import DockWidget
from .tabs.advanced_tab import AdvancedTab

class SpacenavDocker(DockWidget):
    _extension_instance = None  # Class variable to store extension reference
    
    def __init__(self, extension=None):
        super().__init__()
        self.setObjectName("spacenavDocker")
        self.setWindowTitle("SpaceMouse")
        
        # Get extension from parameter or class variable
        self.extension = extension or SpacenavDocker._extension_instance
        
        # Main widget
        self.widget = QWidget()
        self.setWidget(self.widget)
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Just basic settings - no tabs
        self.layout.addWidget(QLabel("SpaceMouse Controls"))
        
        self.advanced_tab = AdvancedTab(self)
        self.layout.addWidget(self.advanced_tab)
        
        # Status
        self.status_label = QLabel("Ready" if not self.extension else "Connected")
        self.layout.addWidget(self.status_label)
    
    def canvasChanged(self, canvas):
        """Required method for canvas observer - called when canvas changes"""
        pass  # We don't need to do anything when canvas changes
        
    def setCanvas(self, canvas):
        """Required method for canvas observer - called when canvas is set"""
        pass  # We don't need to do anything when canvas is set
        
    def set_extension(self, extension):
        """Legacy method for backward compatibility"""
        self.extension = extension
        self.status_label.setText("Connected")
