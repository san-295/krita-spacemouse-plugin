from krita import Krita
from .extension import SpacenavControlExtension

def initialize():
    app = Krita.instance()
    if app:
        # Register the extension
        app.addExtension(SpacenavControlExtension(app))
        print("Krita_Spacemouse plugin v1.0 registered")

        # Optional: Log successful initialization for debugging
        print("Plugin initialization complete")
    else:
        print("Krita instance not found")

# Run initialization
initialize()
