
import logging
import subprocess
import os.path

LOG = logging.getLogger(__name__)

ERRORS = 1
WARNINGS = 2
SUMMARIES = 3
EMITTERS = {ERRORS: [], WARNINGS: [], SUMMARIES: []}


def emit(filepath, errors, warnings, summaries, work_dir):
    """Runs all registered emitters, so that user sees the output.
    Main entry point to this module.
    """
    filename = os.path.basename(filepath)

    if errors:
        for func in EMITTERS[ERRORS]:
            func(filename, errors, work_dir=work_dir)

    if warnings:
        for func in EMITTERS[WARNINGS]:
            func(filename, warnings, work_dir=work_dir)

    if summaries:
        for func in EMITTERS[SUMMARIES]:
            func(filename, summaries, work_dir=work_dir)


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
def zenity_emit(filename, errors, **kwargs):
    """Shell to zenity to popup errors.
    """
    for name, errs in errors.items():
        if not errs:
            continue
        cmd = ['/usr/bin/zenity',
            '--error',
            '--title', name +': ' + filename,
            '--text', '\n'.join(errs)]
        shell(cmd)

#-------------
# notify-send for summaries
#------------
@emitter(SUMMARIES)
def notify_emit(filename, summaries, **kwargs):
    """Shell to notify-send for subtle summary notification.
    """

    body = []
    for name, summary in summaries.items():
        body.append(name +': ' + summary)
    cmd = ['/usr/bin/notify-send', filename, ', '.join(body)]
    shell(cmd)

#--------
# An HTML file for warnings
#--------

HTML_TEMPLATE = u"""
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>lintswitch</title>
</head>
<body>
    <div id="logo" style="float:right">
        <a href="https://github.com/grahamking/lintswitch">lintswitch</a>
    </div>
    <h1>{FILENAME}</h1>
    {CONTENTS}
</body>
</html>
"""

@emitter(WARNINGS)
def html_emit(filename, warnings, work_dir=None, **kwargs):
    """Write out warnings to an HTML file, for our web server to pick up.
    """
    html_file = open(os.path.join(work_dir, filename + '.html'), 'wt')

    content = []
    for name, warns in warnings.items():
        if not warns:
            continue

        content.append('<h2>%s</h2>' % name)
        content.append('<table>')
        for line in warns:
            content.append(_as_html_row(line))
        content.append('</table>')

    html = HTML_TEMPLATE.format(FILENAME=filename, CONTENTS='\n'.join(content))
    html_file.write(html)

    html_file.close()


def _as_html_row(line):
    """Warning line as html row"""
    parts = line.split(': ')
    return '<tr><td>{num}</td><td>{msg}</td></tr>'.format(
        num=parts[0], msg=parts[1])

