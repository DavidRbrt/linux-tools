#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re, shutil

class bcolors:
    HEADER    = '\033[95m'
    BLUE      = '\033[94m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    RED       = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

# ----------------------------------------------------------------------
def usage():
    print(sys.argv[0])
    print("clone a svn-module branch to a local git repo")
    print("-"*100)
    print("Usage : "+sys.argv[0]+" [-h|--help] -f <forge_url> -s <svn_module> -b <svn_branch> [ -g <git_module> ] [ -v ] \n")
    print("  *  -f          : forge url                                                        (ex : https://forge-urd44.osn.sagem)")
    print("  *  -s          : [mandatory]   svn module name                                    (ex : sc.stb-lib-opal)")
    print("  *  -b          : [mandatory]   svn branch name                                    (ex : BO_sc.stb-lib-opal)")
    print("  *  -g          : [facultative] git module name (WITHOUT the '.git' extension !)   (ex : opal)")
    print("                   by default, $(git_module)=$(svn_module).git")
    print("  *  -v          : [facultative] increase verbosity")
    print("  *  -h|--help   : display this help\n")

    print("ex : {script} -f {f} -s {s} -b {b} -g {g} -v".format(
        script=sys.argv[0],
        f="https://forge-urd44.osn.sagem",
        s="sc.stb-lib-opal",
        b="BO_sc.stb-lib-opal",
        g="opal"))
    print("-"*100)
    exit(1)


# ----------------------------------------------------------------------
def get_params():
    """
        get input params :
            - forge_url
            - svn_module
            - svn_branch
            - git_module
    """

    # init params
    forge_url = svn_module = svn_branch = git_module = None
    VERBOSE = False

    # help ?
    if '-h' in sys.argv or '--help' in sys.argv:
        usage()

    # parse arguments (forge_url | svn_module | git_module)
    for i in range(1,len(sys.argv)):
        if sys.argv[i] == '-f':
            try: forge_url = sys.argv[i+1]
            except IndexError: forge_url = None
        if sys.argv[i] == '-s':
            try: svn_module = sys.argv[i+1]
            except IndexError: svn_module = None
        if sys.argv[i] == '-b':
            try: svn_branch = sys.argv[i+1]
            except IndexError: svn_branch = None
        if sys.argv[i] == '-g':
            try: git_module = sys.argv[i+1]
            except IndexError: git_module = None
        if sys.argv[i] == '-v':
            VERBOSE=True

    # ask user to fill the empty parameters
    if forge_url is None or svn_module is None or svn_branch is None or git_module is None:
        print(bcolors.GREEN+"\n* Please select input params"+bcolors.ENDC)
    if forge_url is None:
        answer = 0
        while answer is not '0' and answer is not '1' and answer is not '2':
            print(bcolors.BOLD+"\nSelect your FORGE url :"+bcolors.ENDC)
            print("  0 - quit")
            print("  1 - https://forge-urd44.osn.sagem")
            print("  2 - https://forge-valid30.rmm.sagem")
            answer = raw_input("--> ")
        if answer==0:
            exit(0)
            forge_url = "https://forge-urd44.osn.sagem" if answer=="1" else "https://forge-valid30.rmm.sagem"

    if svn_module is None:
        svn_module = ask_user("Select your svn-module name", "sc.stb-lib-opal")

    if svn_branch is None:
        svn_branch = ask_user("Select your master branch name", "BO_"+svn_module)

    # by default, git_module = svn_module
    if git_module is None:
        git_module = svn_module+'.git'

        answer = ""
        while answer is not 'y' and answer is not 'n':
            print(bcolors.BOLD+"\nDefault git-module name : {}".format(git_module)+bcolors.ENDC)
            print("Are you OK ? [y/n]")
            answer = raw_input("--> ")
        if answer=='n':
            git_module = ask_user("Select your git-module name", None)
        print("\n")

    return forge_url, svn_module, git_module, svn_branch, VERBOSE



# ----------------------------------------------------------------------
def ask_user(msg, ex):
    if ex is not None:
        answer = raw_input(bcolors.BOLD+"\n{}".format(msg)+bcolors.ENDC+" (ex:{}) : ".format(ex))
    else:
        answer = raw_input(bcolors.BOLD+"\n{} : ".format(msg)+bcolors.ENDC)
    return answer



