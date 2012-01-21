"""lintswitch: HTTP server to view lint warnings.
"""
# pylint: disable=R0904

import os
import os.path
import SocketServer
import SimpleHTTPServer
import logging

from config import HTTP_PORT
LOG = logging.getLogger(__name__)
IP = 'localhost'


def http_server(page_queue, work_dir):
    """Start an HTTP server to display emitted HTML files.
    """
    os.chdir(work_dir)
    HTTPHandler.work_dir = work_dir
    HTTPHandler.queue = page_queue

    httpd = SockServ((IP, HTTP_PORT), HTTPHandler)
    httpd.serve_forever()


def url(filename):
    """URL at which filename's html results can be found.
    """
    filename = os.path.basename(filename)
    return 'http://%s:%s/%s.html' % (IP, HTTP_PORT, filename)


class SockServ(SocketServer.TCPServer):
    allow_reuse_address = True


class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Pushes files out over HTTP"""

    work_dir = None
    queue = None

    def do_GET(self):
        """Serve a GET request"""

        if self.path == '/sse/':
            self.send_response(200)
            self.send_header('Content-type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()

            filename = self.queue.get()
            self.wfile.write('data: %s\n\n' % filename)
            self.wfile.flush()

        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
