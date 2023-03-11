#!/usr/bin/env python3

import os, emoji, subprocess
from user_input.user_flags import *
from user_input.user_prompts import user_continue
from config.aws_credentials_config import aws_config, bucket_config
from formatting.string_reformatting import mask_string
from display.usage import usage
from display._version import version, date, author, institution


def config_parameters(user_input, bucket_path,bucket_file, aws_credentials):
    user_args = Args(user_input)
    if os.path.exists(os.path.join(bucket_path,bucket_file)) == True and user_args.bucket == None:
        with open(os.path.join(bucket_path,bucket_file),"r") as file:
            bucket = file.read()
        user_args.bucket = bucket
    elif os.path.exists(os.path.join(bucket_path,bucket_file)) == True and user_args.bucket != None:
        try:
            subprocess.check_output(['aws', 's3api', 'head-bucket', '--bucket', user_args.bucket])
        except subprocess.CalledProcessError:
            sys.exit(emoji.emojize(":red_exclamation_mark: ")+ user_args.WARNINGCOLOR+f'The {user_args.bucket} bucket does not exist or you do not have access to it' + user_args.ENDCOLOR)
    # If the user includes the config flag, then they'll be guided through
    # the process of entering their AWS access keys and bucket name
    if user_args.config == True:
        print("\nConfiguring options for %s"%sys.argv[0])
        if os.path.exists(aws_credentials) == True:
            print("\nCurrent credentials:")
            with open(aws_credentials,"r") as file:
                lines = file.readlines()
                public_key = lines[1].strip().split("=")[-1].strip()
                private_key = lines[2].strip().split("=")[-1].strip()
        
            # We'll print the current AWS credentials to the screen. These will be
            # masked with a "*" replacing each character except the last 4 for privacy.
            print("AWS Access Key ID    : %s"%mask_string(public_key))
            print("AWS Secret Access Key: %s"%mask_string(private_key))
            reconfigure_aws = user_continue("Reconfigure AWS access tokens?")
            if reconfigure_aws == True:
                aws_config()
        else:
            aws_config()
        if user_args.bucket == None:
            bucket_config(bucket_path,bucket_file)
        else:
            print("\nCurrent bucket: %s"%user_args.bucket)
            reconfigure_bucket = user_continue("Reconfigure bucket?")
            if reconfigure_bucket == True:
                bucket_config(bucket_path,bucket_file)
        print("\nConfiguration complete.")
        sys.exit(0)
    
    if user_args.bucket == None:
        try:
            with open(os.path.join(bucket_path,bucket_file),"r") as file:
                bucket = file.read()
            user_args.bucket = bucket
        except FileNotFoundError:
            print("Oops! A bucket needs to be specified to proceed. Either:\n 1. Include the --bucket flag\n2. Use --config to permanently configure your bucket name.\nSee: %s --help for usage information."%sys.argv[0])
    if user_args.usage == True:
        usage(sys.argv[0])
    elif user_args.version == True:
        print("Program    : "+ sys.argv[0])
        print("Version    : "+ version)
        print("Date       : "+date)
        print("Author     : "+author)
        print("Institution: "+institution)
        sys.exit(0)
    return user_args
