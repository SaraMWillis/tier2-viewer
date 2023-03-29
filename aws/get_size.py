#!/usr/bin/env python3

import subprocess, json, sys
from tqdm import tqdm

'''
------------------------------------------------------------------------------------------
                                     du
Get the size of a "directory" or object. AWS doesn't have actual directories, so this 
really is getting the total size of objects starting with a particular prefix. This is 
roughly equivalent to running du -sh on a unix operating system.
'''
def du(user_args):
    
    # AWS pulls a number of objects at a time. The number is defined by page_size here.
    page_size = 10000
    if user_args.prefix == None:
        
        # If we're not targeting a specific directory, we query the whole bucket.
        p = subprocess.Popen(['aws s3api list-objects --bucket %s --query "[length(Contents[])]"'%(user_args.bucket)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    else:
        p = subprocess.Popen(['aws s3api list-objects --bucket %s --prefix=%s --query "[length(Contents[])]"'%(user_args.bucket,user_args.searchable_prefix)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output, error = p.communicate()
    total_objects = json.loads(output.decode("utf-8","ignore"))
    total_objects = int(total_objects[0])
    print("Total objects found: %s"%total_objects)
    
    # If more objects were found than the max we can grab at a time, we'll create a progress bar that users can 
    # use to get an idea of how their request is processing
    if page_size < total_objects:
        pbar = tqdm(total = total_objects,ascii=True, dynamic_ncols=True,leave=False)
        
    # AWS will generate a starting token that will allow you to move through the contents of your bucket
    # in chunks. 
    next_token = None
    size = 0 
    while True:
        if next_token == None:
            # We start without supplying a token flag in our AWS query
            next_token_flag = ""
        else:
            # For any subsequent searches, we add --starting-token <token> to our query
            next_token_flag = "--starting-token %s"%next_token
        if user_args.prefix == None:
            p = subprocess.Popen(['aws s3api list-objects-v2 --bucket %s --max-items %s %s'%(user_args.bucket,page_size,next_token_flag)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        else:
            p = subprocess.Popen(['aws s3api list-objects-v2 --bucket %s --max-items %s --prefix=%s %s'%(user_args.bucket,page_size,user_args.searchable_prefix,next_token_flag)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        output, error = p.communicate()
        out = json.loads(output.decode("utf-8","ignore"))
        err = error.decode("utf-8","ignore")
        size_sum = sum([int(i["Size"]) for i in out["Contents"]])
        size += size_sum
        if "NextToken" in out.keys():
            next_token = out["NextToken"]
            if page_size < total_objects:
                pbar.update(page_size)
        else:
            break
    if page_size < total_objects:
        pbar.update(page_size%total_objects)
    return size
