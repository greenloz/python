#!/usr/bin/python
# APT UPGRADE SCRIPT
#
import os
import subprocess
import re
import sys
import syslog

my_hostname = os.uname()[1]
apt_update = 'apt-get update > /dev/null 2>&1'
apt_upgrade = 'apt-get dist-upgrade -y > /dev/null 2>&1'
apt_clean = 'apt-get autoclean -y > /dev/null 2>&1'
apt_remove = 'apt-get autoremove -y > /dev/null 2>&1'
apt_kernel = 'apt-get upgrade -s |grep "linux-image.\+-amd64" |wc -l'
apt_reboot = '/sbin/reboot'

def subCommand(command):
    subCom = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output = subCom.communicate()[0]
    if subCom.returncode != 0:
        syslog.syslog(syslog.LOG_ERR, "ERROR WHILE PROCESSING COMMAND: " + command)
        sys.exit(1)
    else:
        syslog.syslog(syslog.LOG_INFO, "PROCESSING COMMAND: " + command)
    return output

def chKern():
    kernCheck = int(subCommand(apt_kernel))
    if kernCheck != 0:
        return 1
    else:
        return 0

def aptUpgrade():
    return subCommand(apt_upgrade)


def rebHandle(value):
    if value == 1:
        subCommand(apt_reboot)
        syslog.syslog(syslog.LOG_INFO, "NEW KERNEL INSTALLED, REBOOTING SYSTEM: " + apt_reboot)
    else:
        pass

# --- MAIN ---
if __name__ == "__main__":
    # First we update against repository
    subCommand(apt_update)

    # Check if a new kernel is released
    if chKern() == 1:
        reboot_flag = 1
        syslog.syslog(syslog.LOG_INFO, "Starting apt-get dist-upgrade of system, new kernel found... ")
        subCommand(apt_upgrade)
        #if my_hostname == 'proxbase':
        rebHandle(reboot_flag)
    else:
        reboot_flag = 0
        syslog.syslog(syslog.LOG_INFO, "Starting apt-get dist-upgrade of system...")
        subCommand(apt_upgrade)
        subCommand(apt_clean)
        subCommand(apt_remove)

