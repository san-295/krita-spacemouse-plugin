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

        # Connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_spacemouse)
        self.layout.addWidget(self.connect_button)

        # Disconnect button
        self.disconnect_button = QPushButton("Disconnect")
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
                raw_devices = self.parent.extension.get_available_devices()
                
                if raw_devices:
                    # Format devices for display (UI concern)
                    formatted_devices = self.format_devices_for_display(raw_devices)
                    self.device_combo.addItems(formatted_devices)
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

    def format_devices_for_display(self, raw_devices):
        """Format raw device list for UI display with device numbers when needed"""
        if not raw_devices:
            return []
        
        # Count occurrences of each device name
        device_counts = {}
        for device in raw_devices:
            device_counts[device] = device_counts.get(device, 0) + 1
        
        # Create combined device list with device numbers
        formatted_devices = []
        device_indices = {}
        
        for device in raw_devices:
            # Track current index for this device type
            current_index = device_indices.get(device, 0)
            device_indices[device] = current_index + 1
            
            # If there's only one of this device type, don't show index
            if device_counts[device] == 1:
                formatted_devices.append(device)
            else:
                formatted_devices.append(f"{device} - {current_index}")
        
        return formatted_devices

    def connect_spacemouse(self):
        """Connect to SpaceMouse device"""
        if hasattr(self.parent, 'extension') and self.parent.extension:
            self.connect_button.setText("Connecting...")
            self.connect_button.setEnabled(False)
            
            try:
                device_selection = self.device_combo.currentText()
                
                # Don't try to connect if no valid device selected
                if device_selection == "No devices found" or device_selection == "Error detecting devices":
                    raise Exception("No valid device selected")
                
                # Parse device selection in the view (UI concern)
                device_name, device_number = self.parse_device_selection(device_selection)
                
                # Pass parsed device name and number to controller
                self.parent.extension.connect(device_name, device_number)
                
                self.connect_button.setText("Reconnect")
                self.disconnect_button.setEnabled(True)
                self.update_disconnect_button_text(device_selection)
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.setText(f"Connected to {device_selection}")
                    
            except Exception as e:
                self.connect_button.setText("Connect")
                self.disconnect_button.setEnabled(False)
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.setText(f"Error: {e}")
                QtCore.qWarning(f"Connection error: {e}")
            finally:
                self.connect_button.setEnabled(True)
        else:
            QtCore.qCritical("Extension not available")

    def parse_device_selection(self, device_selection):
        """Parse device selection string into device name and number"""
        if not device_selection:
            return None, 0
            
        # Check if device selection contains " - " indicating device number
        if " - " in device_selection:
            parts = device_selection.rsplit(" - ", 1)  # Split from right, only once
            try:
                device_name = parts[0]
                device_number = int(parts[1])
                return device_name, device_number
            except (ValueError, IndexError):
                # If parsing fails, treat as device name only
                return device_selection, 0
        else:
            # No device number, use 0 as default
            return device_selection, 0

    def update_disconnect_button_text(self, device_selection):
        """Update disconnect button text to show which device will be disconnected"""
        if device_selection and device_selection not in ["No devices found", "Error detecting devices"]:
            self.disconnect_button.setText(f"Disconnect {device_selection}")
        else:
            self.disconnect_button.setText("Disconnect")

    def disconnect_spacemouse(self):
        """Disconnect from SpaceMouse device"""
        if hasattr(self.parent, 'extension') and self.parent.extension:
            self.disconnect_button.setText("Disconnecting...")
            self.disconnect_button.setEnabled(False)
            
            try:
                self.parent.extension.disconnect()
                
                self.connect_button.setText("Connect")
                self.disconnect_button.setText("Disconnect")
                self.disconnect_button.setEnabled(False)
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.setText("Disconnected")
                    
            except Exception as e:
                self.disconnect_button.setText("Disconnect")
                self.disconnect_button.setEnabled(True)
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.setText(f"Disconnect Error: {e}")
                QtCore.qWarning(f"Disconnection error: {e}")
        else:
            QtCore.qCritical("Extension not available")
