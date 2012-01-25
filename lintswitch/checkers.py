"""lintswitch: Parts that actually check the file.
"""

import logging
import subprocess
import os.path

from config import PYMETRICS_ERR, PYMETRICS_WARN

LOG = logging.getLogger(__name__)

CHECKERS = {}   # Filled in by 'checker' decorator


def check(filename):
    """Module entry point.
    Runs all registered linters, gathers and returns their info.
    @return errors, warnings, summaries: Three arrays.
    """

    ext = filename.split('.')[-1].lower()
    if not ext in CHECKERS:
        LOG.debug("No checkers for '%s' files", ext)
        return

    errors = {}
    warnings = {}
    summaries = {}

    for name, func in CHECKERS[ext]:
        try:
            ret = func(filename)
            if not ret:
                continue
            l_errs, l_warns, l_summary = ret

        except Exception:
            LOG.exception('%s failed on %s', name, filename)
            continue
        if l_errs:
            errors[name] = l_errs
        if l_warns:
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


def shell(cmd, cwd=None):
    """Run cmd in a shell, and return it's stdout as array of lines.
    @cmd String or array of command to run.
    """
    if isinstance(cmd, basestring):
        cmd = cmd.split()

    if cwd:
        LOG.debug('Running: %s from %s', ' '.join(cmd), cwd)
    else:
        LOG.debug('Running: %s', ' '.join(cmd))

    try:
        stdout, _ = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        cwd=cwd).communicate()
    except OSError:
        LOG.exception('Error running: %s', cmd)
        return None

    stdout = unicode(stdout)                # Help pylint figure out the type
    return stdout.split('\n')


def find(name, filename=None):
    """Finds a program on system path.
    @param name Name of program you're looking for. e.g. 'pylint'
    @param filename Name of file you're going to use that program with. Used
        to decide whether we're in a virtualenv.
    """
    for directory in syspath(filename):
        candidate = os.path.join(directory, name)
        if os.path.exists(candidate):
            return candidate

    return None


def syspath(filename=None):
    """OS path as array of strings"""

    path = os.getenv('PATH').split(':')

    venv_home = os.getenv('WORKON_HOME')
    filename = os.path.realpath(filename)   # Resolve symlinks
    if filename and venv_home and filename.startswith(venv_home):
        filename = filename[len(venv_home):].strip(os.path.sep)
        venv = filename.split(os.path.sep)[0]
        venv_bin = os.path.join(venv_home, venv, 'bin')
        if os.path.exists(venv_bin):
            path.insert(0, venv_bin)

    return path


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

    pylint = find('pylint', filename)
    if not pylint:
        return

    cmd = [pylint,
           '--output-format=parseable',
           '--include-ids=y',
           '--reports=y',
           '%s' % filename,
          ]
    lines = shell(cmd, cwd=_python_root(filename))

    return _pylint_parse(lines)


def _python_root(filename):
    """The root of this file, which is the highest parent directory
    which is not a python module, determined by looking for __init__.
    """
    sep = os.path.sep
    dirs = filename.split(sep)[:-1]

    candidate = os.path.join(sep.join(dirs), '__init__.py')
    while os.path.exists(candidate):
        dirs = dirs[:-1]
        candidate = os.path.join(sep.join(dirs), '__init__.py')
    return sep.join(dirs)


def _pylint_parse(lines):
    """Parse pylint output into errors, warnings, and a summary."""

    errors = []
    warnings = []
    rating = ''

    for line in lines:
        line = line.strip()

        if '[E' in line:
            parts = line.split(':')
            if len(parts) >= 3:
                errors.append('Line %s: %s' % (parts[1], parts[2]))

        elif '[' in line and not 'Locally disabling' in line:
            parts = line.split(':')
            if len(parts) >= 3:
                warnings.append('Line %s: %s' % (parts[1], parts[2]))

        elif line.startswith('Your code has been rated'):
            rating = line.split()[6]

    summary = _pylint_summary(rating, errors, warnings)
    return errors, warnings, summary


def _pylint_summary(rating, errors, warnings):
    """One line summary of pylint results."""

    summary = rating

    if errors:
        summary += ' (%d error%s)' % (len(errors), plural(errors))
    elif warnings:
        summary += ' (%d warning%s)' % (len(warnings), plural(warnings))

    return summary

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

    pep8 = find('pep8', filename)
    if not pep8:
        return

    cmd = pep8 + ' --ignore=W391 --repeat %s' % filename
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

    pymetrics = find('pymetrics', filename)
    if not pymetrics:
        return

    cmd = [pymetrics,
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


@checker('jshint', 'js')
def jshint_run(filename):
    """Runs jshint"""

    jshint = find('jshint', filename)
    if not jshint:
        return

    cmd = jshint + ' ' + filename
    lines = shell(cmd)

    warnings = []
    summary = ''
    for line in lines:
        line = line.strip()
        if not 'line' in line and not 'errors' in line:
            continue

        if starts_with_number(line):
            summary = line
            continue

        parts = line.split(' ')[1:]
        pos = ' '.join(parts[:4])
        info = ' '.join(parts[4:])
        warnings.append('%s: %s' % (pos, info))

    return [], warnings, summary


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

