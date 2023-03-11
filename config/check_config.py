#!/usr/bin/env python3

import os
from user_input.user_prompts import user_continue
from user_input.user_flags import *
from config.aws_credentials_config import aws_config, bucket_config

def check_if_configured(aws_credentials, bucket_path,bucket_file):
    # If aws is present but hasn't been configured with the user's credentials, this bit gives them the option
    # to set that up. Without aws configured, this wrapper script won't work. If the user chooses not to 
    # configure their credentials with this script, they must run "aws configure"
    if os.path.exists(aws_credentials) == False:
        print("Oops! This script requires the aws CLI to be configured to work properly.")
        configure = user_continue("Configure now?")
        if configure == True:
            aws_config()
        else:
            sys.exit(0)
    else:
        pass
    # if the configuration file doesn't exist, we ask if the user wants to create it
    if os.path.exists(bucket_path) == False:
        print("\nNo bucket set.")
        configure = user_continue("Configure your account to always query a specific bucket?")
        
        # If the user doesn't want to configure their bucket file, then the program exits
        # with a note on usage. 
        if configure == False:
            print("Exiting. For usage, run:\n\t%s --help"%sys.argv[0])
            sys.exit(0)
            
        # Otherwise, we'll create a file under ~/.config/aws-tier-check/bucket with the
        # name of the user's bucket for future reference.
        else:
            bucket_config(bucket_path,bucket_file)
            with open(os.path.join(bucket_path,bucket_file),"r") as file:
                bucket = file.read()
                user_args = Args(['--bucket=%s'%bucket])
                
    # If the bucket path does exist, we'll configure the user arguments to include the
    # bucket name automatically. 
    else:
        with open(os.path.join(bucket_path,bucket_file),"r") as file:
            bucket = file.read()
            user_args = Args(['--bucket=%s'%bucket])
    return user_args