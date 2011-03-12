#!/usr/bin/python
"""Writes out an index.html file with all the lints and some javascript
to navigate.
"""

import os
import glob
import time

WARN_TITLE_PREFIX = '**** '
#TABLE_HEADER = '<tr><th>Line</th><th>Message</th></tr>'

CONFIG = '/usr/local/etc/lintswitch.conf'

HTML_TEMPLATE = u"""
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>lintswitch</title>
    <script type='text/javascript' src='http://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js'></script>
    <script type='text/javascript'>
        function main() {

            $('a').click(function(event){
                var target = $(event.target),
                    file_id = target.data('file');
                event.preventDefault();
                $('ul a').removeClass('active');
                target.addClass('active');
                $('div.warnings').hide();
                $('#'+ file_id).show();
            });

            /* Display most recently linted file, i.e. first div */
            $($('div.warnings')[0]).show();
            $($('a')[0]).addClass('active');
        }

        $(main);
    </script>
    <style>
        h2:first-child { margin-top: 0; }
        td { border: 1px solid #ccc; }
        tr:nth-child(odd) { background-color: #eee; }
        div {
            float:right;
            width:75%;
            border-left: 1px solid #CCC;
            padding-left:10px;
        }
        ul { width: 25%; }
        .active { font-weight: bold; text-decoration: none; }
    </style>
</head>
<body>
    <h1>lintswitch</h1>
    CONTENTS_HERE
    <ul>TOC_HERE</ul>
</body>
</html>
"""

def get_work_dir():
    """Parse the Bash config file to get work dir"""
    config_file = open(CONFIG, 'rt')
    for line in config_file.readlines():
        if not '=' in line:
            continue

        key, value = line.split('=')
        if key == 'WORK_DIR':

            work_dir = os.path.expandvars(os.path.expanduser(value.strip()))

            if not work_dir.endswith(os.path.sep):
                work_dir += os.path.sep

            return work_dir

    return None


def list_files(work_dir, ext):
    """List of the files in given dir with given extension,
    ordered by creation date most recent first.
    """

    wlen = len(work_dir)

    result = []
    for filename in glob.glob(work_dir + '*.' + ext):
        stats = os.stat(filename)
        lastmod_date = time.localtime(stats[8])
        lastmod = time.strftime("%Y/%m/%d %H:%M:%S", lastmod_date)
        result.append((lastmod, filename, filename[wlen:]))
    result.sort(reverse=True)

    return result


def htmlize(lines):
    """Take an array of lines from a warnings file,
    and turns into an HTML table(s) with titles.
    """


    row_tmpl = u'<tr><td>%s</td><td>%s</td></tr>'

    result = []
    is_in_table = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith(WARN_TITLE_PREFIX):

            if is_in_table:
                result.append(u'</table>')
                is_in_table = False

            title = line[len(WARN_TITLE_PREFIX):].split(':')[0]
            result.append(u'<h2>%s</h2>' % title)
            result.append(u'<table>')
            #result.append(TABLE_HEADER)
            is_in_table = True

        elif 'Line' in line:
            parts = line.split(':')
            result.append(row_tmpl % (parts[0], parts[1]))

    result.append('</table>')
    return ''.join(result)


def warning_count(lines):
    """Counts the number of warnings in the file"""
    warnings = 0
    for line in lines:
        if 'Line' in line:
            warnings += 1
    return warnings


def index_html(files):
    """The HTML for index.html with all files info"""

    toc = []
    contents = []
    file_id = 0
    toc_tmpl = (u'<li><a data-file="{file_id}" title="{lastmod}" href="">' +
                u'{filename}</a>: {warn_count}</li>')

    content_tmpl = (u'<div id="{file_id}" class="warnings" ' +
                    u'style="display:none">{file_contents}</div>')

    for lastmod, full_filename, filename in files:

        handle = open(full_filename, 'rt')
        file_lines = handle.readlines()
        handle.close()

        file_contents = htmlize(file_lines)
        warn_count = warning_count(file_lines)

        filename = filename.replace('_', os.path.sep)
        file_id += 1

        toc.append(
            toc_tmpl.format(
                file_id=str(file_id),
                lastmod=lastmod,
                filename=filename,
                warn_count=str(warn_count)))

        contents.append(
            content_tmpl.format(
                file_id=str(file_id),
                file_contents=file_contents))

    html = HTML_TEMPLATE\
                .replace('TOC_HERE', ''.join(toc))\
                .replace('CONTENTS_HERE', ''.join(contents))

    return html


def main():
    """Main"""

    work_dir = get_work_dir()

    files = list_files(work_dir, 'txt')
    html = index_html(files)

    output = open(work_dir + 'index.html', 'wt')
    output.write(html)
    output.close()


if __name__ == '__main__':

    # File to display is in sys.argv[1]

    main()

