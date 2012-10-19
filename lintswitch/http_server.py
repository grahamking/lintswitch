"""lintswitch: HTTP server to view lint warnings.
"""
# pylint: disable=R0904

import os.path
import socket
import SocketServer
import SimpleHTTPServer
import logging
from threading import Condition

LOG = logging.getLogger(__name__)
IP = 'localhost'

HTML_PAGE = open(os.path.dirname(__file__) +
                 os.path.sep +
                 "index.html", "rw").read()

# Shared memory between threads. HTML of results gets written here
SHARED_RESULT = None

# Condition which tells us when SHARED_RESULT changes
SHARED_CONDITION = Condition()


def http_server(http_port):
    """Start an HTTP server to display emitted HTML files.
    """

    httpd = SockServ((IP, http_port), HTTPHandler)
    httpd.serve_forever()


class SockServ(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """Threaded TCPServer which sets SO_REUSEADDR on socket"""
    allow_reuse_address = True
    daemon_threads = True


class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Pushes files out over HTTP"""

    def do_GET(self):                                   # pylint: disable=C0103
        """Serve a GET request"""

        self.send_response(200)
        self.send_header('Cache-Control', 'no-cache')

        SHARED_CONDITION.acquire()

        if self.path == '/sse/':
            self.send_header('Content-type', 'text/event-stream')
            self.end_headers()

            while True:
                if SHARED_RESULT:
                    try:
                        self.wfile.write('data: {}\n\n'
                                         .format(SHARED_RESULT.encode('utf8')))
                        self.wfile.flush()
                    except socket.error:
                        try:
                            self.wfile.close()
                        except:
                            pass
                        break

                SHARED_CONDITION.wait(None)

        else:
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            if not SHARED_RESULT:
                # Wait for someting to display
                SHARED_CONDITION.wait(None)

            container = HTML_PAGE.encode('utf8')
            html = container.replace(
                'Waiting for results...',
                SHARED_RESULT.encode('utf8'))

            self.wfile.write(html)
            self.wfile.close()

        SHARED_CONDITION.release()

        # If Server-Sent Events connection, raise timeout so SocketServer
        # doesn't print a stacktrace
        if self.path == '/sse/':
            raise socket.timeout()

    def log_message(self, logformat, *args):
        """Override default output to use logging module"""
        LOG.info('%s - - [%s] %s',
                 self.address_string(),
                 self.log_date_time_string(),
                 logformat % args)
