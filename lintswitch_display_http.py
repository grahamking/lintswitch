#!/usr/bin/python
""" Display a lintswitch output via HTTP.
Listens on 127.0.0.1:8008 and outputs the latest warnings file
whenever a GET is received.
"""

# pylint: disable-msg=R0904

import sys
import os
import SocketServer
import SimpleHTTPServer
import shutil

IP = "127.0.0.1"

CONFIG = '/usr/local/etc/lintswitch.conf'
SCRIPT_PID_FILE = 'lintswitch_display_http.pid'


class Server(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Pushes files out over HTTP"""

    filename = None

    def do_GET(self):                   # pylint: disable-msg=C0103
        """Serve a GET request."""

        self.send_response(200)
        self.send_header("Content-type", 'text/plain')

        warnings_file = open(Server.filename, 'rb')
        fstat = os.fstat(warnings_file.fileno())
        self.send_header("Content-Length", str(fstat[6]))
        self.send_header("Last-Modified",
                         self.date_time_string(fstat.st_mtime))

        self.end_headers()

        shutil.copyfileobj(warnings_file, self.wfile)
        warnings_file.close()


def get_work_dir():
    """Parse the Bash config file to get work dir"""
    config_file = open(CONFIG, 'rt')
    for line in config_file.readlines():
        if not '=' in line:
            continue

        key, value = line.split('=')
        if key == 'WORK_DIR':
            return os.path.expandvars(os.path.expanduser(value.strip()))

    return None


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    # Thanks Brandon Craig Rhodes:
    # http://stackoverflow.com/questions/568271/
    try:
        os.kill(pid, 0)
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


def main(filename):
    """Serve given file on port 8008"""

    if is_running():
        print('Already running')
    else:
        Server.filename = filename
        httpd = SocketServer.TCPServer((IP, 8008), Server)
        httpd.serve_forever()


if __name__ == '__main__':
    main(sys.argv[1])

