#!/bin/bash

#
# Installs lintswitch (https://github.com/grahamking/lint_switch)
#


# Installs the packages lintswitch relies upon
install_dependencies() {
    echo ""
    echo "* Using apt-get to install dependencies"
    echo ""
    sudo apt-get install libnotify-bin incron zenity pylint pep8 rhino gconf2 imagemagick subversion
}

# Install Google's closure linter
install_closure() {

    local ignore=$(which gjslint)
    if [ $? -eq 1 ]
    then
        echo ""
        echo "* Installing Google's Closure Linter"
        echo ""

        cd /tmp
        svn checkout http://closure-linter.googlecode.com/svn/trunk/ closure-linter
        cd closure-linter
        sudo python setup.py install
        cd $START_DIR 
    else
        echo "Google Closure Linter already installed"
    fi
}

install_jslint4java() {
    if [ ! -f /usr/local/lib/jslint4java-1.4.4.jar ]
    then
        echo ""
        echo "* Installing jslint4java (command-line version of jslint)"
        echo ""
        cd /tmp
        wget http://jslint4java.googlecode.com/files/jslint4java-1.4.4-dist.zip
        unzip jslint4java-1.4.4-dist.zip 
        cd jslint4java-1.4.4
        sudo cp jslint4java-1.4.4.jar /usr/local/lib/
        cd $START_DIR
    else
        echo "jslint4java already installed"
    fi
}

install_lintswitch() {
    if [ ! -f /usr/local/bin/lintswitch.sh ]
    then
        echo ""
        echo "* Copying lintswitch to /usr/local/bin and lintswitch.conf to /usr/local/etc"
        echo ""

        sudo cp lintswitch.sh /usr/local/bin/
        sudo chmod a+x /usr/local/bin/lintswitch.sh
        sudo cp lintswitch.conf /usr/local/etc/
    else
        echo "lintswitch files already installed"
    fi
}

# Incron needs your name in /etc/incron.allow before you are allowed to use it
allow_me_to_use_incron() {

    local me=$(whoami)
    local already_done=$(sudo cat /etc/incron.allow | grep $me | wc -l)
    if [ "$already_done" -eq 0 ]
    then
        echo ""
        echo "* Adding your username to /etc/incron.allow, so that you can use incron"
        echo ""
        sudo bash -c "echo $me >> /etc/incron.allow"
    else
        echo "You are already permissioned for incron"
    fi
}

add_code_dirs() {
    echo ""
    echo "You now need to pick directories to watch and lint."
    echo ""
    echo "In the dialog that follows, hold down Ctrl to pick all relevant top level project directories."
    echo "These should be the directory that goes on your PYTHONPATH. For example in a Django project select your 'project' directory (not your app directories, and not the directory above your project)".
    echo ""
    echo "If you don't get it right, simply run install again. Or type 'incrontab -e' to edit manually"
    echo ""
    echo ""
    read -n1 -r -p "Press any key to continue..."

    local me=$(whoami)

    local projects=$(zenity --file-selection --directory --multiple --title="Select project directories to lint...")
    local arr=$(echo $projects | tr "|" "\n")

    local incron_lines

    for proj_path in $arr
    do
        incron_lines=$(find $proj_path -name "*.py" -or -name "*.js" -or -name "*.css" | xargs -l1 dirname | sort | uniq | awk "{print \$1 \" IN_ATTRIB /usr/local/bin/lintswitch.sh PATH_VALUES $proj_path \"}")
        sudo bash -c "echo \"$incron_lines\" >> /var/spool/incron/${me}"
        sudo sed --in-place 's/PATH_VALUES/$@\/$#/' /var/spool/incron/${me}
        sudo chown ${me}:incron /var/spool/incron/${me}
    done
}

set_screen_xy() {
    echo ""
    echo "* Setting screen dimensions"
    echo ""

    local dim=$(xdpyinfo | grep dimensions | awk '{print $2}')
    local screenx=$(echo $dim | awk -F x '{print $1}')
    local screeny=$(echo $dim | awk -F x '{print $2}')
    if [ "$screenx" -gt 2000 ]
    then
        local num_screens=$(zenity --list --radiolist --text="How many screens do you have?" --column="Select" --column="Number of screens" TRUE 1 FALSE 2 FALSE 3 FALSE 4)
        screenx=$((screenx/num_screens))
    fi
    screenx=$((screenx-100))
    screeny=$((screeny-100))

    sudo sed --in-place "s/SCREEN_X_GOES_HERE/$screenx/" /usr/local/etc/lintswitch.conf
    sudo sed --in-place "s/SCREEN_Y_GOES_HERE/$screeny/" /usr/local/etc/lintswitch.conf
}

prompt_editor_move_file() {
    echo ""
    echo "* Final step: Check your editor does not move / rename the file you're editing"
    echo "* Vim users will need this in their .vimrc:"
    echo "*   set nobackup"
    echo "*   set nowritebackup"
    echo ""
    echo "lintswitch INSTALL COMPLETED"
}

main() {
    START_DIR=$(pwd)
    install_dependencies
    install_closure
    install_jslint4java
    install_lintswitch
    allow_me_to_use_incron
    add_code_dirs
    set_screen_xy
    prompt_editor_move_file
}

main
