# docker.py - Ultra-minimal for SpaceMouse Wireless
from PyQt5.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from .tabs.advanced_tab import AdvancedTab

class SpacenavDocker(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("spacenavDocker")
        self.setWindowTitle("SpaceMouse")
        
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
        self.status_label = QLabel("Ready")
        self.layout.addWidget(self.status_label)
        
    def set_extension(self, extension):
        self.extension = extension
        self.status_label.setText("Connected")
