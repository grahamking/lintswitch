""" lintswitch lints your code in the background.
http://github.com/grahamking/lintswitch
"""

import sys
import socket
import subprocess


def main(argv=None):
    """Start here"""
    if not argv:
        argv = sys.argv

    listener = socket.socket()
    listener.bind(('127.0.0.1', 4008))
    listener.listen(10)
    try:
        main_loop(listener)
    except KeyboardInterrupt:
        listener.close()
        print('Bye')
        return 0

def main_loop(listener):
    """Wait for connections and process them.
    @param listener a socket.socket, open and listening.
    """

    while True:
        conn, _ = listener.accept()
        data = conn.makefile().read()
        conn.close()

        # Probably should run this in separate process or thread
        lint(data)

def lint(filename):
    """Lint given filename"""
    filename = filename.strip()
    print(filename)

    ext = filename.split('.')[-1]
    if ext.lower() != 'py':
        return

    run_pylint(filename)
    #run_pep8(filename)

def run_pylint(filename):
    """Run pylint on given filename"""

    cmd = ['/usr/bin/pylint',
            '--output-format=parseable',
            '--include-ids=y',
            '--reports=y',
            '%s' % filename,
            ]
    stdout, _  = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT).communicate()
    parse_pylint(stdout)

def parse_pylint(lines):
    """Parse pylint output.
    @param lines String of full pylint 'parseable' output.
    """
    """
    local ERRORS=`grep "\[E" $TMP | awk -F : '{print "Line "$2": "$3}'`
    local WARNINGS=`grep ": \[" $TMP | grep -v "Locally disabling" | awk -F : '{print "Line "$2": "$3}'`
    local WARN_LINES=0
    if [ -n "$WARNINGS" ]
    then
        WARN_LINES=`echo "$WARNINGS" | wc -l`
    fi
    add_warnings pylint "$WARNINGS"

    local SUMMARY=`grep "Your code has" $TMP | awk '{print "Rating: "$7" ("$10}'`
    SUMMARY="$SUMMARY\n$WARN_LINES warning(s)"

    local SUMMARY_TITLE="pylint: $filename"

    display_errors "$ERRORS"
    display_summary "$SUMMARY_TITLE" "$SUMMARY"
    """
    print(lines)

if __name__ == '__main__':
    sys.exit(main())
