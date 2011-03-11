#!/bin/bash

# Copyright 2010-2011 Graham King <graham@gkgk.org>
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

# gconftool needs to use DBUS, the Gnome message bus. DBUS is per-user,
# and we're in a cron job, so we don't have it set.
# Find gnome-panel (which always runs on Gnome), look in it's environment
# for the variable, and set it here.
configure_dbus() {

    local pid=$(pgrep -u $USER gnome-panel)
    local dbus_addr=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$pid/environ | sed -e 's/DBUS_SESSION_BUS_ADDRESS=//' )
    export DBUS_SESSION_BUS_ADDRESS=$dbus_addr
    echo $DBUS_SESSION_BUS_ADDRESS > /tmp/out.txt
}

display_warnings_in_root_window() {

    # Configure DBUS, which gconftool-2 needs
    if test -z "$DBUS_SESSION_BUS_ADDRESS"
    then
        configure_dbus
        #eval `dbus-launch --sh-syntax`
        #export DBUS_SESSION_BUS_ADDRESS
        #export DBUS_SESSION_BUS_PID
    fi

    # Are there any warnings to display?
    WARN_SIZE=$(stat -c%s $WARNINGS_FILE)
    if [ "$WARN_SIZE" -gt 10 ]
    then
        # Create a picture of the warnings file
        convert -pointsize $ROOT_WIN_FONT_SIZE -size ${SCREEN_X}x${SCREEN_Y} -gravity $ROOT_WIN_GRAVITY -background transparent -fill $ROOT_WIN_TEXT_COLOR label:@$WARNINGS_FILE ${WARNINGS_FILE}.png

        # Set that picture as desktop background
        gconftool-2 --type=str --set /desktop/gnome/background/picture_filename ${WARNINGS_FILE}.png
        gconftool-2 --type=str --set /desktop/gnome/background/picture_options "centered"

    else
        # No warnings, remove background image
        gconftool-2 --type=str --set /desktop/gnome/background/picture_options "none"
    fi
}

main() {
    display_warnings_in_root_window
}

source /usr/local/etc/lintswitch.conf
WARNINGS_FILE=$1    # Arg 1 is warning file with full path

export DISPLAY=":0.0"   # We're running from incrontab, so need to find display

main

