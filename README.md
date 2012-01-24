
*lintswitch* runs pylint, pep8 and pymetrics on your Python code, and jshint on your JS code, in the background.

You must tell lintswitch which files to lint. A **vim** plugin is included, in the contrib directory, which calls lintswitch every time you save a file.

With lintswitch, your code is constantly being watched and linted in the background, without interrupting your workflow. You view the results in a browser.

Linters and file types currently supported:

 - Python: pylint, pep8, pymetrics
 - Javascript: jshint

lintswitch has only been tested on Ubuntu, but in theory should work anywhere Python does, as long as you install the linters.

# Installation

    git clone git://github.com/grahamking/lintswitch.git
    cd lintswitch
    sudo setup.py install

Then copy: _contrib/lintswitch.vim_ to _~/.vim/plugin/_.

# Output

Browse to _localhost:8008_ to view the output. Select the file you're working on. Leave that window open whilst you work - it will auto-update to always display the file you just saved (server-sent events!).

# Configuration

Edit 'config.py'.

# Not using vim?

To use lintswitch from other editors, you need to connect to a socket and send the filename. In Python, that looks like this:

    import socket
    s = socket.create_connection(('127.0.0.1', 4008), 2)
    s.send('%s\n' % full_path_of_file_you_want_to_lint)
    s.close()

If you write a plugin for another editor, please send it my way and I will include it in _contrib_.

## Contribute

I'd love to add linters for other languages, so if you do that locally, please send it my way. Thanks!

