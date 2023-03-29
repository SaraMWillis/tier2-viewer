#!/usr/bin/env python3

import subprocess, os, sys, json, re


def valid_buckets():
    p = subprocess.Popen(['aws s3 ls'],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output, error = p.communicate()
    out = output.decode("utf-8","ignore")
    err = error.decode("utf-8","ignore")
    print(err)
    out = out.split("\n")
    valid_bucket_names = [i.split(" ")[-1] for i in out if i != ""]
    print(valid_bucket_names)
    #for i in out:
    #    print(i.split("\n"))
    sys.exit(0)
    
    
    
def aws_ls(bucket, prefix,is_directory):

    if prefix == None:
        prefix = ""
    path = os.path.join(bucket,prefix)
    if is_directory == True and prefix != "":
        path = path[:-1]+'/"'
    # Our path should now look something like ua-rt-t2-<groupname>/file/or/directory
    # this will allow us to run an aws s3 ls PATH to get the contents of a directory
    search = True
    while search == True:
        # We start by querying the object. This will give us information on the files/directories inside
        p = subprocess.Popen(['aws s3 ls %s'%path],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        output, error = p.communicate()
        out = [i.strip() for i in output.decode("utf-8","ignore").split("\n") if i != ""]
        err = error.decode("utf-8","ignore")
        # If there is only one result and it starts with PRE, then that means the object we're querying is a directory and the
        # syntax we've used has prevented us from successfully querying the contents. This, in theory, shouldn't happen given
        # upstream manipulations...
        
        # Crud... thats not always true. 
        if len(out) == 1 and out[0].split(" ")[0] == "PRE" and prefix != "":
            path += "/"
        else:
            search = False
    # Now the goal is to collect the contents of whatever directory we're querying. We care about the max_name_length for 
    # display purposes
    objects = {}
    max_name_length = 0
    regex_pattern = "\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}\:\d{2}\s+\d+\s{1}"
    for obj in out:
        reformatted = re.split(regex_pattern,obj)
        #print(reformatted)
        if len(reformatted) == 1 and reformatted[0][:4] == "PRE ":
            #print(reformatted[0][:4])
            name = reformatted[0].split("PRE ")[-1]
            if len(name) > max_name_length:
                max_name_length = len(name)
            size = 0 
            directory = True
            true_path = prefix[:-1] + name + '"'
            objects[name] = {"size" : size, "directory": directory, "true path": true_path, "storage class": "-","ArchiveStatus": "-", "RestoreStatus":"-"}
        elif len(reformatted) == 2:
            name = reformatted[-1]
            date, time, size =[i for i in re.search(regex_pattern,obj)[0].split(" ") if i != ""]
            if is_directory == False and prefix != "":
                true_path = prefix
                key_comparison = true_path 
                directory = False
                if key_comparison[-1] == '"':
                    key_comparison  = key_comparison[:-1]
                if key_comparison[0] == '"':
                    key_comparison = key_comparison[1:]
                key_comparison = key_comparison.split("/")[-1]
                if name == key_comparison:
                    max_name_length = len(name)
                    objects[name] = {"size" : size, "directory": directory, "true path": true_path, "storage class": "-","ArchiveStatus": "-", "RestoreStatus":"-"}
                    break
            # Now, if we've targetted a directory and PRE isn't showing up in the entry we're parsing, we've found a file.    
            else:
                date, time, size =[i for i in re.search(regex_pattern,obj)[0].split(" ") if i != ""]
                directory = False
                if prefix != "":
                    true_path = prefix[:-1]+"/"+name+'"'
                else:
                    true_path = '"'+name+'"'
                if len(name) > max_name_length:
                    max_name_length = len(name) 
                objects[name] = {"size" : size, "directory": directory, "true path": true_path, "storage class": "-","ArchiveStatus": "-", "RestoreStatus":"-"}
        #print(reformatted)
        # The output is space-delimited, so we'll parse it to get the info we need

        # if the parsed output starts with a PRE label, then that means it's a directory
        # Now, if our result has 3 elements with a 0 for size, this is giving us info on the directory we're querying. We won't 
        # worry about this entry and skip it.
        #elif len(reformatted) == 3 and reformatted[-1] == "0":
        #    pass
        
        # Otherwise, the element we've found is a file
        #else:
            # Now, the question is if this file was directly targeted with the --prefix flag. If it is, we only want to 
            # include information about it and nothing else. AWS will return multiple objects if you're querying something
            # that shares a common prefix with something else (think: 111 and 11111), so we need to catch these cases. 
        #    date, time, size = reformatted[:3]
        #    name =  " ".join(reformatted[3:]) 
            
        #    if is_directory == False and prefix != "":
                # if we're targeting a file, the true path is the path that was given with the prefix flag
        #        true_path = prefix
        #        key_comparison = true_path 
        #        directory = False
                # Because the true path has quotations around it, we want to remove them, then get the last element in 
                # the path to compare the name of the object we've found with the prefix that was provided so we can 
                # exclude erroneous results.
        #        if key_comparison[-1] == '"':
        #            key_comparison  = key_comparison[:-1]
        #        if key_comparison[0] == '"':
        #            key_comparison = key_comparison[1:]
        #        key_comparison = key_comparison.split("/")[-1]
                # If we've found our target, we add it to our results and stop the search
        #        if name == key_comparison:
        #            max_name_length = len(name)
        #            objects[name] = {"size" : size, "directory": directory, "true path": true_path, "storage class": "-","ArchiveStatus": "-", "RestoreStatus":"-"}
        #            break
        #    # Now, if we've targetted a directory and PRE isn't showing up in the entry we're parsing, we've found a file.    
        #    else:
        #        date, time, size = reformatted[:3]
        #        directory = False
        #        if prefix != "":
        #            true_path = prefix[:-1]+"/"+name+'"'
        #        else:
        #            true_path = '"'+name+'"'
        #        if len(name) > max_name_length:
        #            max_name_length = len(name) 
        #        objects[name] = {"size" : size, "directory": directory, "true path": true_path, "storage class": "-","ArchiveStatus": "-", "RestoreStatus":"-"}
    #sys.exit(0)
    return objects, max_name_length
    
    
def aws_list_objects(user_args, bucket_limit,bucket_contents):
    if user_args.prefix == None:
        p = subprocess.Popen(["aws s3api list-objects --bucket %s --output json --max-items=%s"%(user_args.bucket,bucket_limit)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    else:
        p = subprocess.Popen(["aws s3api list-objects --bucket %s --output json --prefix=%s --max-items=%s"%(user_args.bucket,user_args.searchable_prefix,bucket_limit)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    out,err = p.communicate()
    err = err.decode("utf-8","ignore")
    out = out.decode('utf-8',"ignore")
    if "ListObjects operation: Access Denied" in err:
        print(user_args.WARNINGCOLOR+"Oops! An error occured trying to access bucket '%s'. Verify this bucket exists and that you have access. Exiting"%user_args.bucket+user_args.ENDCOLOR)
        sys.exit(1)
    elif err == "" and out == "":
        print(user_args.WARNINGCOLOR+"Oops! An error occured. Verify your input to ensure you're entering the correct bucket/prefix. For help, see: %s --help"%sys.argv[0]+user_args.ENDCOLOR)
        sys.exit(1)
    out = json.loads(out)
    return out
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    