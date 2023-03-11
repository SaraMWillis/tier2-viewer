#!/usr/bin/env python3

def merge_bucket_dictionaries(ls_bucket,list_objects_bucket):
    for key,value in list_objects_bucket.items():
        if key in ls_bucket.keys():
            ls_bucket[key] = value
    return ls_bucket