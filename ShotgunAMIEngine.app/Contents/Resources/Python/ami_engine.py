#!/usr/bin/env python

import imp
import logging
import logging.handlers
import os
import traceback
import sys
import urllib

# Include our own Python API from the included submodule
PYTHON_API_PATH = os.path.join(os.path.dirname(__file__), 'python-api')
if PYTHON_API_PATH not in sys.path and os.path.exists(PYTHON_API_PATH):
    sys.path.insert(0, PYTHON_API_PATH)

import shotgun_api3 as shotgun

# This should include the .app suffix
# TODO: Figure out another way to do this with relative paths also see
#       Config.getPluginsPath
OSX_APPLICATION_NAME = 'ShotgunAMIEngine.app'


class Config(object):
    """This object should hold the config options for the AMI engine."""

    def getLogPath(self):
        # TODO: This should be in a config file
        return '/var/log/ShotgunAMIEngine'

    def getDefaultLogFile(self):
        return os.path.join(self.getLogPath(), 'ami_engine.log')

    def getActionLogFile(self, action):
        return os.path.join(self.getLogPath(), 'ami.%s.log' % action)

    def getDefaultLogLevel(self):
        # TODO: This should be in a config file
        return 10

    def getActionLogLevel(self, action):
        # TODO: This should be in a config file
        return self.getDefaultLogLevel()

    def getPluginsPath(self):
        # TODO: Figure out another way to do this with relative paths also see
        #       OSX_APPLICATION_NAME
        return os.path.join('/Applications', OSX_APPLICATION_NAME, 'Contents/Resources/Python/plugins')

    def getShotgunURL(self):
        # TODO: This should be in a config file
        return 'https://my_site.shotgunstudio.com'

    def getDefaultAuth(self):
        # TODO: This should be in a config file
        return ('script_name', 'script_key')

    def getActionAuth(self, action):
        """
        Check the config file for auth parameters for this action or return the
        default auth parameters.
        """
        # TODO: Implement the config file check
        return self.getDefaultAuth()


class AMIEngine(object):
    def __init__(self, config):
        self._config = config

        # Setup logging
        self.logger = logger = self._get_logger()

    def process_url(self, url):
        action, params = self._parse_ami_url(url)

        # Try loading the plugin
        plugin = None
        plugin_file = os.path.join(self._config.getPluginsPath(), '%s.py' % action)
        try:
            plugin = imp.load_source(action, plugin_file)
        except:
            # TODO: Could surely make this error trapping smarter
            self.logger.error('Could not load the plugin at %s.\n\n%s', plugin_file, traceback.format_exc())

        if plugin:
            run_func = getattr(plugin, 'process_action', None)
            if callable(run_func):
                # Setup logging for the action
                logger = self._get_logger(action)

                # Get the Shotgun connection
                script_name, script_key = self._config.getActionAuth(action)
                sg = shotgun.Shotgun(self._config.getShotgunURL(), script_name, script_key, sudo_as_login=params['user_login'])
                sg.set_session_uuid(params['session_uuid'])

                try:
                    run_func(sg, logger, params)
                except:
                    self.logger.critical('Error running process_action function from plugin at %s.\n\n%s', plugin_file, traceback.format_exc())
            else:
                self.logger.critical('Did not find a process_action function in plugin at %s.', plugin_file)

    def _get_logger(self, action=None):
        if action:
            logger = logging.getLogger(action)
            log_file = self._config.getActionLogFile(action)
            log_level = self._config.getActionLogLevel(action)
        else:
            logger = logging.getLogger('engine')
            log_file = self._config.getDefaultLogFile()
            log_level = self._config.getDefaultLogLevel()

        handler = logging.handlers.TimedRotatingFileHandler(log_file, 'midnight', backupCount=10)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(log_level)

        return logger

    def _parse_ami_url(self, url):
        """
        Return a tuple containing the action and the AMI parameters.
        """
        handler, fullPath = url.split(":", 1)
        path, fullArgs = fullPath.split("?", 1)
        action = path.strip("/")
        args = fullArgs.split("&")

        params = {}
        for arg in args:
            key, value = map(urllib.unquote, arg.split("=", 1))
            params[key] = value

        # Preprocess CSV integer data
        for int_csv_data_field in ['ids', 'selected_ids']:
            if int_csv_data_field in params:
                params[int_csv_data_field] = [int(i) for i in params[int_csv_data_field].split(',')]

        return (action, params)


if __name__ == '__main__':
    config = Config()

    # Setup application logging i.e. STDOUT logging
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(config.getDefaultLogLevel())

    # Start the engine and process the URL
    engine = AMIEngine(config)
    engine.process_url(sys.argv[1])
