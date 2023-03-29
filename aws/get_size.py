#!/usr/bin/env python3

import subprocess, json, sys
from tqdm import tqdm

def du(user_args):
    page_size = 10000
    if user_args.prefix == None:
        p = subprocess.Popen(['aws s3api list-objects --bucket %s --query "[length(Contents[])]"'%(user_args.bucket)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    else:
        p = subprocess.Popen(['aws s3api list-objects --bucket %s --prefix=%s --query "[length(Contents[])]"'%(user_args.bucket,user_args.searchable_prefix)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output, error = p.communicate()
    total_objects = json.loads(output.decode("utf-8","ignore"))
    total_objects = int(total_objects[0])
    print("Total objects found: %s"%total_objects)
    
    
    if page_size < total_objects:
        #print("Processing...")
        pbar = tqdm(total = total_objects,ascii=True, dynamic_ncols=True,leave=False)
    next_token = None
    size = 0 
    while True:
        if next_token == None:
            next_token_flag = ""
        else:
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
