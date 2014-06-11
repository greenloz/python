#!/usr/bin/python
import sys
import os
import logging
import subprocess
import time
import datetime
 
# Simple script to handle PPTP on Asus-RT-N66U
#
# -- Variables -- #
serverIP = "IP TO ASUS_ROUTER"

connectSSH = "ssh -i "

sshKey = "YOUR KEY "

userName = "-ladmin "

preConnect = connectSSH + sshKey + userName + serverIP

startProcess = preConnect + " \"/usr/sbin/pptpd -c /tmp/pptpd/pptpd.conf -o /tmp/pptpd/options.pptpd\""

statusPid = preConnect + " \"ps |grep pptp |grep -v grep |awk -F' ' '{print \$1}'\""

stopProcess = preConnect

# Logging config
logFileName = "pptpd_config.log"
logging.basicConfig(filename=logFileName, level=logging.INFO)

def subCommand(command):
    """
    subprocess function
    """
    subPipe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output = subPipe.communicate()[0]
    if subPipe.returncode != 0:
        logging.error(getToday() + " Error while processing command: " + command)
        sys.exit(1)
    return output.decode()

def getCommand(command):
    commandString = "unknown"
    if command == "status":
        commandString = statusPid
    if command == "start":
        if subCommand(statusPid) != "":
            logging.info(getToday() + " Process already running...")
            sys.exit(0)
        else:
            commandString = startProcess
    if command == "stop":
        if subCommand(statusPid) != "":
            commandString = stopProcess + " " + "\"kill -15 " + subCommand(statusPid) + "\""
        else:
            #print("Nothing to stop...")
            logging.info(getToday() + " Nothing to stop, process not running")
            sys.exit(0)
    return commandString

def postCheck(command, pid):
    if pid != "":
        logging.info(getToday() + " Process is running with pid: " + pid)
        #print("Process is running with pid: " + pid)
    else:
        logging.info(getToday() + " Process not running...")
        #print("Process not running...")

def preCheck(command):
    executeCom = getCommand(command)
    if executeCom != "unknown":
        logging.info(getToday() + " Connecting router: Task -> " + command)
        #print("Connecting router: Task -> " + command)
        if command != "status":
            subCommand(executeCom)
        postCheck(command, subCommand(getCommand("status")))
    else:
        logging.error(getToday() + " Unknown command " + command + ". Stopping execution...")
        #print("Unknown command " + command + ". Stopping execution...")
        sys.exit(1)

def getToday():
    return str(datetime.datetime.now())

 ## --- M A I N  ---##
if len(sys.argv) < 3 and len(sys.argv) > 1:
    preCheck(sys.argv[1])
else:
    print("Usage: " + __file__ + " <command>  ; Commands: start, stop, status")
    sys.exit(0)
