# tabs/advanced_tab.py - Advanced controls with separate pan/zoom sensitivity
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QSpinBox
from PyQt5.QtCore import Qt
from PyQt5 import QtCore

class AdvancedTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()

        # Pan sensitivity control
        self.pan_sensitivity_slider = QSlider(Qt.Horizontal)
        self.pan_sensitivity_slider.setMinimum(10)
        self.pan_sensitivity_slider.setMaximum(200)
        self.pan_sensitivity_slider.setValue(100)  # 100% default for optimal feel
        self.pan_sensitivity_slider.valueChanged.connect(self.update_pan_sensitivity)
        self.pan_sensitivity_label = QLabel(f"Pan Sensitivity: {self.pan_sensitivity_slider.value()}%")
        self.layout.addWidget(self.pan_sensitivity_label)
        self.layout.addWidget(self.pan_sensitivity_slider)

        # Zoom sensitivity control
        self.zoom_sensitivity_slider = QSlider(Qt.Horizontal)
        self.zoom_sensitivity_slider.setMinimum(10)
        self.zoom_sensitivity_slider.setMaximum(200)
        self.zoom_sensitivity_slider.setValue(160)  # 160% default for optimal zoom feel
        self.zoom_sensitivity_slider.valueChanged.connect(self.update_zoom_sensitivity)
        self.zoom_sensitivity_label = QLabel(f"Zoom Sensitivity: {self.zoom_sensitivity_slider.value()}%")
        self.layout.addWidget(self.zoom_sensitivity_label)
        self.layout.addWidget(self.zoom_sensitivity_slider)

        # Yaw (rotation) sensitivity control
        self.yaw_sensitivity_slider = QSlider(Qt.Horizontal)
        self.yaw_sensitivity_slider.setMinimum(10)
        self.yaw_sensitivity_slider.setMaximum(200)
        self.yaw_sensitivity_slider.setValue(100)  # 100% default for rotation
        self.yaw_sensitivity_slider.valueChanged.connect(self.update_yaw_sensitivity)
        self.yaw_sensitivity_label = QLabel(f"Rotation Sensitivity: {self.yaw_sensitivity_slider.value()}%")
        self.layout.addWidget(self.yaw_sensitivity_label)
        self.layout.addWidget(self.yaw_sensitivity_slider)

        # Basic dead zone control
        self.dead_zone_slider = QSlider(Qt.Horizontal)
        self.dead_zone_slider.setMinimum(50)    # 5.0% deadzone
        self.dead_zone_slider.setMaximum(300)   # 30.0% deadzone
        self.dead_zone_slider.setValue(130)     # 13.0% default
        self.dead_zone_slider.valueChanged.connect(self.update_dead_zone)
        self.dead_zone_label = QLabel(f"Dead Zone: {self.dead_zone_slider.value() / 10.0}%")
        self.layout.addWidget(self.dead_zone_label)
        self.layout.addWidget(self.dead_zone_slider)

        # Poll rate control
        self.poll_rate_slider = QSlider(Qt.Horizontal)
        self.poll_rate_slider.setMinimum(5)    # 5ms = 200Hz
        self.poll_rate_slider.setMaximum(50)   # 50ms = 20Hz
        self.poll_rate_slider.setValue(30)     # 30ms = 33Hz default
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

    def update_pan_sensitivity(self, value):
        self.pan_sensitivity_label.setText(f"Pan Sensitivity: {value}%")

    def update_zoom_sensitivity(self, value):
        self.zoom_sensitivity_label.setText(f"Zoom Sensitivity: {value}%")

    def update_yaw_sensitivity(self, value):
        self.yaw_sensitivity_label.setText(f"Rotation Sensitivity: {value}%")

    def update_dead_zone(self, value):
        self.dead_zone_label.setText(f"Dead Zone: {value / 10.0}%")

    def update_poll_rate(self, value):
        self.poll_rate_label.setText(f"Poll Rate: {value}ms")
        # Update the extension's timer if it exists
        if hasattr(self.parent, 'extension') and self.parent.extension and hasattr(self.parent.extension, 'timer'):
            self.parent.extension.timer.setInterval(value)

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

    def get_pan_sensitivity(self):
        """Get pan sensitivity as decimal (0.1 to 2.0)"""
        return self.pan_sensitivity_slider.value() / 100.0

    def get_zoom_sensitivity(self):
        """Get zoom sensitivity as decimal (0.1 to 2.0)"""
        return self.zoom_sensitivity_slider.value() / 100.0

    def get_yaw_sensitivity(self):
        """Get yaw (rotation) sensitivity as decimal (0.1 to 2.0)"""
        return self.yaw_sensitivity_slider.value() / 100.0
    
    def get_dead_zone(self):
        """Get dead zone as decimal (0.050 to 0.300)"""
        return self.dead_zone_slider.value() / 1000.0
    
    def get_poll_rate(self):
        """Get poll rate in milliseconds"""
        return self.poll_rate_slider.value()

    # Backwards compatibility method
    def get_sensitivity(self):
        """Backwards compatibility - returns pan sensitivity"""
        return self.get_pan_sensitivity()