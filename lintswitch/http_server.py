"""lintswitch: HTTP server to view lint warnings.
"""
# pylint: disable=R0904

import os
import os.path
import socket
import SocketServer
import SimpleHTTPServer
import logging
from Queue import Empty

LOG = logging.getLogger(__name__)
IP = 'localhost'
port = None

def http_server(page_queue, work_dir, http_port):
    """Start an HTTP server to display emitted HTML files.
    """
    global port
    port = http_port

    os.chdir(work_dir)
    HTTPHandler.work_dir = work_dir
    HTTPHandler.queue = page_queue

    httpd = SockServ((IP, port), HTTPHandler)
    httpd.serve_forever()


def url(filename):
    """URL at which filename's html results can be found.
    """
    filename = os.path.basename(filename)
    return 'http://%s:%s/%s.html' % (IP, port, filename)


class SockServ(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True


class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Pushes files out over HTTP"""

    work_dir = None
    queue = None

    def do_GET(self):
        """Serve a GET request"""
        if self.path == '/sse/':
            filename = None
            self.send_response(200)
            self.send_header('Content-type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()

            while self._is_connected():
                try:
                    filename = self.queue.get(timeout=2)
                    self.wfile.write('data: %s\n\n' % filename)
                    self.wfile.flush()
                except Empty:
                    pass

        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

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

    def log_message(self, format, *args):
        """Override default output to use logging module"""
        LOG.info('%s - - [%s] %s',
                 self.address_string(),
                 self.log_date_time_string(),
                format % args)
