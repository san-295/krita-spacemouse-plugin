# tabs/configuration_tab.py - Configuration controls for SpaceMouse
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt
from PyQt5 import QtCore

class ConfigurationTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()

        # Pan scale control (pixels per unit movement)
        self.pan_scale_slider = QSlider(Qt.Horizontal)
        self.pan_scale_slider.setMinimum(20)    # 20 pixels per unit
        self.pan_scale_slider.setMaximum(400)   # 400 pixels per unit
        self.pan_scale_slider.setValue(120)     # 120 pixels default
        self.pan_scale_slider.valueChanged.connect(self.update_pan_scale)
        self.pan_scale_label = QLabel(f"Pan Scale: {self.pan_scale_slider.value()} px/unit")
        self.layout.addWidget(self.pan_scale_label)
        self.layout.addWidget(self.pan_scale_slider)

        # Zoom scale control (zoom percentage per unit movement)
        self.zoom_scale_slider = QSlider(Qt.Horizontal)
        self.zoom_scale_slider.setMinimum(5)     # 0.5% zoom per unit
        self.zoom_scale_slider.setMaximum(100)   # 10.0% zoom per unit
        self.zoom_scale_slider.setValue(32)      # 3.2% default (0.032 factor)
        self.zoom_scale_slider.valueChanged.connect(self.update_zoom_scale)
        self.zoom_scale_label = QLabel(f"Zoom Scale: {self.zoom_scale_slider.value() / 10.0:.1f}% per unit")
        self.layout.addWidget(self.zoom_scale_label)
        self.layout.addWidget(self.zoom_scale_slider)

        # Rotation speed control (degrees per unit movement)
        self.rotation_speed_slider = QSlider(Qt.Horizontal)
        self.rotation_speed_slider.setMinimum(5)     # 0.5 degrees per unit
        self.rotation_speed_slider.setMaximum(100)   # 10.0 degrees per unit
        self.rotation_speed_slider.setValue(25)      # 2.0 degrees default
        self.rotation_speed_slider.valueChanged.connect(self.update_rotation_speed)
        self.rotation_speed_label = QLabel(f"Rotation Speed: {self.rotation_speed_slider.value() / 10.0:.1f} deg/unit")
        self.layout.addWidget(self.rotation_speed_label)
        self.layout.addWidget(self.rotation_speed_slider)

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

        self.layout.addStretch()
        self.setLayout(self.layout)

    def update_pan_scale(self, value):
        self.pan_scale_label.setText(f"Pan Scale: {value} px/unit")

    def update_zoom_scale(self, value):
        self.zoom_scale_label.setText(f"Zoom Scale: {value / 10.0:.1f}% per unit")

    def update_rotation_speed(self, value):
        self.rotation_speed_label.setText(f"Rotation Speed: {value / 10.0:.1f} deg/unit")

    def update_dead_zone(self, value):
        self.dead_zone_label.setText(f"Dead Zone: {value / 10.0}%")

    def update_poll_rate(self, value):
        self.poll_rate_label.setText(f"Poll Rate: {value}ms")
        # Update the extension's timer if it exists
        if hasattr(self.parent, 'extension') and self.parent.extension and hasattr(self.parent.extension, 'timer'):
            self.parent.extension.timer.setInterval(value)

    def get_pan_scale(self):
        """Get pan scale in pixels per unit movement"""
        return self.pan_scale_slider.value()

    def get_zoom_scale(self):
        """Get zoom scale as factor per unit movement"""
        return self.zoom_scale_slider.value() / 1000.0

    def get_rotation_speed(self):
        """Get rotation speed in degrees per unit movement"""
        return self.rotation_speed_slider.value() / 10.0
    
    def get_dead_zone(self):
        """Get dead zone as decimal (0.050 to 0.300)"""
        return self.dead_zone_slider.value() / 1000.0
    
    def get_poll_rate(self):
        """Get poll rate in milliseconds"""
        return self.poll_rate_slider.value()

    # Backwards compatibility methods
    def get_pan_sensitivity(self):
        """Backwards compatibility - returns pan scale / 120 (base scale)"""
        return self.get_pan_scale() / 120.0
        
    def get_zoom_sensitivity(self):
        """Backwards compatibility - returns zoom scale / 0.02 (base scale)"""
        return self.get_zoom_scale() / 0.02
        
    def get_yaw_sensitivity(self):
        """Backwards compatibility - returns rotation speed / 2.0 (base speed)"""
        return self.get_rotation_speed() / 2.0

    def get_sensitivity(self):
        """Backwards compatibility - returns pan sensitivity"""
        return self.get_pan_sensitivity()
