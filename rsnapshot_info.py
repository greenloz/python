#!/usr/bin/python
#
# Small program that check rsnapshot log with filter of todays date.
# After check, result is mailed to system user.
#
import sys
import datetime
import smtplib
import subprocess
# import shlex : For testing
import syslog


# -- We create a subprocess function
def subCommand(command):
    """Subprocess function, returns output"""
    subCom = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE)
    output = subCom.communicate()[0]
    if subCom.returncode != 0:
        syslog.syslog(syslog.LOG_ERR, "ERROR WHILE PROCESSING BACKUP LOG COMMAND: " + command)
        sys.exit(1)
    return output

# -- Get current time 
now = datetime.datetime.now()

# -- Variables with date, patter, logdata 
today = datetime.datetime.now()
month_name = datetime.datetime.strftime(today, '%b')
date_pattern = 'date' + ' +%d/' + month_name + '/%Y'
grep_pattern = subCommand(date_pattern)
status = subCommand("cat /var/log/rsnapshot.log | grep -i " + grep_pattern)

# -- Mail specific 
smtpserver = '<xxx>'
sender = 'xxx'
to = ['xxx']

# -- If we want to read whole file
# read_file = "/var/log/rsnapshot.log" # Optional logfile
# log_file = open(read_file)
# log_result = status_file.read()

# -- Setup email
subject = 'Rsnapshot log'
dateNow = str(now)[:19]
text = "Status of todays rsnapshot backup: " + dateNow +"\n" + status
headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender, to, subject)
message = headers + text

# -- Sending electronic mail
session = smtplib.SMTP(smtpserver)
#session.login(username, password)
session.sendmail(sender, to, message)
session.quit()

