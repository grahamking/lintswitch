#!/usr/bin/python
"""Writes out an index.html file with all the lints and some javascript
to navigate.
"""

# Copyright 2010-2011 Graham King <graham@gkgk.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# For the full licence see <http://www.gnu.org/licenses/>.

# pylint: disable-msg=R0904

import os
import glob
import time
import datetime
import SocketServer
import SimpleHTTPServer
import shutil

IP = "127.0.0.1"
SCRIPT_PID_FILE = 'lintswitch_display_http.pid'

# Extension that lintswitch.sh gives to the warnings report 
# it writes out in work_dir
WARNINGS_EXT = 'txt'

WARN_TITLE_PREFIX = '**** '
#TABLE_HEADER = '<tr><th>Line</th><th>Message</th></tr>'

CONFIG = '/usr/local/etc/lintswitch.conf'

HTML_TEMPLATE = u"""
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>lintswitch</title>
    <script type='text/javascript'
        src='http://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js'>
    </script>
    <script type='text/javascript'>

        var LATEST = 'LATEST_HERE',
            POLL_INTERVAL = 3000,   /* In millis */
            basename;

        function onNew() {
            window.location.reload();
        }

        function watchForNew() {
            $.ajax({
                url: '/since/' + LATEST,
                statusCode: {200: onNew},
                dataType: 'json'
            });
            setTimeout(watchForNew, POLL_INTERVAL);
        }

        /**
         * Display the warnings associated with given a link.
         */
        function displayWarningsFor(link) {

            link = $(link);

            var fileId = link.data('file'),
                basename = link.data('basename');

            $('ul.toc a').removeClass('active');
            link.addClass('active');

            $('div.warnings').hide();
            $('#'+ fileId).show();

            $('h1').text(basename);
            $('title').text(basename);
        }

        function main() {

            $('ul.toc a').click(function(event){
                event.preventDefault();
                displayWarningsFor(event.target);
            });

            /* Display most recently linted file, i.e. first div */
            displayWarningsFor($('ul.toc a')[0]);

            setTimeout(watchForNew, POLL_INTERVAL);
        }

        $(main);

    </script>
    <style>
        h2:first-child { margin-top: 0; }
        td { border: 1px solid #ccc; }
        tr:nth-child(odd) { background-color: #eee; }
        div.warnings {
            float:right;
            width:70%;
        }
        ul.toc {
            width: 28%;
            float: left;
            margin-top: 0;
            margin-right: 10px;
            overflow: auto;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding-bottom: 20px;
        }
        ul.toc li { list-style-type: none; }
        .active { font-weight: bold; text-decoration: none; }
        #logo { float:right; font-size:small; }
    </style>
</head>
<body>
    <div id="logo">
        <a href="https://github.com/grahamking/lintswitch">lintswitch</a>
    </div>
    <h1>lintswitch</h1>
    CONTENTS_HERE
    <ul class="toc">TOC_HERE</ul>
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
    ordered by last modified date most recent first.
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
            parts = line.split(': ')
            result.append(row_tmpl % (parts[0], parts[1]))

    if result:
        result.append('</table>')
    else:
        result.append('All clear!')

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
    toc_tmpl = (u'<li><a data-file="{file_id}" ' +
                u'data-basename="{basename}" ' +
                u'title="{lastmod}" href="">' +
                u'{filename}</a>: {warn_count}</li>')

    content_tmpl = (u'<div id="{file_id}" class="warnings" ' +
                    u'style="display:none">{file_contents}</div>')

    latest = None

    for lastmod, full_filename, filename in files:

        if not latest:
            latest = lastmod

        handle = open(full_filename, 'rt')
        file_lines = handle.readlines()
        handle.close()

        file_contents = htmlize(file_lines)
        warn_count = warning_count(file_lines)

        # Replace double underscores with slashes, and chop extra extension
        ext_len = len(WARNINGS_EXT) + 1
        filename = filename.replace('__', os.path.sep)[:-ext_len]
        file_id += 1

        basename = filename.split('/')[-1]

        toc.append(
            toc_tmpl.format(
                file_id=str(file_id),
                lastmod=lastmod,
                basename=basename,
                filename=filename,
                warn_count=str(warn_count)))

        contents.append(
            content_tmpl.format(
                file_id=str(file_id),
                file_contents=file_contents))

    html = HTML_TEMPLATE\
                .replace('LATEST_HERE', latest.split(' ')[1])\
                .replace('TOC_HERE', ''.join(toc))\
                .replace('CONTENTS_HERE', ''.join(contents))

    return html


class Server(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Pushes files out over HTTP"""

    work_dir = None
    filename = None

    def do_GET(self):                   # pylint: disable-msg=C0103
        """Serve a GET request."""

        if self.path == '/':
            self.do_root()
        elif self.path.startswith('/since'):
            self.do_since()
        else:
            self.send_response(404)

    def do_root(self):
        """Respond to requests for /"""

        self.send_response(200)
        self.send_header("Content-type", 'text/html')

        warnings_file = open(Server.filename, 'rb')
        fstat = os.fstat(warnings_file.fileno())
        self.send_header("Content-Length", str(fstat[6]))
        self.send_header("Last-Modified",
                         self.date_time_string(fstat.st_mtime))

        self.end_headers()

        shutil.copyfileobj(warnings_file, self.wfile)
        warnings_file.close()

    def do_since(self):
        """Respond to Ajax requests for files
        newer than given date.
        """

        since_str = self.path.split('/')[2]

        since_dt = datetime.datetime.combine(
                        datetime.date.today(),
                        datetime.time(*[int(x) for x in since_str.split(':')]))

        newer = self.find_newer(since_dt)
        if newer:
            print(newer)
            update_index(self.work_dir)

            self.send_response(200)
            self.send_header("Content-type", 'application/json')
            self.end_headers()

            self.wfile.write('{has_new: 1}')
        else:
            self.send_response(304)

    def find_newer(self, since_dt):
        """Files that are newer than given date"""

        result = []

        for filename in glob.glob(self.work_dir + '*.' + WARNINGS_EXT):
            stats = os.stat(filename)
            lastmod_date = datetime.datetime(*time.localtime(stats[8])[:6])
            if lastmod_date > since_dt:
                #lastmod = time.strftime("%Y/%m/%d %H:%M:%S", lastmod_date)
                result.append((filename, lastmod_date.isoformat()))

        return result


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    # Thanks Brandon Craig Rhodes:
    # http://stackoverflow.com/questions/568271/
    try:
        os.kill(int(pid), 0)
    except (OSError, TypeError):
        return False

    return True


def is_running():
    """Is the HTTP server running already"""

    work_dir = get_work_dir()
    if not work_dir[-1] == os.path.sep:
        work_dir += os.path.sep

    pid_filename = work_dir + SCRIPT_PID_FILE
    if os.path.exists(pid_filename):

        current_pid = open(pid_filename, 'rt').read()
        if check_pid(current_pid):
            return True

    pid_file = open(pid_filename, 'wt')
    pid_file.write(str(os.getpid()))
    pid_file.close()

    return False


def update_index(work_dir):
    """Writes out a new index.html.
    @return Full path of index.html file we wrote.
    """
    files = list_files(work_dir, WARNINGS_EXT)
    html = index_html(files)

    filename = work_dir + 'index.html'
    output = open(filename, 'wt')
    output.write(html)
    output.close()

    return filename


def main():
    """Main"""

    work_dir = get_work_dir()

    filename = update_index(work_dir)

    if is_running():
        print('Already running')
    else:
        Server.work_dir = work_dir
        Server.filename = filename
        httpd = SocketServer.TCPServer((IP, 8008), Server)
        httpd.serve_forever()


if __name__ == '__main__':

    # File to display is in sys.argv[1]

    main()

