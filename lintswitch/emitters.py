"""lintswitch emitters: Parts which output the results of linting / checking.
"""

import logging
import subprocess
import os.path
import datetime

LOG = logging.getLogger(__name__)


def emit(filepath, errors, warnings, summaries, work_dir):
    """Runs all registered emitters, so that user sees the output.
    Main entry point to this module.
    """
    filename = os.path.basename(filepath)

    for func in [log_emit, html_emit]:

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


def log_emit(filename, summaries=None, **kwargs):      # pylint: disable=W0613
    """Write summary to log file at DEBUG level"""
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
    <link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgBAMAAACBVGfHAAAAAXNSR0IArs4c6QAAABhQTFRFYXAA/v//AAAAwMDAgICAAACAgIAAgAAA1R+gQgAAAAF0Uk5TAEDm2GYAAAAJcEhZcwAACxMAAAsTAQCanBgAAAEmSURBVCjPTdHNbcMwDAVgQoAHoIH0bP2kOUdUMgDF9Gw38QJC0QWyP1BSTuDq5k/vUYIMYCvogn/LlXL9VVrn7TvEWutX5CMM7/2mkegvAD2i+ylqIr4h6W4O18Y61zrO+kShCb/A+qQiYeoQtwSJaGRwNqLkek3VaBp8TzRqEoiK8BG3QyixlrKIQaxcSU5PTSS59UT+sKEdHt7u0XRC3OBu8NMSC1MtL4DP5k7PTFEk3cjATRAoZ+I3mMUSSiw7DE4qkyYy6gus6zxAqElYHgYr4kVZn9mnh0dYF/Y093fA8RsV7BccYQWt4mKAXts2yeNisPjRE1vF48Hg7s5IrFMdYq/ofyKFweCAHSAKTzD7HfQG+t5Lb3TQ8AjuoMfugMHjtv4AC1JIveAm+5gAAAAASUVORK5CYII=" />
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
        h1 { margin-bottom: 0; }
        h1 + p { margin-top: 0; font-size: small; }
        .errors { border: 2px solid red; padding: 5px; }
        .errors dt { font-weight: bold; }
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
    <p>Last updated: TIME</p>
    CONTENT
</body>
</html>
"""


def html_emit(
        filename,
        errors=None,
        warnings=None,
        summaries=None,
        work_dir=None,
        **kwargs):                                  # pylint: disable=W0613
    """Write out warnings to an HTML file, for our web server to pick up.
    """
    html_file = open(os.path.join(work_dir, filename + '.html'), 'wt')
    content = []

    content.extend(_emit_errors(errors))
    content.extend(_emit_warnings_and_summaries(warnings, summaries))

    if not content:
        content = ['All good']

    now = datetime.datetime.now()
    html = HTML_TEMPLATE.replace('FILENAME', filename)\
                        .replace('TIME', now.strftime('%A %d %b, %H:%M'))\
                        .replace('CONTENT', '\n'.join(content))
    html_file.write(html)

    html_file.close()


def _emit_errors(errors):
    """Error list as array of HTML strings"""
    if not errors:
        return []

    content = []
    content.append('<dl class="errors">')
    for name, err in errors.items():
        content.append('<dt>%s</dt><dd>%s</dd>' % (name, '<br/>'.join(err)))
    content.append('</dl>')
    return content


def _emit_warnings_and_summaries(warnings, summaries):
    """Warnings and summaries as array of HTML strings"""
    if not warnings:
        return []

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

    return content


def _as_html_row(line):
    """Warning line as html row"""
    parts = line.split(': ')
    return '<tr><td>{num}</td><td>{msg}</td></tr>'.format(
        num=parts[0], msg=parts[1])

