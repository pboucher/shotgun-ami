# shotgun-ami
Handle Shotgun AMI protocols on local computers

# Application Configuration
1. Download the contents of this repo
2. Within the `ShotgunAMIEngine.app` bundle, navigate to `Contents/Resources/Python`
3. Edit the file `ami_engine.py` with the correct settings
4. Copy the Shotgun Python API to the `shotgun_api3` folder
5. In the `plugins` folder, create any handler plugins. These must contain a function called `process_action` that takes the following argments: `sg`, `logger`, `params`, where `sg` is a Shotgun instance, `logger` is a logger instance, and `params` is a dict of data sent from Shotgun

# Shotgun Configuration
1. On the Action Menu Items page, create a new Action Menu Item with URL set to `shotgun://name_of_plugin`. For example, to add a Action Menu Item that runs the "test" plugin, the URL would be `shotgun://test`

# End-user Usage
Double-click the `ShotgunAMIEngine.app`. If you get a warning that the file cannot be opened, then right-click it and choose "Open", and then accept when asked for confirmation. The application will quit immediately (but it should remain in /Applications afterwards).

In Shotgun, right-click the approppriate item, or use the Action Menu button and choose the action. The very first time you activate one of the menu options, the browser may ask you if it's ok to launch an external protocol. Accept (and if there's an option to remember that choice, check it so it doesn't ask you every time).
