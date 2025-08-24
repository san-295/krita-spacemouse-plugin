# tabs/connection_tab.py - Connection controls for SpaceMouse
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox, QComboBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5 import QtCore

class ConnectionTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()

        # Device selection dropdown
        self.device_label = QLabel("Select Device:")
        self.layout.addWidget(self.device_label)
        
        # Device refresh and selection layout
        device_layout = QHBoxLayout()
        self.device_combo = QComboBox()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_devices)
        device_layout.addWidget(self.device_combo)
        device_layout.addWidget(self.refresh_button)
        self.layout.addLayout(device_layout)

        # Device number control (for multiple devices of same type)
        self.device_number_spinbox = QSpinBox()
        self.device_number_spinbox.setMinimum(0)
        self.device_number_spinbox.setMaximum(9)  # Support up to 10 devices (0-9)
        self.device_number_spinbox.setValue(0)    # Default to device 0
        self.device_number_label = QLabel("Device Number (if multiple of same type)")
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
        
        # Initialize device list
        self.refresh_devices()

    def refresh_devices(self):
        """Refresh the list of available devices via controller"""
        try:
            # Clear existing items
            self.device_combo.clear()
            
            # Get available devices through the controller
            if hasattr(self.parent, 'extension') and self.parent.extension:
                devices = self.parent.extension.get_available_devices()
                
                if devices:
                    self.device_combo.addItems(devices)
                    self.device_combo.setEnabled(True)
                    self.connect_button.setEnabled(True)
                else:
                    self.device_combo.addItem("No devices found")
                    self.device_combo.setEnabled(False)
                    self.connect_button.setEnabled(False)
            else:
                self.device_combo.addItem("Extension not available")
                self.device_combo.setEnabled(False)
                self.connect_button.setEnabled(False)
                
        except Exception as e:
            QtCore.qWarning(f"Error refreshing devices: {e}")
            self.device_combo.clear()
            self.device_combo.addItem("Error detecting devices")
            self.device_combo.setEnabled(False)
            self.connect_button.setEnabled(False)

    def connect_spacemouse(self):
        """Connect to SpaceMouse device"""
        if hasattr(self.parent, 'extension') and self.parent.extension:
            self.connect_button.setText("Connecting...")
            self.connect_button.setEnabled(False)
            
            try:
                device_num = self.device_number_spinbox.value()
                device_name = self.device_combo.currentText()
                
                # Don't try to connect if no valid device selected
                if device_name == "No devices found" or device_name == "Error detecting devices":
                    raise Exception("No valid device selected")
                
                self.parent.extension.connect(device_num, device_name)
                
                self.connect_button.setText("Reconnect SpaceMouse")
                self.disconnect_button.setEnabled(True)
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.setText(f"Connected to {device_name} (#{device_num})")
                    
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
