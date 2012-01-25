""" lintswitch lints your code in the background.
http://github.com/grahamking/lintswitch
"""

import sys
import socket
import logging
import os
import os.path
from multiprocessing import Queue, Process

import checkers
import emitters
import http_server
from config import LINT_PORT, LOG_LEVEL

LOG = logging.getLogger(__name__)

WORK_DIR = os.path.join(os.path.expanduser('~'), '.lintswitch')


def main():
    """Start here"""

    try:
        log_level = getattr(logging, LOG_LEVEL)
    except AttributeError:
        print("Invalid log level %s. " +
              "Must be one of 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'",
              log_level)
        return 1

    logging.basicConfig(level=log_level)
    LOG.debug('lintswitch start')

    work_dir = WORK_DIR
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    work_queue = Queue()
    page_queue = Queue()

    check_proc = Process(target=worker,
                         args=(work_queue, page_queue, work_dir))
    check_proc.start()

    server = Process(target=http_server.http_server,
                     args=(page_queue, work_dir,))
    server.start()

    # Listen for connections from vim (or other) plugin
    listener = socket.socket()
    listener.bind(('127.0.0.1', LINT_PORT))
    listener.listen(10)

    try:
        main_loop(listener, work_queue)
    except KeyboardInterrupt:
        listener.close()
        print('Bye')

    return 0


def main_loop(listener, work_queue):
    """Wait for connections and process them.
    @param listener: a socket.socket, open and listening.
    """

    while True:
        conn, _ = listener.accept()
        data = conn.makefile().read()
        conn.close()

        work_queue.put(data)


def worker(work_queue, page_queue, work_dir):
    """Takes filename from queue, checks them and displays (emit) result.
    """

    while 1:
        filename = work_queue.get()
        filename = filename.strip()
        if not filename:
            continue

        check_result = checkers.check(filename)
        if not check_result:
            continue

        errors, warnings, summaries = check_result
        emitters.emit(filename, errors, warnings, summaries, work_dir)

        page_queue.put(http_server.url(filename))


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
