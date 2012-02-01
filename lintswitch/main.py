""" lintswitch lints your code in the background.
http://github.com/grahamking/lintswitch
"""

import sys
import socket
import logging
import os
import os.path
import argparse
from multiprocessing import Queue, Process

from lintswitch import checkers, emitters, http_server

DESC = 'Linting server - https://github.com/grahamking/lintswitch'
LOG = logging.getLogger(__name__)


def main():
    """Start here"""

    parser = make_parser()
    args = parser.parse_args()

    if args.version:
        from lintswitch import __version__
        print(__version__)
        return 0

    log_params = {'level': args.loglevel}
    if args.logfile:
        log_params['filename'] = args.logfile
    logging.basicConfig(**log_params)                   # pylint: disable=W0142

    LOG.debug('lintswitch start')

    work_queue = Queue()
    result_queue = Queue()

    check_proc = Process(target=worker,
                         args=(work_queue, result_queue, args))
    check_proc.start()

    server = Process(target=http_server.http_server,
                     args=(result_queue, args.httpport))
    server.start()

    # Listen for connections from vim (or other) plugin
    listener = socket.socket()
    listener.bind(('127.0.0.1', args.lintport))
    listener.listen(10)

    try:
        main_loop(listener, work_queue)
    except KeyboardInterrupt:
        listener.close()
        print('Bye')

    return 0


def make_parser():
    """argparse object which can parse command line arguments,
    or print help.
    """

    parser = argparse.ArgumentParser(
            description=DESC,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--version',
            action='store_true',
            help='Print version info and quit')
    parser.add_argument('--loglevel',
            default='DEBUG',
            choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'],
            help='One of DEBUG, INFO, WARN, ERROR or FATAL')
    parser.add_argument('--logfile',
            default=None,
            help='Full path of log file. Defaults to stdout.')
    parser.add_argument('--lintport',
            type=int,
            default=4008,
            help='Port to listen for lint requests')
    parser.add_argument('--httpport',
            type=int,
            default=8008,
            help='Port for web browser interface')
    parser.add_argument('--pymetrics_warn',
            type=int,
            default=5,
            help='Cyclomatic complexity considered a warning, per function')
    parser.add_argument('--pymetrics_error',
            type=int,
            default=10,
            help='Cyclomatic complexity considered an error, per function')

    return parser


def main_loop(listener, work_queue):
    """Wait for connections and process them.
    @param listener: a socket.socket, open and listening.
    """

    while True:
        conn, _ = listener.accept()
        data = conn.makefile().read()
        conn.close()

        work_queue.put(data)


def worker(work_queue, result_queue, args):
    """Takes filename from queue, checks them and displays (emit) result.
    """

    while 1:
        filename = work_queue.get()
        filename = filename.strip()
        if not filename:
            continue

        check_result = checkers.check(filename, args)
        if not check_result:
            continue

        errors, warnings, summaries = check_result
        html = emitters.emit(filename, errors, warnings, summaries)

        result_queue.put(html)


def find(name):
    """Finds a program on system path."""

    for directory in syspath():
        candidate = os.path.join(directory, name)
        if os.path.exists(candidate):
            return candidate

    return None


def syspath():
    """OS path as array of strings"""
    path = os.getenv('PATH').split(':')
    return path


if __name__ == '__main__':
    sys.exit(main())
