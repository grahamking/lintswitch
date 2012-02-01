"""lintswitch: HTTP server to view lint warnings.
"""
# pylint: disable=R0904

import socket
import SocketServer
import SimpleHTTPServer
import logging
from Queue import Empty

LOG = logging.getLogger(__name__)
IP = 'localhost'


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
        if self.path == '/sse/':
            self.send_response(200)
            self.send_header('Content-type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()

            while self._is_connected():
                try:
                    html = self.queue.get(timeout=2)
                    self.wfile.write('data: %s\n\n' % html.encode('utf8'))
                    self.wfile.flush()
                except Empty:
                    pass

        else:
            self.wfile.write(HTML_PAGE.encode('utf8'))
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


HTML_PAGE = u"""
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>lintswitch</title>
    <link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgBAMAAACBVGfHAAAAAXNSR0IArs4c6QAAABhQTFRFYXAA/v//AAAAwMDAgICAAACAgIAAgAAA1R+gQgAAAAF0Uk5TAEDm2GYAAAAJcEhZcwAACxMAAAsTAQCanBgAAAEmSURBVCjPTdHNbcMwDAVgQoAHoIH0bP2kOUdUMgDF9Gw38QJC0QWyP1BSTuDq5k/vUYIMYCvogn/LlXL9VVrn7TvEWutX5CMM7/2mkegvAD2i+ylqIr4h6W4O18Y61zrO+kShCb/A+qQiYeoQtwSJaGRwNqLkek3VaBp8TzRqEoiK8BG3QyixlrKIQaxcSU5PTSS59UT+sKEdHt7u0XRC3OBu8NMSC1MtL4DP5k7PTFEk3cjATRAoZ+I3mMUSSiw7DE4qkyYy6gus6zxAqElYHgYr4kVZn9mnh0dYF/Y093fA8RsV7BccYQWt4mKAXts2yeNisPjRE1vF48Hg7s5IrFMdYq/ofyKFweCAHSAKTzD7HfQG+t5Lb3TQ8AjuoMfugMHjtv4AC1JIveAm+5gAAAAASUVORK5CYII=" />
    <script type='text/javascript'
        src='http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js'>
    </script>
    <script type='text/javascript'>

        function main() {

            // Server sent events for updates
            var source = new EventSource('/sse/');
            source.addEventListener('message', function(event) {
                $('#container').html(event.data);
                notify();
            }, false);

            if (window.webkitNotifications.checkPermission() == 1) {
                $('#enable_notifications').show();
            }

            $('#enable_notifications').click(function(event) {
                event.preventDefault();
                window.webkitNotifications.requestPermission();
                $('#enable_notifications').hide();
            });
        }

        /* Desktop notification for errors (Chrome only) */
        function notify() {

            var filename = $('h1').text(),
                errCount = $('.errors dt').length,
                notif;

           if (errCount == 0 || !window.webkitNotifications) {
                return;
            }

            notif = window.webkitNotifications.createNotification(
                '', filename, 'Errors: ' + errCount);

            // Close notification after 3 seconds, or on click
            setTimeout(function(){ notif.cancel(); }, 3000);
            notif.onclick = function(event) { notif.cancel() };

            notif.show();
        }

        $(main);
    </script>
    <style>
        body { background-color: whitesmoke; }
        h1 { margin-bottom: 0; }
        h1 + p { margin-top: 0; font-size: small; }
        .errors { border: 2px solid red; padding: 5px; }
        .errors dt { font-weight: bold; }
        h2 { margin-top: 0; padding-top: 0; }
        .checker {
            height: 100%;
            float: left;
            border-right: 1px solid white;
            margin-right: 5px;
        }
        table { height: 100%; }
        .checker:last-child { border-right: none; }
        td { padding: 2px; }
        tr:nth-child(odd) { background:#FFF; }
        tr:nth-child(even) { background:#DDD; }
    </style>
</head>
<body>
    <div id="logo" style="float:right">
        <a href="https://github.com/grahamking/lintswitch">lintswitch</a><br>
        <a id="enable_notifications" href="" style="display:none">
            Enable Notifications
        </a>
    </div>
    <div id="container">Waiting for results...</div>
</body>
</html>
"""
