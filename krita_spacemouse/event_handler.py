# event_handler.py - Ultra-minimal
from krita import Krita
from krita_spacemouse.spnav import libspnav, SPNAV_EVENT_MOTION, SPNAV_EVENT_BUTTON

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
                    break
            else:
                return

        # Simple event polling - but do nothing with events for minimal functionality
        result = libspnav.spnav_poll_event(self.event)
        if result == 0:
            return
            
        # Events are polled but ignored for minimal wireless setup
        if self.event.type == SPNAV_EVENT_BUTTON:
            pass  # Button events ignored
        elif self.event.type == SPNAV_EVENT_MOTION:
            pass  # Motion events ignored

    except Exception:
        self.timer.stop()  # Stop on any error
