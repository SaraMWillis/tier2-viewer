#!/usr/bin/env python3

import subprocess, json, sys

def find_objects(out,user_args):
    # AWS reports all the objects stored in AWS at once. This next bit 
    depth_1_objects = {}
    max_file_length = 0 
    

    for k in out["Contents"]:
        true_path = k["Key"]
        path_correct = True
        if user_args.prefix_is_dir == True and user_args.prefix != None:
            true_prefix = user_args.prefix + "/"
            if true_prefix == true_path:
                pass
            elif true_prefix == true_path[:len(true_prefix)]:
                pass
            else:
                path_correct = False
        if path_correct == True:
            obj = k['Key'].split("/")
            obj_size = k['Size']
            storage_class = k['StorageClass']
            if len(obj) == user_args.first_index:
                if len(obj[user_args.first_index-1]) > max_file_length:
                    max_file_length = len(obj[user_args.first_index-1])
                depth_1_objects['"' + obj[user_args.first_index-1]+'"'] = {"size": obj_size, "storage class": storage_class,"directory": False,"true path":true_path,"ArchiveStatus":"-","RestoreStatus":"-"}
            elif len(obj[user_args.first_index:]) == 1:
                if len(obj[user_args.first_index]) > max_file_length:
                    max_file_length = len(obj[user_args.first_index])
                depth_1_objects['"' + obj[user_args.first_index] + '"'] = {"size": obj_size, "storage class": storage_class,"directory": False,"true path":true_path,"ArchiveStatus":"-","RestoreStatus":"-"}
            elif obj[user_args.first_index + 1] == "":
                if len(obj[user_args.first_index]) > max_file_length:
                    max_file_length = len(obj[user_args.first_index])
                depth_1_objects['"'+obj[user_args.first_index]+'"'] = {"size": obj_size, "storage class": storage_class,"directory": True,"true path":true_path,"ArchiveStatus":"-","RestoreStatus":"-"}
    try:
        depth_1_objects.pop("")
    except KeyError:
        pass
    
    return depth_1_objects, max_file_length



def get_tier_class(bucket, true_path):
    p = subprocess.Popen(['aws s3api head-object --bucket %s --output json --key %s'%(bucket,true_path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    out,err = p.communicate()
    try:
        out =  json.loads(out.decode('utf-8',"ignore"))
    except json.decoder.JSONDecodeError:

        print("\nError retrieving data %s\nCheck that your input and try again. You can check the contents of your bucket without the --tier flag.\nIf the object you're querying exists, report this bug to sarawillis@arizona.edu. Debug information below."%true_path)
        print("Command executed: aws s3api head-object --bucket %s --output json --key %s"%(bucket,true_path))
        print("stdout: %s"%out.decode("utf-8","ignore"))
        print("stderr: %s"%err.decode("utf-8","ignore"))
        sys.exit(1)
    try:
        storage_class = out["StorageClass"]
    except KeyError:
        storage_class = "STANDARD"
    try: 
        restore_status = out["Restore"]
        if "false" in restore_status:
            restore_status="RESTORED"
        elif "true" in restore_status:
            restore_status="PROCESSING"
    except KeyError:
        restore_status = "-"
    try:
        archive_status = out["ArchiveStatus"]
    except KeyError:
        if storage_class == "INTELLIGENT_TIERING":
            archive_status = "FREQUENT_ACCESS"
        else:
            archive_status = "-"
    return storage_class, archive_status, restore_status
