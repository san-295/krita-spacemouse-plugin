# event_handler.py - Ultra-minimal
from krita import Krita
from PyQt5 import QtCore
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

        # Read SpaceNavigator data and print results
        try:
            state = spacenavigator.read()
            if state:
                QtCore.qDebug(f"SpaceNavigator data: x={state.x:.3f}, y={state.y:.3f}, z={state.z:.3f}")
                QtCore.qDebug(f"                    roll={state.roll:.3f}, pitch={state.pitch:.3f}, yaw={state.yaw:.3f}")
                QtCore.qDebug(f"                    buttons={state.buttons}")
        except Exception as read_error:
            QtCore.qWarning(f"Error reading SpaceNavigator: {read_error}")

    except Exception as e:
        QtCore.qCritical(f"Error in poll_spacenav: {e}")
        self.timer.stop()  # Stop on any error
