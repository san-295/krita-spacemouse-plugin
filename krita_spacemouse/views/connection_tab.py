# tabs/connection_tab.py - Connection controls for SpaceMouse
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox
from PyQt5.QtCore import Qt
from PyQt5 import QtCore

class ConnectionTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()

        # Device number control
        self.device_number_spinbox = QSpinBox()
        self.device_number_spinbox.setMinimum(0)
        self.device_number_spinbox.setMaximum(9)  # Support up to 10 devices (0-9)
        self.device_number_spinbox.setValue(3)    # Default to device 3
        self.device_number_label = QLabel("Device Number")
        self.layout.addWidget(self.device_number_label)
        self.layout.addWidget(self.device_number_spinbox)

        # Connect button
        self.connect_button = QPushButton("Connect SpaceMouse")
        self.connect_button.clicked.connect(self.connect_spacemouse)
        self.layout.addWidget(self.connect_button)

        # Disconnect button
        self.disconnect_button = QPushButton("Disconnect SpaceMouse")
        self.disconnect_button.clicked.connect(self.disconnect_spacemouse)
        self.disconnect_button.setEnabled(False)  # Initially disabled
        self.layout.addWidget(self.disconnect_button)

        self.layout.addStretch()
        self.setLayout(self.layout)

    def connect_spacemouse(self):
        """Connect to SpaceMouse device"""
        if hasattr(self.parent, 'extension') and self.parent.extension:
            self.connect_button.setText("Connecting...")
            self.connect_button.setEnabled(False)
            
            try:
                device_num = self.device_number_spinbox.value()
                self.parent.extension.connect(device_num)
                
                self.connect_button.setText("Reconnect SpaceMouse")
                self.disconnect_button.setEnabled(True)
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.setText(f"Connected (Device {device_num})")
                    
            except Exception as e:
                self.connect_button.setText("Connect SpaceMouse")
                self.disconnect_button.setEnabled(False)
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.setText(f"Error: {e}")
                QtCore.qWarning(f"Connection error: {e}")
            finally:
                self.connect_button.setEnabled(True)
        else:
            QtCore.qCritical("Extension not available")

    def disconnect_spacemouse(self):
        """Disconnect from SpaceMouse device"""
        if hasattr(self.parent, 'extension') and self.parent.extension:
            self.disconnect_button.setText("Disconnecting...")
            self.disconnect_button.setEnabled(False)
            
            try:
                self.parent.extension.disconnect()
                
                self.connect_button.setText("Connect SpaceMouse")
                self.disconnect_button.setText("Disconnect SpaceMouse")
                self.disconnect_button.setEnabled(False)
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.setText("Disconnected")
                    
            except Exception as e:
                self.disconnect_button.setText("Disconnect SpaceMouse")
                self.disconnect_button.setEnabled(True)
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.setText(f"Disconnect Error: {e}")
                QtCore.qWarning(f"Disconnection error: {e}")
        else:
            QtCore.qCritical("Extension not available")

    def get_device_number(self):
        """Get the selected device number"""
        return self.device_number_spinbox.value()
