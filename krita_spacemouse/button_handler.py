# button_handler.py - Ultra-minimal
def process_button_event(self, button_id, press_state):
    """Minimal button handler - just store state"""
    self.button_states[button_id] = press_state
