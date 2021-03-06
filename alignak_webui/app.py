#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016:
#   Frederic Mohier, frederic.mohier@gmail.com
#
# This file is part of (WebUI).
#
# (WebUI) is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# (WebUI) is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with (WebUI).  If not, see <http://www.gnu.org/licenses/>.
"""
Usage:
    {command} [-h] [-v] [-d] [-x] [-b=url] [-n=hostname] [-p=port] [<cfg_file>...]

Options:
    -h, --help                  Show this screen.
    -v, --version               Show application version.
    -b, --backend url           Specify backend URL [default: http://127.0.0.1:5000]
    -n, --hostname host         Specify WebUI host (or ip address) [default: 127.0.0.1]
    -p, --port port             Specify WebUI port [default: 5001]
    -d, --debug                 Run in debug mode (more info to display) [default: False]
    -x, --exit                  Start application but do not run server [default: False]

Use cases:
    Display help message:
        {command} -h
    Display current version:
        {command} -v

    Run application in default mode:
        {command} -b=backend

    Run application in normal mode (open outside):
        {command} -b=backend -n=0.0.0.0

    Run application in debug mode and listen on all interfaces:
        {command} -d -b=backend -n=0.0.0.0 -p=5001

    Exit code:
        0 if all is ok
        1 configuration error
        2 run error
        64 if command line parameters are not used correctly
        99 application started but server not run (test application start)

"""
from __future__ import print_function

import os
import traceback

# Logs
from logging import getLogger

# Bottle import
from bottle import run

# Command line interpreter
from docopt import docopt
from docopt import DocoptExit

# Settings
from alignak_webui.utils.settings import Settings

# Application
from alignak_webui import manifest, webapp
from alignak_webui import set_app_config, set_app_webui
from alignak_webui import __name__ as __pkg_name__
from alignak_webui.application import WebUI

# --------------------------------------------------------------------------------------------------
# Application logger
logger = getLogger(__pkg_name__)

cfg_file = None

# Test mode for the application
if os.environ.get('TEST_WEBUI'):
    print("Application is in test mode")
else:  # pragma: no cover - tests are run in test mode...
    print("Application is in production mode")

if os.environ.get('ALIGNAK_WEBUI_CONFIGURATION_FILE'):
    cfg_file = os.environ.get('ALIGNAK_WEBUI_CONFIGURATION_FILE')
    print("Application configuration file name from environment: %s" % cfg_file)

# Read configuration file
app_config = Settings(cfg_file)
config_file = app_config.read(manifest['name'])
print("Configuration read from: %s" % config_file)
if not app_config:  # pragma: no cover, should never happen
    print("Required configuration file not found.")
    exit(1)

# Store application name in the configuration
app_config['name'] = manifest['name']

# Debug mode for the application (run Bottle in debug mode)
app_config['debug'] = (app_config.get('debug', '0') == '1')
print("Application debug mode: %s" % app_config['debug'])

if __name__ != "__main__":
    # Make the configuration available globally for the package
    set_app_config(app_config)

    # Make the application available globally for the package
    app_webui = set_app_webui(WebUI(app_config))


# --------------------------------------------------------------------------------------------------
# Main function
def main():  # pragma: no cover, not mesured by coverage!
    # pylint: disable=redefined-variable-type, global-statement
    """
        Called when this module is started from shell
    """
    global cfg_file, app_config, app_webui

    # ----------------------------------------------------------------------------------------------
    # Command line parameters
    args = {
        '--debug': False,
        '--backend': None,
        '--hostname': None,
        '--port': None,
        '--exit': False
    }

    if __name__ == "__main__":  # pragma: no cover, not mesured by coverage!
        try:
            args = docopt(__doc__, version=manifest['version'])
        except DocoptExit:
            print("Command line parsing error")
            exit(64)
    # Application settings
    # ----------------------------------------------------------------------------------------------
    # Configuration file path in command line parameters
    if '<cfg_file>' in args:
        cfg_file = args['<cfg_file>']

        if cfg_file and isinstance(cfg_file, list):
            cfg_file = cfg_file[0]

        # Read configuration file
        app_config = Settings(cfg_file)
        new_config_file = app_config.read(manifest['name'])
        print("Configuration read from: %s" % new_config_file)
        if not app_config:  # pragma: no cover, should never happen
            print("Required configuration file not found.")
            exit(1)

    # Store application name in the configuration
    app_config['name'] = manifest['name']

    if '--debug' in args and args['--debug']:  # pragma: no cover, not mesured by coverage!
        app_config['debug'] = '1'
        print("Application is in debug mode from command line")

    if os.environ.get('WEBUI_DEBUG'):  # pragma: no cover, not mesured by coverage!
        app_config['debug'] = '1'
        print("Application is in debug mode from environment")

    # Applications backend URL
    if args['--backend']:  # pragma: no cover, not mesured by coverage!
        app_config['alignak_backend'] = args['--backend']

    # WebUI server configuration
    if args['--hostname']:  # pragma: no cover, not mesured by coverage!
        app_config['host'] = args['--hostname']
    if args['--port']:  # pragma: no cover, not mesured by coverage!
        app_config['port'] = args['--port']

    # Make the configuration available globally for the package
    set_app_config(app_config)

    # Make the application available globally for the package
    app_webui = set_app_webui(WebUI())

    try:
        if args['--exit']:
            print("Application exit because of command line parameter")
            exit(99)

        # Run application server...
        run(
            app=webapp,
            host=app_config.get('host', '127.0.0.1'),
            port=int(app_config.get('port', 5001)),
            debug=(app_config.get('debug', '0') == '1'),
            server=app_config.get('http_backend', 'cherrypy')
        )
    except Exception as e:
        logger.error("Application run failed, exception: %s / %s", type(e), str(e))
        logger.info("Backtrace: %s", traceback.format_exc())
        logger.info("stopping backend livestate thread...")
        exit(2)

if __name__ == "__main__":  # pragma: no cover, not mesured by coverage!
    main()
