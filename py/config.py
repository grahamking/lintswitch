"""lintswitch: Configuration.
"""

LOG_FILE = '/tmp/lint_switch.log'

# Connect to this socket and write a filename, for it to get linted.
LINT_PORT = 4008

# Browse here!
HTTP_PORT = 8009

# Full path to various checkers

PYLINT_CMD = '/usr/local/bin/pylint'    # pip install pylint
PEP8_CMD = '/usr/local/bin/pep8'        # pip install pep8
PYMETRICS_CMD = '/usr/bin/pymetrics'    # sudo apt-get install pymetrics

# Above which Cyclomatic complexity do we register a warning?
PYMETRICS_WARN = 5

# Above which Cyclomatic complexity do we register an error?
PYMETRICS_ERR = 10

# List of function to output results. These must be in emitters.py.
EMITTERS = ['zenity_emit', 'notify_emit', 'html_emit']

# Full path to zenity. Only needed if using zenity_emit in EMITTERS.
# Install on Ubuntu: sudo apt-get install zenity
ZENITY_CMD = '/usr/bin/zenity'

# Full path to notify-send. Only needed if using notify_emit in EMITTERS.
# Install on Ubuntu: sudo apt-get install libnotify-bin
NOTIFY_CMD = '/usr/bin/notify-send'
