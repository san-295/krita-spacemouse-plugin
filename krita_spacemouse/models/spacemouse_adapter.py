"""
SpaceMouse device adapter for Krita SpaceMouse plugin.
Provides interface between spacenavigator library and the plugin.
"""

import spacenavigator
from PyQt5 import QtCore

# Global variables for device state
_spacemouse_device = None
_last_state = None
_button_states = {}

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

def open_device(device_number=0):
    """Open connection to SpaceMouse device"""
    global _spacemouse_device, _last_state, _button_states
    
    try:
        _spacemouse_device = spacenavigator.open(DeviceNumber=device_number)
        if _spacemouse_device:
            QtCore.qDebug("Connected to SpaceMouse device")
            return 0  # Success
        else:
            QtCore.qWarning("No SpaceMouse device found")
            return -1  # Failure
    except Exception as e:
        QtCore.qCritical(f"Error opening SpaceMouse: {e}")
        return -1

def close_device():
    """Close connection to SpaceMouse device"""
    global _spacemouse_device
    try:
        if _spacemouse_device:
            spacenavigator.close()
            _spacemouse_device = None
            QtCore.qDebug("SpaceMouse connection closed")
        return 0
    except Exception as e:
        QtCore.qCritical(f"Error closing SpaceMouse: {e}")
        return -1

def poll_device_event(event_wrapper):
    """Poll for events from SpaceMouse device"""
    global _spacemouse_device, _last_state, _button_states
    
    if not _spacemouse_device:
        return 0  # No events
    
    try:
        # Get current state
        current_state = spacenavigator.read()
        if not current_state:
            return 0  # No events
        
        # Check for motion events (if state changed)
        if _last_state is None or (
            current_state.x != _last_state.x or 
            current_state.y != _last_state.y or 
            current_state.z != _last_state.z or
            current_state.roll != _last_state.roll or 
            current_state.pitch != _last_state.pitch or 
            current_state.yaw != _last_state.yaw
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
            
            _last_state = current_state
            return 1  # Event available
        
        # Check for button events
        for i, button_state in enumerate(current_state.buttons):
            last_button_state = _button_states.get(i, 0)
            if button_state != last_button_state:
                event_wrapper.type = BUTTON_EVENT
                event_wrapper.event.button.bnum = i
                event_wrapper.event.button.press = button_state
                _button_states[i] = button_state
                return 1  # Event available
        
        _last_state = current_state
        return 0  # No events
        
    except Exception as e:
        QtCore.qCritical(f"Error polling SpaceMouse: {e}")
        return 0

def remove_events(event_type):
    """Remove events of specified type from queue"""
    # The spacenavigator library doesn't queue events, so we just return 0
    return 0

class SpaceMouseAdapter:
    """Adapter that provides interface for SpaceMouse devices"""
    def __init__(self):
        self.open_device = open_device
        self.close_device = close_device
        self.poll_device_event = poll_device_event
        self.remove_events = remove_events

# Create the adapter instance
adapter = SpaceMouseAdapter()
