
import logging
import subprocess

LOG = logging.getLogger(__name__)

ERRORS = 1
WARNINGS = 2
SUMMARIES = 3
EMITTERS = {ERRORS: [], WARNINGS: [], SUMMARIES: []}


def emit(errors, warnings, summaries):
    """Runs all registered emitters, so that user sees the output.
    """

    if errors:
        for func in EMITTERS[ERRORS]:
            func(errors)

    if warnings:
        for func in EMITTERS[WARNINGS]:
            func(warnings)

    if summaries:
        for func in EMITTERS[SUMMARIES]:
            func(summaries)


def emitter(interest):
    """Decorator to register an emitter.
    @param interest One of ERRORS, WARNINGS or SUMMARIES. Says which
    type of information the emitter emits.
    """
    return lambda func: EMITTERS[interest].append(func)


def shell(cmd):
    """Run cmd in a shell.
    @cmd String or array of command to run.
    """
    if isinstance(cmd, basestring):
        cmd = cmd.split()

    try:
        subprocess.call(cmd)
    except OSError:
        LOG.exception('Error running: %s', cmd)


#--------
# zenity for errors
#--------
@emitter(ERRORS)
def zenity_emit(errors):
    """Shell to zenity to popup errors.
    """
    cmd = ['/usr/bin/zenity',
           '--error',
           '--title', 'Lint errors',
           '--text', '\n'.join(errors)]
    shell(cmd)

#-------------
# notify-send for summaries
#------------
@emitter(SUMMARIES)
def notify_emit(summaries):
    """Shell to notify-send to subtle summary notification.
    """

    title = "lintswitch"
    body = ','.join(summaries)
    cmd = ['/usr/bin/notify-send', title, body]
    shell(cmd)

