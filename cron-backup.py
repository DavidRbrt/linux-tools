#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

from datetime import datetime
from filecmp import dircmp

class bcolors:
    HEADER    = '\033[95m'
    BLUE      = '\033[94m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    RED       = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

# HELP
####################################################################################
def help():
    print(sys.argv[0])
    print("Manage crontab backup")
    print("_"*100)
    print("")
    print("Usage : "+sys.argv[0]+" [-h|--help] -d|--dir <file/directory> -b|--backupdir <backup directory> [ -a|--add ] [ -r|--remove ] [ -x|--execute ] \n")
    print("  *  -d|--dir         : [mandatory]   file or directory           (ex : -d /home/g179948/sources/sc-thor2)")
    print("  *  -b|--backupdir   : [mandatory]   backup directory            (ex : -b /home/g179948/backups/auto)")
    print("  *  -a|--add         : add backup to crontab")
    print("  *  -r|--remove      : remove backup from crontab")
    print("  *  -x|--execute     : execute backup")
    print("  *  -h|--help        : display this help\n")

    print("ex : {script} -d {d} -b {b} -a".format(
        script=sys.argv[0],
        b="/home/g179948/backups/auto",
        d="/home/g179948/sources/sc-thor2"))
    print("_"*100)
    print("")


# GET PARAMETERS
####################################################################################
def getParameters():
    ## case help
    if '-h' in sys.argv or '--help' in sys.argv:
        help()
        exit(1)

    ## case action
    action = directory = backup_directory = None

    # get parameters
    if not '-d' in sys.argv:
        print("!! missing directory parameter")
        exit(1)

    if not '-b' in sys.argv:
        print("!! missing backup directory parameter")
        exit(1)

    if '-a' in sys.argv:
        action = "add"

    if '-r' in sys.argv:
        if action is not None:
            print("!! too many actions requested")
            exit(1)
        action = "remove"

    if '-x' in sys.argv:
        if action is not None:
            print("!! too many actions parameters")
            exit(1)
        action = "execute"

    # case no action
    if action is None:
        print("!! no action parameter")
        exit(1)

    # parse arguments (directory, backup_directory)
    for i in range(1,len(sys.argv)):
        if sys.argv[i] == '-d':
            try: directory = sys.argv[i+1]
            except IndexError: directory = None
        if sys.argv[i] == '-b':
            try: backup_directory = sys.argv[i+1]
            except IndexError: backup_directory = None

    return action, directory, backup_directory


# RUN CMD
####################################################################################
def runCmd(cmd):
    print(bcolors.BOLD+"\n--> {}".format(cmd)+bcolors.ENDC)
    try:
        if os.system(cmd) != 0:
            raise Exception('wrong command !')
            exit(1)
    except:
        print(bcolors.BOLD+"\n{}: command failed !".format(cmd)+bcolors.ENDC)
        exit(1)


# GET DATE STRING
####################################################################################
def getDateString():
    now = datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M")


# BUILD CRONTAB LINE
####################################################################################
def buildCrontabLine(directory, backup_directory):
    print("> buildCrontabLine")
    # TODO: get script path
    return "00 13,00 * * * /home/g179948/tools/./cron-backup.py -d {d} -b {b} -x".format(d=directory, b=backup_directory)


# ADD CRONTAB LINE
####################################################################################
def addCrontabLine(crontabLine):
    print("> addCrontabLine")
    runCmd('(sudo crontab -l ; echo "{}")| sudo crontab -'.format(crontabLine))


# REMOVE CRONTAB LINE
####################################################################################
def removeCrontabLine(crontabLine):
    print("> removeCrontabLine")
    # TODO
    #runCmd('sudo crontab -l | grep -v "{}"  | sudo crontab -'.format(crontabLine))


# RELOAD CRONTAB
####################################################################################
def reloadCrontab():
    print("> reloadCrontab")
    runCmd("sudo service cron reload")



####################################################################################
####################################################################################
# MAIN
####################################################################################
if __name__ == "__main__":

    # get parameters
    action, directory, backup_directory = getParameters()

    # display parameters
    print("action:            {a}".format(a=action))
    print("directory:         {d}".format(d=directory))
    print("backup_directory:  {b}".format(b=backup_directory))

    # case add
    ################################################################################
    if action == 'add':
        print("> action add")
        crontabLine = buildCrontabLine(directory, backup_directory)
        print("- crontabLine: {}".format(crontabLine))
        addCrontabLine(crontabLine)
        reloadCrontab()
        exit(0)

    # case remove
    ################################################################################
    if action == 'remove':
        print("> action remove")
        crontabLine = buildCrontabLine(directory, backup_directory)
        print("- crontabLine: {}".format(crontabLine))
        removeCrontabLine(crontabLine)
        reloadCrontab()
        exit(0)

    # case execute
    ################################################################################
    if action == 'execute':
        print("> action execute")

        backup_base_name = directory.replace("/","_")

        # find last backup
        last_backup = None
        backup_file_list = os.listdir(backup_directory)
        backup_file_list = [os.path.join(backup_directory, f) for f in backup_file_list] # add path to each file
        backup_file_list.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        for f in backup_file_list:
            if backup_base_name in f:
                last_backup = f
                break

        print("last backup found: {}".format(last_backup))

        # search for diff between last backup and dir
        dcmp = dircmp(last_backup, directory) 
        
        if dcmp.left_only or dcmp.right_only or dcmp.diff_files or dcmp.funny_files:
            print("diff founds => do backup")

            # do backup
            date = getDateString()
            runCmd("sudo cp -rf {d} {b}/{n}_{da}".format(d=directory, b=backup_directory, n=backup_base_name, da=date))
        else:
            print("no diff founds")

        exit(0)

    # unrecognize case
    ################################################################################
    print("> unrecognize action")
    exit(1)
