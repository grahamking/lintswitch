
# Summary

*lintswitch* is a small Bash script that connects:

1. _incron_ which watches your files
1. _pylint_, _jslint_ and other linters, which warn you about possible problems
in your files
1. _zenity_, _notify-send_, and _imagemagick_, which display the lint result.

The result is that your code is constantly being watched and linted,
in the background, without interrupting your workflow, unless
there is an error in your code.

Linters and file types currently supported:

 - Python: pylint, pep8
 - Javascript: jslint, gjslint (Google Closure's Linter)
 - CSS: jslint (yes jslint lint's CSS too)

lintswitch requires Gnome, and has only been tested on Ubuntu.

# Installation

    git clone git://github.com/grahamking/lint_switch.git
    cd lint_switch
    ./install.sh

## Test it

Open a python, javascript or css file in your favorite editor, and save it. 
You should see:

- If lint found an error: a modal popup.
- If lint found some warnings: A Gnome notification, and details written
directly on your desktop (root window).
- If lint is happy: Just a notification. Good job.

# Misc.

## Configure and Customise

The config file is `/usr/local/etc/lintswitch.conf` - syntax is bash script 

All lintswitch does does is wire together a number of other tools. It's just bash script, and there are lots of comments. Hopefully you can customise it for your particular situation.

## Contribute

I'd love to add linters for other languages, so if you do that locally, please send me a patch. Thanks!

## Help, make the root window warnings go away!

Once you are done working, you probably want to clear any remaining warnings from your root window. Simply right-click on it, Change Desktop Background, and select the background you had before.

