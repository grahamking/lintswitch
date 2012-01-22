"""lintswitch emitters: Parts which output the results of linting / checking.
"""

import logging
import subprocess
import os.path

from config import ZENITY_CMD, NOTIFY_CMD, EMITTERS

LOG = logging.getLogger(__name__)


def emit(filepath, errors, warnings, summaries, work_dir):
    """Runs all registered emitters, so that user sees the output.
    Main entry point to this module.
    """
    filename = os.path.basename(filepath)

    for func_name in EMITTERS:
        try:
            func = globals()[func_name]
        except KeyError:
            LOG.error('Could not find function "%s" in emitters.py', func_name)
            continue

        func(filename,
             errors=errors,
             warnings=warnings,
             summaries=summaries,
             work_dir=work_dir)


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
def zenity_emit(filename, errors=None, **kwargs):   # pylint: disable=W0613
    """Shell to zenity to popup errors.
    """
    for name, errs in errors.items():
        if not errs:
            continue
        cmd = [ZENITY_CMD,
            '--error',
            '--title', name + ': ' + filename,
            '--text', '\n'.join(errs)]
        shell(cmd)


#-------------
# notify-send for summaries
#------------
def notify_emit(filename, summaries=None, **kwargs):   # pylint: disable=W0613
    """Shell to notify-send for subtle summary notification.
    """

    body = []
    for name, summary in summaries.items():
        body.append(name + ': ' + summary)
    cmd = [NOTIFY_CMD, filename, ', '.join(body)]
    shell(cmd)


def log_emit(filename, summaries=None, **kwargs):      # pylint: disable=W0613
    body = []
    for name, summary in summaries.items():
        body.append(name + ': ' + summary)
    LOG.debug('%s: %s', filename, ', '.join(body))


#--------
# An HTML file for warnings
#--------

HTML_TEMPLATE = u"""
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>lintswitch</title>
    <script type='text/javascript'
        src='http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js'>
    </script>
    <script type='text/javascript'>
        var source = new EventSource('/sse/');
        source.addEventListener('message', function(event) {
            console.log(event.data);
            window.location = event.data;
        }, false);
    </script>
    <style>
        body { background-color: whitesmoke; }
        h2 { margin-top: 0; padding-top: 0; }
        .checker {
            height: 100%;
            float: left;
            border-right: 1px solid white;
            margin-right: 5px;
        }
        table { height: 100%; }
        .checker:last-child { border-right: none; }
        td { padding: 2px; }
        tr:nth-child(odd) { background:#FFF; }
        tr:nth-child(even) { background:#DDD; }
    </style>
</head>
<body>
    <div id="logo" style="float:right">
        <a href="https://github.com/grahamking/lintswitch">lintswitch</a>
    </div>
    <h1>FILENAME</h1>
    CONTENTS
</body>
</html>
"""


def html_emit(
        filename,
        warnings=None,
        summaries=None,
        work_dir=None,
        **kwargs):                                  # pylint: disable=W0613
    """Write out warnings to an HTML file, for our web server to pick up.
    """
    html_file = open(os.path.join(work_dir, filename + '.html'), 'wt')

    content = []
    for name, warns in warnings.items():
        if not warns:
            continue
        content.append('<div class="checker">')
        content.append('<h2>%s</h2>' % name)
        if name in summaries:
            content.append('<p class="summary">%s</p>' % summaries[name])
        content.append('<table>')
        for line in warns:
            content.append(_as_html_row(line))
        content.append('</table>')
        content.append('</div>')

    if not content:
        content = ['All good']

    html = HTML_TEMPLATE.replace('FILENAME', filename)\
                        .replace('CONTENTS', '\n'.join(content))
    html_file.write(html)

    html_file.close()


def _as_html_row(line):
    """Warning line as html row"""
    parts = line.split(': ')
    return '<tr><td>{num}</td><td>{msg}</td></tr>'.format(
        num=parts[0], msg=parts[1])

