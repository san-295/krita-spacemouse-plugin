"""
SpaceMouse device adapter for Krita SpaceMouse plugin.
Provides interface between spacenavigator library and the plugin.
"""

import spacenavigator
from PyQt5 import QtCore

# Constants for event types
MOTION_EVENT = 1
BUTTON_EVENT = 2

class SpaceMouseMotionEvent:
    """Motion event data structure"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.rx = 0
        self.ry = 0
        self.rz = 0
        self.period = 0

class SpaceMouseButtonEvent:
    """Button event data structure"""
    def __init__(self):
        self.bnum = 0
        self.press = 0

class SpaceMouseEventUnion:
    """Union for different event types"""
    def __init__(self):
        self.motion = SpaceMouseMotionEvent()
        self.button = SpaceMouseButtonEvent()

class SpaceMouseEvent:
    """SpaceMouse event wrapper"""
    def __init__(self):
        self.type = 0
        self.event = SpaceMouseEventUnion()

class SpaceMouseAdapter:
    """Adapter that provides interface for SpaceMouse devices"""
    def __init__(self):
        # Global variables for device state
        self._spacemouse_device = None
        self._last_state = None
        self._button_states = {}

    def open_device(self, device_number=0, device_name=None):
        """Open connection to SpaceMouse device"""
        try:
            self._spacemouse_device = spacenavigator.open(DeviceNumber=device_number, device=device_name)
            if self._spacemouse_device:
                QtCore.qDebug("Connected to SpaceMouse device")
                return 0  # Success
            else:
                QtCore.qWarning("No SpaceMouse device found")
                return -1  # Failure
        except Exception as e:
            QtCore.qCritical(f"Error opening SpaceMouse: {e}")
            return -1

    def close_device(self):
        """Close connection to SpaceMouse device"""
        try:
            if self._spacemouse_device:
                spacenavigator.close()
                self._spacemouse_device = None
                QtCore.qDebug("SpaceMouse connection closed")
            return 0
        except Exception as e:
            QtCore.qCritical(f"Error closing SpaceMouse: {e}")
            return -1

    def poll_device_event(self, event_wrapper):
        """Poll for events from SpaceMouse device"""
        if not self._spacemouse_device:
            return 0  # No events
        
        try:
            # Get current state
            current_state = spacenavigator.read()
            if not current_state:
                return 0  # No events
            
            # Check for motion events (if state changed)
            if self._last_state is None or (
                current_state.x != self._last_state.x or 
                current_state.y != self._last_state.y or 
                current_state.z != self._last_state.z or
                current_state.roll != self._last_state.roll or 
                current_state.pitch != self._last_state.pitch or 
                current_state.yaw != self._last_state.yaw
            ):
                # Scale from [-1, 1] range to integer range similar to libspnav
                scale_factor = 350
                event_wrapper.type = MOTION_EVENT
                event_wrapper.event.motion.x = int(current_state.x * scale_factor)
                event_wrapper.event.motion.y = int(current_state.y * scale_factor)
                event_wrapper.event.motion.z = int(current_state.z * scale_factor)
                event_wrapper.event.motion.rx = int(current_state.roll * scale_factor)
                event_wrapper.event.motion.ry = int(current_state.pitch * scale_factor)
                event_wrapper.event.motion.rz = int(current_state.yaw * scale_factor)
                event_wrapper.event.motion.period = 0
                
                self._last_state = current_state
                return 1  # Event available
            
            # Check for button events
            for i, button_state in enumerate(current_state.buttons):
                last_button_state = self._button_states.get(i, 0)
                if button_state != last_button_state:
                    event_wrapper.type = BUTTON_EVENT
                    event_wrapper.event.button.bnum = i
                    event_wrapper.event.button.press = button_state
                    self._button_states[i] = button_state
                    return 1  # Event available
            
            self._last_state = current_state
            return 0  # No events
            
        except Exception as e:
            QtCore.qCritical(f"Error polling SpaceMouse: {e}")
            return 0

    def remove_events(self, event_type):
        """Remove events of specified type from queue"""
        # The spacenavigator library doesn't queue events, so we just return 0
        return 0

    def list_devices(self):
        """List all available SpaceMouse devices"""
        try:
            devices = spacenavigator.list_devices()
            return devices if devices else []
        except Exception as e:
            QtCore.qWarning(f"Error listing devices: {e}")
            return []

    def read_device_state(self):
        """Read current state from connected SpaceMouse device"""
        return spacenavigator.read()

# Create the adapter instance
adapter = SpaceMouseAdapter()
