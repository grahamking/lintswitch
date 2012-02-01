
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

**Dependencies**

    sudo apt-get install pymetrics
    sudo pip install pylint
    sudo pip install pep8

Note that 'pymetrics' in pypi (pip) is a different project, and won't work with lintswitch.

For **jshint**:

- install nodejs: `https://github.com/joyent/node/wiki/Installation`
- install jshint: `npm install jshint -g`

**lintswitch** will search your system path and virtualenv bin to find those dependencies.

All depencies are optional - if a linter is absent it will simply be ignored.

# Output

Browse to _localhost:8008_ to view the output. Leave that window open whilst you work - it will auto-update to always display results for the file you just saved (server-sent events!).

If you have Chrome, and click 'Enable Notifications' in the top right of the window, errors will be displaying using desktop notifications.

# Daemonize

In case you find lintswitch so awesome that you want to run it all the time, an [upstart](http://upstart.ubuntu.com/) is included. Copy `contrib/lintswitch.conf` as `/etc/init/lintswitch.conf`, and replace my username / group with yours.

That script will start lintswitch on boot. You can also manage it manually: `sudo [start|stop|restart|status] lintswitch`

# Configuration

All the configuration options are command line switches. See `lintswitch --help` for details.

# Not using vim?

To use lintswitch from other editors, you need to connect to a socket and send the filename. In Python, that looks like this:

    import socket
    s = socket.create_connection(('127.0.0.1', 4008), 2)
    s.send('%s\n' % full_path_of_file_you_want_to_lint)
    s.close()

If you write a plugin for another editor, please send it my way and I will include it in _contrib_.

## Virtualenv aware

If the file being checked is in a virtualenv, lintswitch will also look for the checkers in the virtualenv's bin directory.

## pylint notes

lintswitch will change into the root of your project before running pylint, and use a .pylintrc file if there is one there. The root of your project is determined to be the first directory that does not contain an __init__.py file, i.e. the first directory that is not a python module.

## Contribute

I'd love to add linters for other languages, so if you do that locally, please send it my way. Thanks!

