#!/usr/bin/env python3

import subprocess, sys, emoji

def check_if_directory(user_args):
    if user_args.prefix == None:
        user_args.prefix_is_dir = True

    else:
        compareable_names = [user_args.prefix.split("/")[-1], user_args.prefix.split("/")[-1]+"/"]
        p = subprocess.Popen(["aws s3 ls %s/%s"%(user_args.bucket,user_args.searchable_prefix)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        out,err = p.communicate()
        out = out.decode("utf-8","ignore")
        err = err.decode("utf-8","ignore")    
        # If no results are returned, then this path does not exist

        if out == err == "":
            print(user_args.WARNINGCOLOR + "Oops! No objects exist in bucket %s with the specified path: %s"%(user_args.bucket,user_args.prefix)+user_args.ENDCOLOR)
            sys.exit(1)
        # If we get results, we need to check the number of results 
        out = out.strip().split("\n")
        # First, if there's only one entry, that makes things easy since we can differentiate directories from files
        # using the presence of the string PRE
        if len(out) == 1:
            reformatted = [i for i in out[0].split(" ") if i != ""]
            if reformatted[0] == "PRE":
                user_args.prefix_is_dir = True
            else:
                user_args.prefix_is_dir = False
        else:
            for result in out:
                reformatted = [i for i in result.split(" ") if i != ""]
                name = reformatted[-1].replace("/","")
                if name in compareable_names:
                    if reformatted[0] == "PRE":
                        user_args.prefix_is_dir = True
                    else:
                        user_args.prefix_is_dir = False
                    break
    return user_args
