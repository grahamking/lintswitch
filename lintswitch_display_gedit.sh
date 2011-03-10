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

display_warnings_in_gedit() {
    # You need alltray to use this: sudo apt-get install alltray
    kill `ps -ef | grep alltray | grep gedit | awk '{print $2}'`
    alltray --sticky gedit ${WARNINGS_FILE}
}

main() {
    display_warnings_in_gedit
}

source /usr/local/etc/lintswitch.conf
WARNINGS_FILE=$1    # Arg 1 is warning file with full path

export DISPLAY=":0.0"   # We're running from incrontab, so need to find display

main

