#!/usr/bin/env python3

import sys
from tqdm import tqdm
from formatting.string_reformatting import human_readable, formatting_string, formatting_string_ls, truncate
from aws.storage_class import find_objects, get_tier_class

def display_ls(content_data,user_args,max_name_length):
    print()
    print(formatting_string_ls("Object","Size",False,max_name_length,user_args))
    if max_name_length == 0:
        print("-"*16)
        print(user_args.WARNINGCOLOR + "[No contents found]" + user_args.ENDCOLOR)
        return
    else:
        print("-"*(max_name_length + 10))
    printing_objects = {"Directories":[],"Files":[]}
    for object_name, object_data in content_data.items():
        directory = object_data["directory"]
        size = human_readable(object_data["size"])
        display_name = truncate(object_name,max_name_length)
        if display_name[0] == '"':
            display_name = display_name[1:]
        if display_name[-1] == '"':
            display_name = display_name[:-1]
        if directory == True:
            printing_objects["Directories"].append(formatting_string_ls(display_name,size,directory,max_name_length,user_args))
        else:
            printing_objects["Files"].append(formatting_string_ls(display_name,size,directory,max_name_length,user_args))
    directories = sorted(printing_objects["Directories"],key=str.casefold)
    files = sorted(printing_objects["Files"],key=str.casefold)
    for i in directories:
        print(i)
    for i in files:
        print(i)
    return
    
    
    
def display_tiers(path_contents,user_args,max_file_length):
    print()
    printing_objects = {"Directories":[],"Files":[]}
    t = tqdm(path_contents.items(), desc="Found %s objects. Processing"%len(path_contents.keys()), ascii=True)
    for object_name, object_data in t:
        size = human_readable(object_data["size"])
        directory = object_data["directory"]
        true_path = object_data["true path"]
        storage_class = object_data["storage class"]
        display_name = object_name 
        if display_name[0] == '"':
            display_name = display_name[1:]
        if display_name[-1] == '"':
            display_name = display_name[:-1]
        if len(display_name) > max_file_length:
            display_name = display_name[:max_file_length-3]+"..."
        if directory == True:
            object_data["storage class"] = "-"
            object_data["ArchiveStatus"] = "-"
            object_data["RestoreStatus"] = "-"
            printing_objects["Directories"].append(formatting_string(display_name,size,object_data["storage class"],"-","-",object_data["directory"],user_args,max_file_length))
        elif storage_class == "STANDARD":
            object_data["ArchiveStatus"] = "-"
            object_data["RestoreStatus"] = "-"
            printing_objects["Files"].append(formatting_string(display_name,size,object_data["storage class"],object_data["ArchiveStatus"],object_data["RestoreStatus"],object_data["directory"],user_args,max_file_length))
        else:
            #size = human_readable(size)
            true_path = object_data["true path"]
            storage_class, archive_status, restore_status = get_tier_class(user_args.bucket, true_path)
            object_data["storage class"] = storage_class
            object_data["ArchiveStatus"] = archive_status
            object_data["RestoreStatus"] = restore_status     
            printing_objects["Files"].append(formatting_string(display_name,size,object_data["storage class"],object_data["ArchiveStatus"],object_data["RestoreStatus"],object_data["directory"],user_args,max_file_length))
    sys.stdout.write("\033[F\033[J")
    print(formatting_string("Object","Size","Storage Class","Archive Status","Restore Status",False,False,max_file_length))
    print("-"*(max_file_length + 75))
    directories = sorted(printing_objects["Directories"],key=str.casefold)
    files = sorted(printing_objects["Files"],key=str.casefold)
    for i in directories:
        print(i)
    for i in files:
        print(i)
    return