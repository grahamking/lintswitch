"""lintswitch: HTTP server to view lint warnings.
"""
# pylint: disable=R0904

import os.path
import socket
import SocketServer
import SimpleHTTPServer
import logging
from Queue import Empty

LOG = logging.getLogger(__name__)
IP = 'localhost'

HTML_PAGE = open(os.path.dirname(__file__) +
                 os.path.sep +
                 "index.html", "rw").read()


def http_server(result_queue, http_port):
    """Start an HTTP server to display emitted HTML files.
    """

    HTTPHandler.queue = result_queue

    httpd = SockServ((IP, http_port), HTTPHandler)
    httpd.serve_forever()


class SockServ(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """Threaded TCPServer which set SO_REUSEADDR on socket"""
    allow_reuse_address = True


class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Pushes files out over HTTP"""

    queue = None

    def do_GET(self):                                   # pylint: disable=C0103
        """Serve a GET request"""

        self.send_response(200)
        self.send_header('Cache-Control', 'no-cache')

        if self.path == '/sse/':
            self.send_header('Content-type', 'text/event-stream')
            self.end_headers()

            while self._is_connected():
                try:
                    html = self.queue.get(timeout=2)
                    self.wfile.write('data: %s\n\n' % html.encode('utf8'))
                    self.wfile.flush()
                except Empty:
                    pass

        else:
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = self.queue.get()

            container = HTML_PAGE.encode('utf8')
            html = container.replace(
                    'Waiting for results...',
                    html.encode('utf8'))

            self.wfile.write(html)
            self.wfile.close()

    def _is_connected(self):
        """Write a comment to the socket to check it's open.

        If it's closed, flushing it with pending data will raise socket.error,
        which we don't care about because we only wrote a PING.
        Closing also calls flush, so we have to catch twice.
        """
        try:
            self.wfile.write(':PING\n\n')
            self.wfile.flush()
            return True
        except socket.error:
            try:
                self.wfile.close()
            except socket.error:
                pass
            raise socket.timeout()

    def log_message(self, logformat, *args):
        """Override default output to use logging module"""
        LOG.info('%s - - [%s] %s',
                 self.address_string(),
                 self.log_date_time_string(),
                logformat % args)
