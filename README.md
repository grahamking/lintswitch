
*lintswitch* runs pylint, pep8 and pymetrics on your Python code, in the background.

You must tell lintswitch which files to lint. A **vim** plugin is included, in the contrib directory, which calls lintswitch every time you save a file.

With lintswitch, your code is constantly being watched and linted in the background, without interrupting your workflow, unless there is an error in your code.

Linters and file types currently supported:

 - Python: pylint, pep8, pymetrics

lintswitch has only been tested on Ubuntu, but in theory should work anywhere Python does, assuming you customise the emitters.

# Installation

    git clone git://github.com/grahamking/lintswitch.git
    cd lintswitch
    sudo setup.py install

# Configuration

Edit 'config.py'.

lintswitch has two key concepts: **checkers**, and **emitters**.

Checkers are the things that check your code: pylint, pep8, etc.

Emitters are things that tell you if you did something wrong. By default lintswitch will call:

- zenity to popup any errors
- notify-bin for subtle gnome notifications of a summary
- and serves html results on port 8008, with auto refresh (server-sent events!).

# Not using vim?

To use lintswitch from other editors, you need to connect to a socket and send the filename. In Python, that looks like this:

    import socket
    s = socket.create_connection(('127.0.0.1', 4008), 2)
    s.send('%s\n' % full_path_of_file_you_want_to_lint)
    s.close()

If you write a plugin for another editor, please send it my way and I will include it in _contrib_.

## Contribute

I'd love to add linters for other languages, so if you do that locally, please send it my way. Thanks!

