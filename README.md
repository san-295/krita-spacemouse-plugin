# krita-spacemouse-plugin
A simple plugin that allows for panning and zooming in krita via space mouse

# setup instruction
1. Copy the contents of this repository into the pykrita folder, which can be accessed via Settings -> Manage Resources -> Open Resource Folder
2. Enable the plugin: Settings -> Configure Krita -> Python Plugin Manager -> Check SpaceMouse Plugin (Simplified)
3. Restart Krita
4. Enable the docker: Settings -> Dockers -> SpaceMouse
5. Connect the corresponding SpaceMouse device by selecting from the dropdown and pressing connect

Requires:
spacenavigator: https://github.com/johnhw/pyspacenavigator
and
pywinusb: https://github.com/rene-aguirre/pywinusb
to be installed into the pykrita folder.

Not sure if this is the right way to do things, I did this by: pip install <spacenavigator/pywinusb> --target <pykrita-director>
