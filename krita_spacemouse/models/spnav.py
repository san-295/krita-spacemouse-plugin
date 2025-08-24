"""
SpaceNavigator device interface for Krita SpaceMouse plugin.
Provides compatibility layer between spacenavigator library and libspnav-like interface.
"""

import spacenavigator
from PyQt5 import QtCore

# Global variables for device state
_spacenav_device = None
_last_state = None
_button_states = {}

# Constants for event types (libspnav compatibility)
SPNAV_EVENT_MOTION = 1
SPNAV_EVENT_BUTTON = 2

class SpnavMotionEvent:
    """Motion event data structure"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.rx = 0
        self.ry = 0
        self.rz = 0
        self.period = 0

class SpnavButtonEvent:
    """Button event data structure"""
    def __init__(self):
        self.bnum = 0
        self.press = 0

class SpnavEventUnion:
    """Union for different event types"""
    def __init__(self):
        self.motion = SpnavMotionEvent()
        self.button = SpnavButtonEvent()

class SpnavEvent:
    """SpaceNavigator event wrapper"""
    def __init__(self):
        self.type = 0
        self.event = SpnavEventUnion()

def spnav_open(device_number=0):
    """Open connection to SpaceNavigator device"""
    global _spacenav_device, _last_state, _button_states
    
    try:
        _spacenav_device = spacenavigator.open(DeviceNumber=device_number)
        if _spacenav_device:
            QtCore.qDebug("Connected to SpaceNavigator device")
            return 0  # Success
        else:
            QtCore.qWarning("No SpaceNavigator device found")
            return -1  # Failure
    except Exception as e:
        QtCore.qCritical(f"Error opening SpaceNavigator: {e}")
        return -1

def spnav_close():
    """Close connection to SpaceNavigator device"""
    global _spacenav_device
    try:
        if _spacenav_device:
            spacenavigator.close()
            _spacenav_device = None
            QtCore.qDebug("SpaceNavigator connection closed")
        return 0
    except Exception as e:
        QtCore.qCritical(f"Error closing SpaceNavigator: {e}")
        return -1

def spnav_poll_event(event_wrapper):
    """Poll for events from SpaceNavigator device"""
    global _spacenav_device, _last_state, _button_states
    
    if not _spacenav_device:
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
            event_wrapper.type = SPNAV_EVENT_MOTION
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
                event_wrapper.type = SPNAV_EVENT_BUTTON
                event_wrapper.event.button.bnum = i
                event_wrapper.event.button.press = button_state
                _button_states[i] = button_state
                return 1  # Event available
        
        _last_state = current_state
        return 0  # No events
        
    except Exception as e:
        QtCore.qCritical(f"Error polling SpaceNavigator: {e}")
        return 0

def spnav_remove_events(event_type):
    """Remove events of specified type from queue"""
    # The spacenavigator library doesn't queue events, so we just return 0
    return 0

# Create a libspnav-like object for compatibility
class LibSpnavCompat:
    """Compatibility class that mimics libspnav CDLL interface"""
    def __init__(self):
        self.spnav_open = spnav_open
        self.spnav_close = spnav_close
        self.spnav_poll_event = spnav_poll_event
        self.spnav_remove_events = spnav_remove_events

# Create the libspnav compatibility object
libspnav = LibSpnavCompat()
