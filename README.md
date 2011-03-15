
# Summary

*lintswitch* is a small Bash script that connects:

1. _incron_ which watches your files
1. _pylint_, _jslint_ and other linters, which warn you about possible problems
in your files
1. _zenity_, _notify-send_, and _python_, which display the lint result.

The result is that your code is constantly being watched and linted,
in the background, without interrupting your workflow, unless
there is an error in your code.

Linters and file types currently supported:

 - Python: pylint, pep8
 - Javascript: jslint, gjslint (Google Closure's Linter)
 - CSS: jslint (yes jslint lint's CSS too)

lintswitch requires Gnome (for notifications), 
and has only been tested on Ubuntu. In theory it
should work on any modern Gnome based Linux.

# Installation

    git clone git://github.com/grahamking/lintswitch.git
    cd lintswitch
    ./install.sh

## Test it

Open a python, javascript or css file in your favorite editor, and save it. 
You should see:

- If lint found an error: a modal popup.
- If lint found some warnings: A Gnome notification.
- If lint is happy: Just a notification. Good job.

To view the warnings, browse to http://localhost:8008
Leave your browser window open, it will refresh as needed.

## How it works

**incrontab** uses Linux's inotify feature, to watch your code files. 
When a file changes, the kernel wakes up incrontab, which consults it's config 
(edited via incrontab -e), and runs the relevant command.

The relevant command in our case is **lintswitch.sh**. That bash script checks
the modified file's extension, and runs the relevant linters (**pylint**, **jslint**, etc) on it,
capturing their output.

Using grep and awk, we deduce whether there were any errors, and how many
warnings, if any, there were.

Errors are displayed in a modal popup using **zenity**. A summary of the
warnings count is displayed as a gnome notification, using **notify-send**.

Finally we start a separate (configurable in lintswitch.conf) script to display the warnings. There
are three different ways to display the warnings included. The default is
in a browser.

We format the warnings as an index.html file which we save to our work directory,
then use **python's built-in http server** to start a server on localhost:8008.

The index.html includes some **jquery javascript** to check whether any
new warnings have been written to disk, and if so we simply reload the page
to get the new index.html.

The two other included ways to display the warnings are:

 - Using **alltray** and **gedit** to simply open them as a text file and
 lodge gedit in your systems tray.

 - Using **imagemagick** and **gconf2** to turn the text into a png and
 make it your wallpaper (i.e. paint the root window).

# Misc.

## Better notifications

lintswitch makes heavy use of the notification system. Ubuntu's notifications can't display more than one thing at a time, so I recommend switching to Gnome's notifications. See [Improved Ubuntu notifications: gnome-stracciatella-session](http://www.darkcoding.net/software/improved-ubuntu-notifications-gnome-stracciatella-session/) for how to set that up.

## Configure and Customise

The config file is `/usr/local/etc/lintswitch.conf` - syntax is bash script 

All lintswitch does does is wire together a number of other tools. It's just bash script, and there are lots of comments. Hopefully you can customise it for your particular situation.

## Debug

incron logs the command it runs to the syslog (/var/log/syslog). If it's not working, try running that command manually.

## Contribute

I'd love to add linters for other languages, so if you do that locally, please send me a patch. Thanks!

