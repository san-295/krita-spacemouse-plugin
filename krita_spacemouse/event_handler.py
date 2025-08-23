# event_handler.py - SpaceMouse canvas control
from krita import Krita
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMdiArea, QScrollBar
import spacenavigator

def poll_spacenav(self):
    try:
        window = Krita.instance().activeWindow()
        if not window or not window.activeView():
            return
        
        if not self.docker:
            dockers = Krita.instance().dockers()
            for d in dockers:
                if d.objectName() == "spacenavDocker":
                    self.docker = d
                    self.docker.set_extension(self)
                    QtCore.qDebug("Docker found and linked in event_handler")
                    break
            else:
                return

        # Read SpaceNavigator data and apply to canvas
        try:
            state = spacenavigator.read()
            if state:
                # Get settings from UI
                pan_sensitivity = self.docker.advanced_tab.get_pan_sensitivity() if hasattr(self.docker, 'advanced_tab') else 1.0
                zoom_sensitivity = self.docker.advanced_tab.get_zoom_sensitivity() if hasattr(self.docker, 'advanced_tab') else 1.0
                yaw_sensitivity = self.docker.advanced_tab.get_yaw_sensitivity() if hasattr(self.docker, 'advanced_tab') else 1.0
                dead_zone = self.docker.advanced_tab.get_dead_zone() if hasattr(self.docker, 'advanced_tab') else 0.13
                
                # Apply dead zone and get processed values with separate sensitivities
                x_pan = apply_deadzone(state.x, dead_zone) * pan_sensitivity
                y_pan = apply_deadzone(state.y, dead_zone) * pan_sensitivity * -1  # Invert Y for natural movement
                z_zoom = apply_deadzone(state.z, dead_zone) * zoom_sensitivity
                yaw_rotation = apply_deadzone(state.yaw, dead_zone) * yaw_sensitivity  # Use separate yaw sensitivity
                
                # Only process if there's any movement (apply_deadzone already handles deadzone filtering)
                if x_pan != 0 or y_pan != 0 or z_zoom != 0 or yaw_rotation != 0:
                    apply_to_canvas(window, x_pan, y_pan, z_zoom, yaw_rotation, zoom_sensitivity)
                    
        except Exception as read_error:
            QtCore.qWarning(f"Error reading SpaceNavigator: {read_error}")

    except Exception as e:
        QtCore.qCritical(f"Error in poll_spacenav: {e}")
        self.timer.stop()  # Stop on any error

def apply_deadzone(value, deadzone):
    """Apply deadzone to raw input value with smooth scaling"""
    if abs(value) < deadzone:
        return 0.0
    # Scale the remaining range to maintain smooth movement
    # This removes the deadzone portion and scales the rest to 0-1 range
    sign = 1 if value > 0 else -1
    scaled_value = (abs(value) - deadzone) / (1.0 - deadzone)
    return sign * scaled_value

def apply_to_canvas(window, x_pan, y_pan, z_zoom, yaw_rotation, zoom_sensitivity):
    """Apply movement to the Krita canvas"""
    try:
        view = window.activeView()
        if not view:
            return
            
        canvas = view.canvas()
        if not canvas:
            return

        # Apply panning using scroll bars (apply_deadzone already filtered out small values)
        if x_pan != 0 or y_pan != 0:
            # Find the scroll bars through MDI area
            qwin = window.qwindow()
            subwindow = qwin.findChild(QMdiArea).currentSubWindow()
            if not subwindow:
                QtCore.qWarning("No subwindow found for panning")
            else:
                hscroll = vscroll = None
                for sb in subwindow.findChildren(QScrollBar):
                    if sb.orientation() == Qt.Horizontal:
                        hscroll = sb
                    elif sb.orientation() == Qt.Vertical:
                        vscroll = sb
                        
                if hscroll and vscroll:
                    # Scale panning for reasonable speed
                    pan_scale = 120
                    dx = int(-x_pan * pan_scale)  # Inverted horizontal
                    dy = int(-y_pan * pan_scale)  # Inverted vertical
                    
                    # Apply panning via scroll bars
                    hscroll.setValue(hscroll.value() + dx)
                    vscroll.setValue(vscroll.value() + dy)
                else:
                    QtCore.qWarning("Scrollbars not found")

        # Apply zooming (apply_deadzone already filtered out small values)
        if z_zoom != 0:
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
                        
                # Calculate zoom factor based on z movement and UI zoom sensitivity
                zoom_scale = 0.02 * zoom_sensitivity  # Scale zoom sensitivity 
                zoom_factor = 1.0 + (z_zoom * zoom_scale)
                
                # Apply zoom factor to actual zoom percentage
                new_actual_percent = actual_zoom_percent * zoom_factor
                
                # Only apply zoom if the change is significant enough
                new_zoom_decimal = max(5.0, min(3200.0, new_actual_percent)) / 100.0
                
                # Set the new zoom level (no DPI conversion needed for setZoomLevel)
                view.canvas().setZoomLevel(new_zoom_decimal)
                QtCore.qDebug(f"Zoom: {actual_zoom_percent:.1f}% -> {new_actual_percent:.1f}%")
                
            except Exception as zoom_error:
                QtCore.qDebug(f"Zoom error: {zoom_error}")
                QtCore.qWarning(f"Error with smooth zoom: {zoom_error}")

        # Apply rotation (apply_deadzone already filtered out small values)
        if yaw_rotation != 0:
            current_rotation = canvas.rotation()
            rotation_speed = 2.0  # degrees per unit
            new_rotation = (current_rotation + (yaw_rotation * rotation_speed)) % 360
            canvas.setRotation(new_rotation)
            
    except Exception as e:
        QtCore.qWarning(f"Error applying canvas transformation: {e}")
