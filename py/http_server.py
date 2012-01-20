
import os
import os.path
import shutil
import SocketServer
import SimpleHTTPServer


def http_server(work_dir):
    """Start an HTTP server to display emitted HTML files.
    """
    #Server.work_dir = work_dir
    os.chdir(work_dir)
    httpd = SocketServer.TCPServer(('127.0.0.1', 8008), SimpleHTTPServer.SimpleHTTPRequestHandler)
    httpd.allow_reuse_address = True
    httpd.serve_forever()


class Server(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Pushes files out over HTTP"""

    work_dir = None

    def do_GET(self):
        """Serve a GET request"""
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

