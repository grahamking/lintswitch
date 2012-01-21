"""lintswitch: Parts that actually check the file.
"""

import logging
import subprocess

from config import PYLINT_CMD, PEP8_CMD, PYMETRICS_CMD
from config import PYMETRICS_ERR, PYMETRICS_WARN

LOG = logging.getLogger(__name__)

CHECKERS = {}


def check(filename):
    """Module entry point.
    Runs all registered linters, gathers and returns their info.
    @return errors, warnings, summaries: Three arrays.
    """

    ext = filename.split('.')[-1].lower()
    if not ext in CHECKERS:
        return

    errors = {}
    warnings = {}
    summaries = {}

    for name, func in CHECKERS[ext]:
        try:
            l_errs, l_warns, l_summary = func(filename)
        except Exception:
            LOG.exception('%s failed on %s', name, filename)
            continue
        errors[name] = l_errs
        warnings[name] = l_warns
        if l_summary:
            summaries[name] = l_summary

    return errors, warnings, summaries


def checker(name, ext):
    """Decorator that registers decorated func as a checker
    for the given extension.
    @param name Display name of the checker
    @param ext Extension this checker targets ('py', 'js', etc)
    """
    if not ext in CHECKERS:
        CHECKERS[ext] = []
    return lambda func: CHECKERS[ext].append((name, func))


def shell(cmd):
    """Run cmd in a shell, and return it's stdout as array of lines.
    @cmd String or array of command to run.
    """
    if isinstance(cmd, basestring):
        cmd = cmd.split()

    try:
        stdout, _ = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT).communicate()
    except OSError:
        LOG.exception('Error running: %s', cmd)
        return None

    stdout = unicode(stdout)                # Help pylint figure out the type
    return stdout.split('\n')


def plural(arr):
    """Utility to help adding an 's' to pluralize strings.
    Usage: print('hello world%s' % plural(world_array))
    """
    return '' if len(arr) == 1 else 's'


#--------
# pylint
#--------

@checker('pylint', 'py')
def pylint_run(filename):
    """Run pylint on given filename.

    Dependencies: pip install pylint
    """

    cmd = [PYLINT_CMD,
           '--output-format=parseable',
           '--include-ids=y',
           '--reports=y',
           '%s' % filename,
          ]
    lines = shell(cmd)

    errors = []
    warnings = []
    rating = ''

    for line in lines:
        line = line.strip()

        if '[E' in line:
            parts = line.split(':')
            errors.append('Line %s: %s' % (parts[1], parts[2]))

        elif '[' in line and not 'Locally disabling' in line:
            parts = line.split(':')
            warnings.append('Line %s: %s' % (parts[1], parts[2]))

        elif line.startswith('Your code has been rated'):
            rating = line.split()[6]

    summary = rating
    if errors:
        summary += ' (%d error%s)' % (len(errors), plural(errors))
    elif warnings:
        summary += ' (%d warning%s)' % (len(warnings), plural(warnings))

    return errors, warnings, summary


#------
# pep8
#------

@checker('pep8', 'py')
def pep8_run(filename):
    """Run pep8 on given filename.
    We ignore the following warnings:
        - W391: Blank line at end of file.

    Dependencies: pip install pep8
    """

    cmd = PEP8_CMD + ' --ignore=W391 --repeat %s' % filename
    lines = shell(cmd)

    warnings = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.split(':')
        warnings.append('Line %s, char %s: %s' %
                (parts[1], parts[2], parts[3]))

    summary = ''
    if warnings:
        summary = '%d warning%s' % (len(warnings), plural(warnings))

    return [], warnings, summary


@checker('pymetrics', 'py')
def pymetrics_run(filename):
    """Run pymetrics on give filename to get cyclomatic complexity.

    Dependencies: sudo apt-get install pymetrics
    The 'pymetrics' in pypi is wrong!
    If you're not on Ubuntu use the source:
        http://sourceforge.net/projects/pymetrics/
    """

    cmd = [PYMETRICS_CMD,
           '--nobasic',
           '--nosql',
           '--nocsv',
           '--include=mccabe:McCabeMetric',
           filename]

    lines = shell(cmd)

    errors = []
    warnings = []
    max_complexity = 0

    for line in lines:
        line = line.strip()
        if not starts_with_number(line):
            continue

        parts = line.split()
        complexity = int(parts[0])
        function = parts[1]

        max_complexity = max(complexity, max_complexity)

        if complexity > PYMETRICS_ERR:
            errors.append('%s too complex (%d)' % (function, complexity))
        elif complexity > PYMETRICS_WARN:
            warnings.append('%s: Complexity %d' % (function, complexity))

        summary = ''
        if errors:
            summary = '%d max complexity' % max_complexity

    return errors, warnings, summary


def starts_with_number(line):
    """True if the first char of line is a number,
    False otherwise.
    """
    if not line:
        return False

    try:
        int(line[0])
        return True
    except ValueError:
        return False

