#!/usr/bin/env python3

import sys, shutil, textwrap, emoji

def usage(command):
    TERMINAL_WIDTH=shutil.get_terminal_size().columns
    width = 80
    if width > TERMINAL_WIDTH:
        width = TERMINAL_WIDTH
    print("\n\n")
    print("\n".join(textwrap.wrap(command + " is a command line utility to view the contents of an AWS bucket. This is used as a wrapper for the aws CLI to list files/directories, their storage classes"+emoji.emojize(":star:")+", and the status of a restore request.", width)))
    print()
    print("\n".join(textwrap.wrap("To retrieve information on the storage tier of an object, use the --tier flag in your query. This can sometimes take a long time depending on the number of objects in your bucket. A limit of 1000 objects can be queried for their storage class in a bucket.", width)))
    print()
    print("\n".join(textwrap.wrap(emoji.emojize("Objects stored in a UArizona AWS bucket are subject to intelligent tiering:star::star:."), width)))
    print()
    print("\n".join(textwrap.wrap(emoji.emojize(":star:   Directories do not have storage tiers associated with them, only files."), width)))
    print("\n".join(textwrap.wrap(emoji.emojize(":star::star: Objects smaller than 128KB are not subject to intelligent tiering and will always be stored as STANDARD."), width)))
    #Objects stored in a UArizona AWS bucket are subject to intelligent tiering**.\n\n\n")
    #print(textwrap.wrap(about_string,width=TERMINAL_WIDTH))
    print("\n\n")
    
    print("\nUsage: %s [--OPTION=VALUE|--help|--config]"%command)
    print()
    print("Valid OPTION/VALUE combinations")
    print("  --bucket=<bucket_name>                : Specify your bucket name. Not needed if --config used.")
    print("  --prefix=</path/to/file/or/directory> : View a specific file or directory in your bucket")
    print("                                        : Note: if your path has special characters (spaces, tabs, stars, etc)")
    print('                                        : in it, use quotes, e.g.: --prefix="file name.txt"')
    print("")
    print("Additional flags")
    print("  --tiers                               : Get the storage class of a directory's contents or a specific file. This")
    print("                                          will also display processing restore requests for archival data.")
    print("  --config                              : (Re)Configure your aws credentials and bucket name\n")
    print("  --full-width                          : Display full filenames rather than scaling them to fit your terminal's width")
    print("  --help                                : Show this help message")
    print("  --version                             : Print software version")
    sys.exit(0)