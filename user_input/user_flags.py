#!/usr/bin/env python3

import getopt, sys, re, shutil
'''
------------------------------------------------------------------------------------------
                                     Args
Parses input flags. Flags determine what's displayed and how it's displayed. Recently added 
scale/width option. 
'''
class Args:
    def __init__(self,argv):
        self.DIRECTORYCOLOR="\033[38;5;27m"
        self.WARNINGCOLOR="\033[38;5;9m"
        self.ENDCOLOR="\033[0m"
        self.TERMINAL_WIDTH=shutil.get_terminal_size().columns
        self.max_width = self.TERMINAL_WIDTH - 13
        if self.max_width < 10:
            self.max_width=10
        self.argv = argv
        self.prefix = self.searchable_prefix =None
        self.prefix_is_dir = False
        self.first_index = 0
        self.bucket = None
        self.tiers = False
        self.config = False
        self.usage = False
        self.version = False
        self.get_size = False
        try:
            opts,args = getopt.getopt(argv, "hvcsftn:p:g:b:",["help","version","tiers","config","size","configure","full-width","no-color","prefix=","path=","group=","bucket="])
        except getopt.GetoptError:
            sys.exit("Unrecognized Option")
        for opt,arg in opts:
            if opt in ("-h","--help"):
                self.usage = True
            elif opt in ("-p","--prefix","--path"):
                self.prefix = arg
                if len(arg) == 0 or arg == "/":
                    self.prefix = None
                else:
                    if arg[-1] == "/":
                        self.prefix = self.prefix[:-1]
                    if arg[0] == "/":
                        self.prefix = self.prefix[1:]
                    elif arg == "":
                        self.prefix = None
                    self.first_index = len(self.prefix.split("/"))
                if self.prefix != None:
                    self.searchable_prefix = '"' + self.prefix + '"'
            elif opt in ("-b","--bucket"):
                self.bucket = arg
            elif opt in ("-t","--tiers"):
                self.tiers = True
                self.max_width = self.max_width - 75
                if self.max_width < 10:
                    self.max_width = 10
            elif opt in ("-g","--group"):
                self.bucket = "ua-rt-t2-%s"%arg
            elif opt in ("-c","--config","--configure"):
                self.config = True
            elif opt in ("-v", "--version"):
                self.version = True
            elif opt in ("-f","--full-width"):
                self.max_width = None
            elif opt in ("--no-color"):
                self.WARNINGCOLOR ="\033[0m"
                self.DIRECTORYCOLOR = "\033[0m"
            elif opt in ("--size","-s"):
                self.get_size = True
        if [self.tiers, self.get_size].count(True) > 1:
            sys.exit("Oops! The --tiers and --size flags are mutually exclusive.")