# ----------------------------------------------------------------------
def run_cmd(cmd):
    print(bcolors.BOLD+"\n--> {}".format(cmd)+bcolors.ENDC)
    try:
        if os.system(cmd) != 0:
            raise Exception('wrong command !')
            exit(1)
    except:
        print(bcolors.BOLD+"\n{}: command failed !".format(cmd)+bcolors.ENDC)
        exit(1)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":

    # get params
    forge_url, svn_module, git_module, svn_branch, VERBOSE = get_params()
    current_dir = os.path.dirname(os.path.realpath(__file__))

    if VERBOSE:
        print("-------------- DEBUG --------------")
        print("input params :")
        print("forge_url  = {}".format(forge_url))
        print("svn_module = {}".format(svn_module))
        print("svn_branch = {}".format(svn_branch))
        print("git_module = {}".format(git_module))
        print("-----------------------------------")
        answer = ""
        while answer is not 'y' and answer is not 'n':
            print("Are you OK with that ? [y/n]")
            answer = raw_input("--> ")
        if answer=='n':
            print("abort !")
            exit(0)


    # check svn-module is valid
    cmd = 'svn info {}/svn/{} 2>/dev/null'.format(forge_url, svn_module)
    if VERBOSE:
        print("check svn-module is valid :")
        print("command : {}".format(cmd))
        print("result  : {}".format(os.popen(cmd, "r").read()))
    if not svn_module in os.popen(cmd, "r").read():
        print(bcolors.RED+"ERROR ! {} is not a valid svn module on {}".format(svn_module, forge_url)+bcolors.ENDC)
        exit(1)


    # ********
    # STEP 1 : clone branch from svn to git repo
    print(bcolors.GREEN+"\n* Create local git repo"+bcolors.ENDC)

    os.mkdir(git_module)
    os.chdir(git_module)
    if VERBOSE:
        print("mkdir({}) + chdir({})".format(git_module, git_module))

    # 1.1 : prepare (git svn init / git svn fetch)
    run_cmd("git svn init {f}/svn/{s} --trunk=BO/branches/{b} --tags=BO/tags".format(b=svn_branch, f=forge_url, s=svn_module))
    run_cmd("git svn fetch")

    # 1.2 : re-write all comments with :noBugzillaLink:
    run_cmd("git filter-branch --tag-name-filter cat --prune-empty --msg-filter 'python {}/cleaner.py' -- --all".format(current_dir))

    # ********
    # STEP 2 : create tags
    print(bcolors.GREEN+"\n\n* Create tags on master branch"+bcolors.ENDC)

    tag_pattern = svn_branch.replace("BO_", "")
    cmd = 'git branch -a | grep tags | grep '+tag_pattern+' | sed "s/^\ *//g"'
    remote_tag_list = re.split("\n", os.popen(cmd, "r").read())[:-1]

    if VERBOSE:
        print("tag_pattern = {}".format(tag_pattern))
        print("remote_tag_list is build with cmd :\n{}".format(cmd))
        index = 0
        for remote in remote_tag_list:
            index += 1
            print("  - tag #{} : {}".format(index, remote))

    index = 0
    nb_tags = len(remote_tag_list)

    for remote in remote_tag_list:
        index += 1
        svn_tag_name = os.path.basename(remote)
        git_tag_name = svn_tag_name

        msg = "[{}/{}] create tag svn:{s} --> git:{g}".format(index, nb_tags, s=svn_tag_name, g=git_tag_name)
        print("\n\n"+bcolors.BOLD+bcolors.YELLOW+msg+bcolors.ENDC)
        run_cmd('git checkout -b {s} {r}'.format(s=svn_tag_name, r=remote))
        run_cmd('git tag -a {g} {s} -m ":noBugzillaLink: create tag from SVN {g}"'.format(g=git_tag_name, s=svn_tag_name))
        run_cmd('git checkout master')
        run_cmd('git branch -D {s}'.format(s=svn_tag_name))

    os.chdir(current_dir)