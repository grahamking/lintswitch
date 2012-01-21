
import os
import os.path
#import shutil
import SocketServer
import SimpleHTTPServer
import logging

LOG = logging.getLogger(__name__)
IP = 'localhost'
PORT = 8005


def http_server(page_queue, work_dir):
    """Start an HTTP server to display emitted HTML files.
    """
    os.chdir(work_dir)
    HTTPHandler.work_dir = work_dir
    HTTPHandler.queue = page_queue

    httpd = SockServ((IP, PORT), HTTPHandler)
    httpd.serve_forever()


def url(filename):
    """URL at which filename's html results can be found.
    """
    filename = os.path.basename(filename)
    return 'http://%s:%s/%s.html' % (IP, PORT, filename)


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

        """
        self.send_response(200)
        self.send_header("Content-type", 'text/html')

        warnings_file = open(os.path.join(self.work_dir, 'emitters.py.html'), 'rb')
        fstat = os.fstat(warnings_file.fileno())
        self.send_header("Content-Length", str(fstat[6]))
        self.send_header("Last-Modified",
                         self.date_time_string(fstat.st_mtime))

        self.end_headers()

        shutil.copyfileobj(warnings_file, self.wfile)
        warnings_file.close()
        """

