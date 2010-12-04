#!/bin/bash


# Copyright 2010 Graham King <graham@gkgk.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# For the full licence see <http://www.gnu.org/licenses/>.


# Requirements:
# > sudo apt-get install libnotify-bin incron zenity pylint pep8 rhino root-tail psmisc
#
# libnotify-bin gives us notify-send
# psmisc gives us killall
# rhino is needed to run jslint
#
# To get jslint:
# > cd $TOOL_DIR
# > wget http://www.jslint.com/rhino/jslint.js
#
# To get Google Closure Lint:
# > cd <temp_dir>
# > svn checkout http://closure-linter.googlecode.com/svn/trunk/ closure-linter
# > cd closure-linter
# > python setup.py install


run_pylint() {

    /usr/bin/pylint --output-format parseable --include-ids y --reports y $fullfile > $TMP 

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
}

run_pep8() {

    local WARNINGS=`/usr/bin/pep8 --ignore=W391,W291 --repeat $fullfile | awk -F : '{print "Line "$2", char "$3": "$4 }'`
    local WARN_LINES=0
    if [ -n "$WARNINGS" ]
    then
        WARN_LINES=`echo "$WARNINGS" | wc -l`
    fi
    add_warnings pep8 "$WARNINGS"

    local SUMMARY="$WARN_LINES warning(s)"
    local SUMMARY_TITLE="pep8: $filename"
    display_summary "$SUMMARY_TITLE" "$SUMMARY"
}

run_jslint() {

    /usr/bin/rhino $TOOL_DIR/jslint.js $fullfile > $TMP

    local ERRORS=`grep "Stopping, unable to continue" $TMP`
    local WARNINGS=`grep "Lint at" $TMP`
    local WARN_LINES=0
    if [ -n "$WARNINGS" ]
    then
        WARN_LINES=`echo "$WARNINGS" | wc -l`
    fi
    add_warnings jslint "$WARNINGS"

    local SUMMARY="$WARN_LINES warning(s)"
    local SUMMARY_TITLE="jslint: $filename"

    display_errors "$ERRORS"
    display_summary "$SUMMARY_TITLE" "$SUMMARY"
}

run_gjslint() {

    local WARNINGS=`/usr/local/bin/gjslint $fullfile | grep "Line "`
    local WARN_LINES=0
    if [ -n "$WARNINGS" ]
    then
        WARN_LINES=`echo "$WARNINGS" | wc -l`
    fi
    add_warnings jslint "$WARNINGS"

    local SUMMARY="$WARN_LINES warning(s)"
    local SUMMARY_TITLE="gjslint: $filename"

    if [ "$WARN_LINES" -gt 30 ]
    then
        SUMMARY="$SUMMARY - Try running 'fixjsstyle $filename'"
    fi

    display_summary "$SUMMARY_TITLE" "$SUMMARY"
}

# Display summary as a notification, subtle.
display_summary() {
    notify-send "$1" "$2"
}

# Display errors as a popup that steals focus. No ignoring this.
display_errors() {
    if [ -n "$1" ]
    then
        zenity --error --title="Lint errors" --text="$1"
    fi
}

# Add some warnings to the warnings file
# Args are 1=linter_name 2=warnings
# add_warnings pylint "$WARNINGS"
add_warnings() {

    if [ -n "$2" ]
    then
        echo "**** $1: $filename" >> $WARNINGS_FILE
        echo "$2" >> $WARNINGS_FILE
    fi
}

display_warnings() {
    killall root-tail   # Clear the root window

    # Are there any warnings to display?
    WARN_SIZE=$(stat -c%s $WARNINGS_FILE)
    if [ "$WARN_SIZE" -gt 10 ]
    then

        # How big should the root window be?
        local WIN_HEIGHT=$((100 + 22 * `cat $WARNINGS_FILE | wc -l`))

        # Use root-tail to show warnings on root window (desktop background)
        root-tail -g 850x$WIN_HEIGHT-30+100 --fork --font 10x20 --interval 3600 $WARNINGS_FILE 
    fi
}

#
# Main
#
main() {

    local extension=${filename##*.}       # Get the extension
    local active=0

    cd $cwd

    # Is it Python?
    if [ "$extension" = "py" ]
    then
        active=1
        run_pylint
        run_pep8

    # Is it Javascript?
    elif [ "$extension" = "js" ]
    then
        active=1
        run_jslint
        run_gjslint

    # Is it CSS?
    elif [ "$extension" = "css" ]
    then
        active=1
        run_jslint
    fi

    if [ $active ] # Did we actually do anything?
    then
        display_warnings
    fi
}

fullfile=$1     # Arg 1 is filename with full path
cwd=$2          # Arg 2 is working directoy to lint that file
filename=$(basename $fullfile)  # Strip path to retain only filename

TMP=/tmp/lint_switch.txt        # Scratch file
TOOL_DIR=/home/graham/bin       # Where various lint programs are

WARNINGS_FILE=/tmp/lint_switch_warnings.txt # Warnings from all linters
echo '' > $WARNINGS_FILE                    # Wipe the file

export DISPLAY=":0.0"   # We're running from incrontab, so need to find display

main

