# tabs/advanced_tab.py - Minimal version
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QSpinBox
from PyQt5.QtCore import Qt
from PyQt5 import QtCore

class AdvancedTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()

        # Just basic sensitivity control
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setMinimum(10)
        self.sensitivity_slider.setMaximum(200)
        self.sensitivity_slider.setValue(100)
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity)
        self.sensitivity_label = QLabel(f"Sensitivity: {self.sensitivity_slider.value()}%")
        self.layout.addWidget(self.sensitivity_label)
        self.layout.addWidget(self.sensitivity_slider)

        # Basic dead zone control
        self.dead_zone_slider = QSlider(Qt.Horizontal)
        self.dead_zone_slider.setMinimum(50)
        self.dead_zone_slider.setMaximum(300)
        self.dead_zone_slider.setValue(130)
        self.dead_zone_slider.valueChanged.connect(self.update_dead_zone)
        self.dead_zone_label = QLabel(f"Dead Zone: {self.dead_zone_slider.value()}")
        self.layout.addWidget(self.dead_zone_label)
        self.layout.addWidget(self.dead_zone_slider)

        # Poll rate control
        self.poll_rate_slider = QSlider(Qt.Horizontal)
        self.poll_rate_slider.setMinimum(5)    # 5ms = 200Hz
        self.poll_rate_slider.setMaximum(50)   # 50ms = 20Hz
        self.poll_rate_slider.setValue(10)     # 10ms = 100Hz default
        self.poll_rate_slider.valueChanged.connect(self.update_poll_rate)
        self.poll_rate_label = QLabel(f"Poll Rate: {self.poll_rate_slider.value()}ms")
        self.layout.addWidget(self.poll_rate_label)
        self.layout.addWidget(self.poll_rate_slider)

        # Device number control
        self.device_number_spinbox = QSpinBox()
        self.device_number_spinbox.setMinimum(0)
        self.device_number_spinbox.setMaximum(9)  # Support up to 10 devices (0-9)
        self.device_number_spinbox.setValue(3)    # Default to device 3
        self.device_number_label = QLabel(f"Device Number")
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

    def update_sensitivity(self, value):
        self.sensitivity_label.setText(f"Sensitivity: {value}%")

    def update_dead_zone(self, value):
        self.dead_zone_label.setText(f"Dead Zone: {value}")

    def update_poll_rate(self, value):
        self.poll_rate_label.setText(f"Poll Rate: {value}ms")

    def connect_spacemouse(self):
        """Connect to SpaceMouse device"""
        if hasattr(self.parent, 'extension') and self.parent.extension:
            # Update button state
            self.connect_button.setText("Connecting...")
            self.connect_button.setEnabled(False)
            
            try:
                # Set the device number from the spinbox
                device_num = self.device_number_spinbox.value()
                
                self.parent.extension.connect(device_num)
                
                # Update button and parent status
                self.connect_button.setText("Reconnect SpaceMouse")
                self.disconnect_button.setEnabled(True)  # Enable disconnect button
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.setText(f"Connected (Device {device_num})")
                    
            except Exception as e:
                # Handle connection error
                self.connect_button.setText("Connect SpaceMouse")
                self.disconnect_button.setEnabled(False)  # Keep disconnect disabled
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
            # Update button state
            self.disconnect_button.setText("Disconnecting...")
            self.disconnect_button.setEnabled(False)
            
            try:
                # Call the disconnect method on the extension
                self.parent.extension.disconnect()
                
                # Update button states and status
                self.connect_button.setText("Connect SpaceMouse")
                self.disconnect_button.setText("Disconnect SpaceMouse")
                self.disconnect_button.setEnabled(False)  # Disable disconnect button
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.setText("Disconnected")
                    
            except Exception as e:
                # Handle disconnection error
                self.disconnect_button.setText("Disconnect SpaceMouse")
                self.disconnect_button.setEnabled(True)
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.setText(f"Disconnect Error: {e}")
                QtCore.qWarning(f"Disconnection error: {e}")
        else:
            QtCore.qCritical("Extension not available")

    def get_sensitivity(self):
        """Get sensitivity as decimal (0.1 to 2.0)"""
        return self.sensitivity_slider.value() / 100.0
    
    def get_dead_zone(self):
        """Get dead zone as decimal (0.05 to 0.3)"""
        return self.dead_zone_slider.value() / 1000.0
    
    def get_poll_rate(self):
        """Get poll rate in milliseconds"""
        return self.poll_rate_slider.value()