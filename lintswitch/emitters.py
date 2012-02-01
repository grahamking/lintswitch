"""lintswitch emitters: Parts which output the results of linting / checking.
"""

import logging
import os.path
import datetime

LOG = logging.getLogger(__name__)


def emit(filepath, errors, warnings, summaries):
    """Generate HTML results.  Main entry point to this module.
    """

    log_emit(filepath, summaries=summaries)

    return html_emit(filepath,
                     errors=errors,
                     warnings=warnings,
                     summaries=summaries)


def log_emit(filepath, summaries=None):
    """Write summary to log file at DEBUG level"""
    filename = os.path.basename(filepath)
    body = []
    for name, summary in summaries.items():
        body.append(name + ': ' + summary)
    LOG.debug('%s: %s', filename, ', '.join(body))


#--------
# HTML formatted results
#--------

HTML_CONTENT = u"""<h1>FILENAME</h1><p>Last updated: TIME</p>CONTENT"""


def html_emit(filepath, errors=None, warnings=None, summaries=None):
    """ HTML snippet of results, for our web server to push out.
    """
    content = []

    content.extend(_emit_errors(errors))
    content.extend(_emit_warnings_and_summaries(warnings, summaries))

    if not content:
        content = [u'All good']

    filename = os.path.basename(filepath)

    now = datetime.datetime.now()
    html = [u'<h1>%s</h1>' % filename]
    html.append(u'<p>%s<br>' % filepath)
    html.append(u'Last updated: %s</p>' % now.strftime('%A %d %b, %H:%M'))
    html.extend(content)

    return ''.join(html)


def _emit_errors(errors):
    """Error list as array of HTML strings"""
    if not errors:
        return []

    content = []
    content.append(u'<dl class="errors">')
    for name, err in errors.items():
        content.append(u'<dt>%s</dt><dd>%s</dd>' % (name, '<br/>'.join(err)))
    content.append(u'</dl>')
    return content


def _emit_warnings_and_summaries(warnings, summaries):
    """Warnings and summaries as array of HTML strings"""
    if not warnings:
        return []

    content = []
    for name, warns in warnings.items():
        if not warns:
            continue
        content.append(u'<div class="checker">')

        content.append(u'<h2>%s</h2>' % name)
        if name in summaries:
            content.append(u'<p class="summary">%s</p>' % summaries[name])

        content.append(u'<table>')
        for line in warns:
            content.append(_as_html_row(line))
        content.append(u'</table>')

        content.append(u'</div>')

    return content


def _as_html_row(line):
    """Warning line as html row"""
    parts = line.split(': ')
    return u'<tr><td>{num}</td><td>{msg}</td></tr>'.format(
        num=parts[0], msg=parts[1])

