"""lintswitch: Configuration.
"""

#
# Defaults
#


LOG_LEVEL = 'DEBUG'

# Connect to this socket and write a filename, for it to get linted.
LINT_PORT = 4008

# Browse here for live linting results!
HTTP_PORT = 8008

# Full path to various checkers

PYLINT_CMD = '/usr/local/bin/pylint'    # pip install pylint
PEP8_CMD = '/usr/local/bin/pep8'        # pip install pep8
PYMETRICS_CMD = '/usr/bin/pymetrics'    # sudo apt-get install pymetrics

# Above which Cyclomatic complexity do we register a warning?
PYMETRICS_WARN = 5

# Above which Cyclomatic complexity do we register an error?
PYMETRICS_ERR = 10
