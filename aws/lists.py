#!/usr/bin/env python3

import subprocess, os, sys, json, re

'''
------------------------------------------------------------------------------------------
                                     Valid Buckets
Currently, and maybe unhelpfully, this function is not in effect. It's designed to print
the names of available valid buckets. This may be implemented in a future version.
'''
def valid_buckets():
    p = subprocess.Popen(['aws s3 ls'],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output, error = p.communicate()
    out = output.decode("utf-8","ignore")
    err = error.decode("utf-8","ignore")
    print(err)
    out = out.split("\n")
    valid_bucket_names = [i.split(" ")[-1] for i in out if i != ""]
    print(valid_bucket_names)
    sys.exit(0)
    
    
'''
------------------------------------------------------------------------------------------
                                     AWS LS
This function goes into an S3 bucket and collects the contents listed under a specific prefix.
This parses out "directories" from files and gets the sizes of the objects.This could also be used 
to get the time/date stamps on objects which may be useful for intelligent tiering objects 
headed toward archive.
'''    
def aws_ls(bucket, prefix,is_directory):

    if prefix == None:
        prefix = ""
    path = os.path.join(bucket,prefix)
    if is_directory == True and prefix != "":
        path = path[:-1]+'/"'
        
    # Our path should now look something like bucket_name/file/or/directory
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
        
        # Crud... thats not always true. Fine. Catching that case.
        if len(out) == 1 and out[0].split(" ")[0] == "PRE" and prefix != "":
            path += "/"
        else:
            search = False
            
    # Now the goal is to collect the contents of whatever directory we're querying. We care about the max_name_length for 
    # display purposes
    objects = {}
    max_name_length = 0
    # AWS has the option to provide aws s3 ls in json format, but it doesn't work -_-
    # This means (sigh) the output is space delimited. We'll use regex to parse date/time/size data from file names. This
    # is especially important if we want to query filenames later for tier information. If files contain spaces and we try 
    # brute forcing splits based on spaces, things go downhill quickly. 
    regex_pattern = "\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}\:\d{2}\s+\d+\s{1}"
    
    for obj in out:
        reformatted = re.split(regex_pattern,obj)
        # If our reformatted data only has one entry, no date/time/size formatting using our regex pattern. If this includes
        # a "PRE " at the start of the entry, then it's a "directory".
        if len(reformatted) == 1 and reformatted[0][:4] == "PRE ":
            # We'll splice out the PRE bit and keep the directory name.
            name = reformatted[0].split("PRE ")[-1]
            if len(name) > max_name_length:
                max_name_length = len(name)
            size = 0 
            directory = True
            # Our "true_path" variable should have quotes around it for search purposes. We'll lop the last one off, add our
            # directory name, and add a new " to the end to requote it. Without quotes on our searchable prefixes, we'd need 
            # to escape all the unusual characters users put in their filenames (one space, two spaces, line break, hypen, question mark,
            # bean burrito, etc.) and that gets nasty quickly.
            true_path = prefix[:-1] + name + '"'
            # We'll store our directory in our objects dictionary with the information we parsed.
            objects[name] = {"size" : size, "directory": directory, "true path": true_path, "storage class": "-","ArchiveStatus": "-", "RestoreStatus":"-"}
            
        # If two objects are in our results, the regex pattern was matched. This is a file, so we'll get information from it. 
        elif len(reformatted) == 2:
            # The filename is the second object in the list, it's the bit after what matched the regex expression
            name = reformatted[-1]
            # The first bit that matched the pattern is parsed to get the date, time, and size. This is a space-delimited chunk, so we'll
            # excise the spaces using a list comprehension
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
    return objects, max_name_length
    
'''
------------------------------------------------------------------------------------------
                                     AWS list objects
aws s3api list-objects is different from aws s3 ls. It does a recursive search of everything under the bucket or supplied
prefix. It's a bit of a shame that you can't merge the functionality of s3 ls and s3api list-objects, since what 
I'm personally interested in is what storage class an object is in, displayed in a format that resembles a standard file system. I don't
really want to have to parse through a whole bunch of prefix/json output and navigate through pages using starting tokens. But, of course, 
that's the whole point between tier2-viewer. If I could do this with aws s3api, I might not have written this software...

The reason I'd like to get this output is to figure out object classes. I can't get the archive status of an object without running 
a head-object on it. This may require a lot of aws s3api calls, depending on how many objects there are in the query. I'd like
to skip as many as I can. Specifically, if an object is in the STANDARD storage class, then archival status is irrelevant. 
# I can find these with the list-objects, so it may help speed things up.
'''        
def aws_list_objects(user_args, bucket_limit,bucket_contents):
    if user_args.prefix == None:
        p = subprocess.Popen(["aws s3api list-objects --bucket %s --output json --max-items=%s"%(user_args.bucket,bucket_limit)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    else:
        p = subprocess.Popen(["aws s3api list-objects --bucket %s --output json --prefix=%s --max-items=%s"%(user_args.bucket,user_args.searchable_prefix,bucket_limit)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    out,err = p.communicate()
    err = err.decode("utf-8","ignore")
    out = out.decode('utf-8',"ignore")
    # If stderr is giving us an Access Denied message, then we're trying to access a bucket we don't have the permissions for.
    if "ListObjects operation: Access Denied" in err:
        print(user_args.WARNINGCOLOR+"Oops! An error occured trying to access bucket '%s'. Verify this bucket exists and that you have access. Exiting"%user_args.bucket+user_args.ENDCOLOR)
        sys.exit(1)
    # If we're entering a prefix that doesn't exist, this will cause problems.
    elif err == "" and out == "":
        print(user_args.WARNINGCOLOR+"Oops! An error occured. Verify your input to ensure you're entering the correct bucket/prefix. For help, see: %s --help"%sys.argv[0]+user_args.ENDCOLOR)
        sys.exit(1)
    out = json.loads(out)
    return out
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    