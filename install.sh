#!/bin/bash

#
# Installs lintswitch (https://github.com/grahamking/lint_switch)
#


# Installs the packages lintswitch relies upon
install_dependencies() {
    sudo apt-get install libnotify-bin incron zenity pylint pep8 rhino gconf2 imagemagick subversion git-core
}

# Install Google's closure linter
install_closure() {
    cd /tmp
    svn checkout http://closure-linter.googlecode.com/svn/trunk/ closure-linter
    cd closure-linter
    sudo python setup.py install
    cd -
}

install_jslint4java() {
    cd /tmp
    wget http://jslint4java.googlecode.com/files/jslint4java-1.4.4-dist.zip
    unzip jslint4java-1.4.4-dist.zip 
    cd jslint4java-1.4.4
    sudo cp jslint4java-1.4.4.jar /usr/local/lib/
    cd -
}

install_lintswitch() {
    sudo cp lintswitch.sh /usr/local/bin/
    sudo cp lintswitch.conf /usr/local/etc/
}

# Incron needs your name in /etc/incron.allow before you are allowed to use it
allow_me_to_use_incron() {
    local me=$(whoami)
    local already_done=$(sudo cat /etc/incron.allow | grep $me | wc -l)
    if [ -n "$already_done" ]
    then
        sudo bash -c "echo $me >> /etc/incron.allow"
    fi
}

add_code_dirs() {
    echo "You now need to pick directories to watch and lint."
    echo ""
    echo "In the dialog that follows, please use Ctrl to pick all relevant top level project directories."
    echo "These should be the directory that goes on your PYTHONPATH. For example in a Django project select your 'project' directory (not your app directories, and not the directory above your project)".
    echo ""
    echo "If you don't get it right, simply run install again. Or type 'incrontab -e' to edit manually"
    echo ""
    read -n1 -r -p "Press any key to continue..."

    local me=$(whoami)

    local projects=$(zenity --file-selection --directory --multiple --title="Select project directories to lint...")
    local arr=$(echo $projects | tr "|" "\n")

    local incron_lines

    for proj_path in $arr
    do
        incron_lines=$(find $proj_path -name "*.py" -or -name "*.js" -or -name "*.css" | xargs -l1 dirname | sort | uniq | awk "{print \$1 \" IN_ATTRIB /usr/local/bin/lintswitch.sh \$@/\$# $proj_path \"}")
        sudo bash -c "echo \"$incron_lines\" >> /var/spool/incron/${me}"
    done
}

set_screen_xy() {
    local dim=$(xdpyinfo | grep dimensions | awk '{print $2}')
    echo $dim | awk -F x '{print $1}'
    echo $dim | awk -F x '{print $2}'
}

#if [ "$(whoami)" != "root" ]
#then
#    echo "Install must be run as root, because it needs to write to /usr/local/bin and /etc"
#    exit 1
#fi

install_dependencies
install_closure
install_jslint4java
install_lintswitch
allow_me_to_use_incron
add_code_dirs
set_screen_xy

