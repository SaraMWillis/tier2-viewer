#!/usr/bin/env python3

import pwinput, subprocess, emoji, os

def aws_config():
    while True:
        print("\nEntering AWS configuration.")
        public_key  = pwinput.pwinput(prompt="AWS Access Key ID     : ")
        private_key = pwinput.pwinput(prompt="AWS Secret Access Key : ")
        region_name = "us-west-2"
        output_format = "json"
    
        print("Setting default region name to  : %s"%region_name)
        print("Setting default output format to: %s"%output_format)
    
        p = subprocess.Popen(['aws configure set aws_access_key_id %s'%public_key],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        output, error = p.communicate()
        p = subprocess.Popen(['aws configure set aws_secret_access_key %s'%private_key],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        output, error = p.communicate()
        p = subprocess.Popen(['aws configure set region %s'%region_name],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        output, error = p.communicate()
        p = subprocess.Popen(['aws configure set output %s'%output_format],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        output, error = p.communicate()
        try:
            subprocess.check_output(['aws', 'sts', 'get-caller-identity'])
            print(emoji.emojize(":check_mark_button: Credentials are valid"))
            break
        except subprocess.CalledProcessError:
            print(emoji.emojize(':red_exclamation_mark: Credentials are invalid. Retry.'))
    print("aws configured")
    del public_key
    del private_key 
    return

def bucket_config(bucket_path,bucket_file):
    print("\nEntering bucket configuration")
    while True:
        bucket_group = input("Bucket Name: ")
        bucket_name = "ua-rt-t2-"+bucket_group
        try: 
            subprocess.check_output(['aws', 's3api', 'head-bucket', '--bucket', bucket_name])
            print(emoji.emojize(":check_mark_button: ")+ f'The {bucket_name} bucket exists. Continuing')
            break
        except subprocess.CalledProcessError:
            print(emoji.emojize(":red_exclamation_mark: ")+ f'The {bucket_name} bucket does not exist or you do not have access to it')
    try:
        os.makedirs(bucket_path)
    except FileExistsError:
        pass
    write_path = os.path.join(bucket_path,bucket_file)
    with open(write_path,"w") as file:
        file.write(bucket_name)
    return
