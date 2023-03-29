#!/usr/bin/env python3

'''
------------------------------------------------------------------------------------------
                                     Merge Bucket Dicts
A small function that takes the dictionaries generated from the output of aws s3 ls
and aws s3api list-objects and merges them.

Not particularly impressive, but it gives us some additional information about 
objects that were found with ls that can be used to skip running a head-object on
every key later.
'''

def merge_bucket_dictionaries(ls_bucket,list_objects_bucket):
    for key,value in list_objects_bucket.items():
        if key in ls_bucket.keys():
            ls_bucket[key] = value
    return ls_bucket