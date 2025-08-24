# event_handler.py - SpaceMouse canvas control
from krita import Krita
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMdiArea, QScrollBar
from .models.spacemouse_adapter import adapter

def poll_spacenav(extension):
    try:
        window = Krita.instance().activeWindow()
        if not window or not window.activeView():
            return
        
        # Get the docker from the extension by finding it in the dockers list
        docker = None
        dockers = Krita.instance().dockers()
        for d in dockers:
            if d.objectName() == "spacenavDocker":
                docker = d
                break
        
        if not docker:
            return

        # Read SpaceMouse data and apply to canvas
        try:
            state = adapter.read_device_state()
            if state:
                # Get settings from UI - configuration tab
                pan_scale = docker.configuration_tab.get_pan_scale() if hasattr(docker, 'configuration_tab') else None
                zoom_scale = docker.configuration_tab.get_zoom_scale() if hasattr(docker, 'configuration_tab') else None
                rotation_speed = docker.configuration_tab.get_rotation_speed() if hasattr(docker, 'configuration_tab') else None
                dead_zone = docker.configuration_tab.get_dead_zone() if hasattr(docker, 'configuration_tab') else None
                
                # Skip processing if we can't get configuration values
                if pan_scale is None or zoom_scale is None or rotation_speed is None or dead_zone is None:
                    QtCore.qWarning("Configuration tab not available, skipping SpaceMouse processing")
                    return
                
                # Apply dead zone and get processed values - let UI sensitivities handle all scaling
                x_pan_raw = apply_deadzone(state.x, dead_zone)
                y_pan_raw = apply_deadzone(state.y, dead_zone) * -1  # Invert Y for natural movement
                z_zoom_raw = apply_deadzone(state.z, dead_zone)
                yaw_raw = apply_deadzone(state.yaw, dead_zone)
                
                # Only process if there's any movement (apply_deadzone already handles deadzone filtering)
                if x_pan_raw != 0 or y_pan_raw != 0 or z_zoom_raw != 0 or yaw_raw != 0:
                    apply_to_canvas(window, x_pan_raw, y_pan_raw, z_zoom_raw, yaw_raw, 
                                  pan_scale, zoom_scale, rotation_speed)
                    
        except Exception as read_error:
            QtCore.qWarning(f"Error reading SpaceMouse: {read_error}")

    except Exception as e:
        QtCore.qCritical(f"Error in poll_spacenav: {e}")
        extension.timer.stop()  # Stop on any error

def apply_deadzone(value, deadzone):
    """Apply deadzone to raw input value with smooth scaling"""
    if abs(value) < deadzone:
        return 0.0
    # Scale the remaining range to maintain smooth movement
    # This removes the deadzone portion and scales the rest to 0-1 range
    sign = 1 if value > 0 else -1
    scaled_value = (abs(value) - deadzone) / (1.0 - deadzone)
    return sign * scaled_value

def apply_to_canvas(window, x_pan_raw, y_pan_raw, z_zoom_raw, yaw_raw, pan_scale, zoom_scale, rotation_speed):
    """Apply movement to the Krita canvas"""
    try:
        view = window.activeView()
        if not view:
            return
            
        canvas = view.canvas()
        if not canvas:
            return

        # Apply panning
        if x_pan_raw != 0 or y_pan_raw != 0:
            apply_panning(window, x_pan_raw, y_pan_raw, pan_scale)

        # Apply zooming
        if z_zoom_raw != 0:
            apply_zooming(view, z_zoom_raw, zoom_scale)

        # Apply rotation
        if yaw_raw != 0:
            apply_rotation(canvas, yaw_raw, rotation_speed)
            
    except Exception as e:
        QtCore.qWarning(f"Error applying canvas transformation: {e}")

def apply_panning(window, x_pan_raw, y_pan_raw, pan_scale):
    """Apply panning movement to the canvas using scroll bars"""
    try:
        # Find the scroll bars through MDI area
        qwin = window.qwindow()
        subwindow = qwin.findChild(QMdiArea).currentSubWindow()
        if not subwindow:
            QtCore.qWarning("No subwindow found for panning")
            return
            
        hscroll = vscroll = None
        for sb in subwindow.findChildren(QScrollBar):
            if sb.orientation() == Qt.Horizontal:
                hscroll = sb
            elif sb.orientation() == Qt.Vertical:
                vscroll = sb
                
        if hscroll and vscroll:
            # Use direct pan scale from UI
            dx = int(-x_pan_raw * pan_scale)  # Inverted horizontal
            dy = int(-y_pan_raw * pan_scale)  # Inverted vertical
            
            # Apply panning via scroll bars
            hscroll.setValue(hscroll.value() + dx)
            vscroll.setValue(vscroll.value() + dy)
        else:
            QtCore.qWarning("Scrollbars not found")
            
    except Exception as e:
        QtCore.qWarning(f"Error applying panning: {e}")

def apply_zooming(view, z_zoom_raw, zoom_scale):
    """Apply zooming to the canvas with DPI correction"""
    try:
        # Get current zoom level - account for DPI scaling bug in Krita
        canvas_zoom_raw = view.canvas().zoomLevel()
        
        # Get document DPI to calculate actual zoom percentage
        document = Krita.instance().activeDocument()
        doc_dpi = document.resolution()  # Document DPI
        baseline_dpi = 72.0  # Krita's baseline DPI for zoom calculations
        dpi_factor = doc_dpi / baseline_dpi
        
        # Calculate actual UI zoom percentage (correct for DPI bug in reading)
        actual_zoom_percent = (canvas_zoom_raw / dpi_factor) * 100
                
        # Use direct zoom scale from UI
        zoom_factor = 1.0 + (z_zoom_raw * zoom_scale)
        
        # Apply zoom factor to actual zoom percentage
        new_actual_percent = actual_zoom_percent * zoom_factor
        
        # Only apply zoom if the change is significant enough
        new_zoom_decimal = max(5.0, min(3200.0, new_actual_percent)) / 100.0
        
        # Set the new zoom level (no DPI conversion needed for setZoomLevel)
        view.canvas().setZoomLevel(new_zoom_decimal)
        
    except Exception as zoom_error:
        QtCore.qDebug(f"Zoom error: {zoom_error}")
        QtCore.qWarning(f"Error with smooth zoom: {zoom_error}")

def apply_rotation(canvas, yaw_raw, rotation_speed):
    """Apply rotation to the canvas"""
    try:
        current_rotation = canvas.rotation()
        # Use direct rotation speed from UI
        new_rotation = (current_rotation + (yaw_raw * rotation_speed)) % 360
        canvas.setRotation(new_rotation)
        
    except Exception as e:
        QtCore.qWarning(f"Error applying rotation: {e}")
