# docker.py - SpaceMouse Docker with tabbed interface
from PyQt5.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel, QTabWidget
from PyQt5.QtCore import Qt
from krita import DockWidget
from .connection_tab import ConnectionTab
from .configuration_tab import ConfigurationTab

class SpacenavDocker(DockWidget):
    def __init__(self, extension=None):
        super().__init__()
        self.setObjectName("spacenavDocker")
        self.setWindowTitle("SpaceMouse")
        
        # Store extension reference directly from constructor
        self.extension = extension
        
        # Main widget
        self.widget = QWidget()
        self.setWidget(self.widget)
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Title
        self.layout.addWidget(QLabel("SpaceMouse Controls"))
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.connection_tab = ConnectionTab(self)
        self.configuration_tab = ConfigurationTab(self)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.connection_tab, "Connection")
        self.tab_widget.addTab(self.configuration_tab, "Configuration")
        
        self.layout.addWidget(self.tab_widget)
        
        # Status
        self.status_label = QLabel("Ready" if not self.extension else "Extension Connected")
        self.layout.addWidget(self.status_label)
        
        # For backwards compatibility, create advanced_tab reference
        self.advanced_tab = self.configuration_tab
    
    def canvasChanged(self, canvas):
        """Required method for canvas observer - called when canvas changes"""
        pass  # We don't need to do anything when canvas changes
        
    def setCanvas(self, canvas):
        """Required method for canvas observer - called when canvas is set"""
        pass  # We don't need to do anything when canvas is set
