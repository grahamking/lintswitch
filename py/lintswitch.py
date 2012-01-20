""" lintswitch lints your code in the background.
http://github.com/grahamking/lintswitch
"""

import sys
import socket
from multiprocessing import Queue, Process

from checkers import check
from emitters import emit

import logging

LOG_FILE = '/tmp/lint_switch.log'
LOG = logging.getLogger(__name__)


def main(argv=None):
    """Start here"""
    if not argv:
        argv = sys.argv

    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
    LOG.debug('lintswitch start')

    queue = Queue()
    check_proc = Process(target=worker, args=(queue,))
    check_proc.start()

    listener = socket.socket()
    listener.bind(('127.0.0.1', 4008))
    listener.listen(10)

    try:
        main_loop(listener, queue)
    except KeyboardInterrupt:
        listener.close()
        print('Bye')
        return 0


def main_loop(listener, queue):
    """Wait for connections and process them.
    @param listener a socket.socket, open and listening.
    """

    while True:
        conn, _ = listener.accept()
        data = conn.makefile().read()
        conn.close()

        queue.put(data)


def worker(queue):
    """Takes filename from queue, checks them and displays (emit) result.
    """

    while 1:
        filename = queue.get()
        filename = filename.strip()
        LOG.info(filename)

        errors, warnings, summaries = check(filename)
        emit(errors, warnings, summaries)


if __name__ == '__main__':
    sys.exit(main())
