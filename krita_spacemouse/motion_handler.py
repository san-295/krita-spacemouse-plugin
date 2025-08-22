# motion_handler.py - Ultra-minimal for SpaceMouse Wireless
from krita import Krita

def process_motion_event(self, axis_inputs):
    """Ultra-simplified motion handler - hardcoded settings"""
    docker = self.docker
    
    # Get sensitivity from UI if available, otherwise use default
    sensitivity = docker.advanced_tab.sensitivity_slider.value() / 100.0 if hasattr(docker, 'advanced_tab') else 1.0
    dead_zone = docker.advanced_tab.dead_zone_slider.value() if hasattr(docker, 'advanced_tab') else 130
    
    # Simple fixed axis mapping
    x_input = axis_inputs.get("x", 0)
    y_input = axis_inputs.get("y", 0)
    z_input = axis_inputs.get("z", 0)
    rz_input = axis_inputs.get("rz", 0)
    
    # Apply dead zone and scaling
    def process_axis(raw_value, scale=1.0):
        if abs(raw_value) < dead_zone:
            return 0
        return int((raw_value - dead_zone if raw_value > 0 else raw_value + dead_zone) * sensitivity * scale)
    
    dx = process_axis(x_input, 2.0)  # Horizontal pan
    dy = process_axis(y_input, -2.0)  # Vertical pan (inverted)
    zoom_delta = process_axis(z_input, 0.002)  # Zoom
    rotation_delta = process_axis(rz_input, 0.02)  # Rotation
    
    # Apply transformations if there's movement
    if dx != 0 or dy != 0 or zoom_delta != 0 or rotation_delta != 0:
        view = Krita.instance().activeWindow().activeView()
        if not view:
            return
            
        canvas = view.canvas()
        if not canvas:
            return

        # Apply panning
        if dx != 0 or dy != 0:
            qpoint = canvas.canvasWidget().mapFromGlobal(canvas.canvasWidget().cursor().pos())
            canvas.pan(qpoint.x() + dx, qpoint.y() + dy)

        # Apply zooming
        if zoom_delta != 0:
            current_zoom = canvas.zoomLevel()
            new_zoom = max(0.01, min(100.0, current_zoom * (1 + zoom_delta)))
            canvas.setZoomLevel(new_zoom)

        # Apply rotation
        if rotation_delta != 0:
            current_rotation = canvas.rotation()
            new_rotation = (current_rotation + rotation_delta) % 360
            canvas.setRotation(new_rotation)
