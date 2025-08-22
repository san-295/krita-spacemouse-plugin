# spnav.py - SpaceNavigator interface using spacenavigator.py library
import sys
import os

# Add the parent directory to the path to import spacenavigator
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import spacenavigator
    print("spacenavigator library loaded successfully")
except ImportError as e:
    print(f"Error: Could not load spacenavigator library - {e}")
    raise

# Event type constants (for compatibility with existing code)
SPNAV_EVENT_MOTION = 1
SPNAV_EVENT_BUTTON = 2

# Global device reference
_spacenav_device = None
_last_state = None
_button_states = {}

class SpnavMotionEvent:
    """Motion event compatibility class"""
    def __init__(self, x=0, y=0, z=0, rx=0, ry=0, rz=0, period=0):
        self.x = x
        self.y = y  
        self.z = z
        self.rx = rx
        self.ry = ry
        self.rz = rz
        self.period = period

class SpnavButtonEvent:
    """Button event compatibility class"""
    def __init__(self, press=0, bnum=0):
        self.press = press
        self.bnum = bnum

class SpnavEvent:
    """Event union compatibility class"""
    def __init__(self):
        self.motion = SpnavMotionEvent()
        self.button = SpnavButtonEvent()

class SpnavEventWrapper:
    """Event wrapper compatibility class"""
    def __init__(self):
        self.type = 0
        self.event = SpnavEvent()

# Compatibility functions that mimic libspnav interface
def spnav_open(device_number):
    """Open connection to SpaceNavigator device"""
    global _spacenav_device
    try:
        _spacenav_device = spacenavigator.open(DeviceNumber=device_number)
        if _spacenav_device:
            print("Connected to SpaceNavigator device")
            return 0  # Success
        else:
            print("No SpaceNavigator device found")
            return -1  # Failure
    except Exception as e:
        print(f"Error opening SpaceNavigator: {e}")
        return -1

def spnav_close():
    """Close connection to SpaceNavigator device"""
    global _spacenav_device
    try:
        if _spacenav_device:
            spacenavigator.close()
            _spacenav_device = None
            print("SpaceNavigator connection closed")
        return 0
    except Exception as e:
        print(f"Error closing SpaceNavigator: {e}")
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
            # Scale from [-1, 1] range to integer randebug_print ge similar to libspnav
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
        print(f"Error polling SpaceNavigator: {e}")
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
