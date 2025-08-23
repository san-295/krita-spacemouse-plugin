from krita import Krita
from .extension import SpacenavControlExtension
from PyQt5 import QtCore

def initialize():
    app = Krita.instance()
    if app:
        try:
            # Register the extension
            app.addExtension(SpacenavControlExtension(app))
            QtCore.qDebug("Krita_Spacemouse plugin v1.0 registered")
            QtCore.qDebug("Plugin initialization complete")
        except Exception as e:
            QtCore.qCritical(f"Failed to initialize SpaceMouse plugin: {e}")
    else:
        QtCore.qWarning("Krita instance not found")

# Run initialization
initialize()
