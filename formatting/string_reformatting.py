#!/usr/bin/env python3

'''
------------------------------------------------------------------------------------------
                                     human readable
Converts bytes into a human-readable format
'''            
def human_readable(size):
    size = int(size)
    size_prefixes = ["B","KB","MB","GB","TB","PB"]
    
    for pfx in size_prefixes:
        if size < 1024:
            return str(size)+pfx
        else:
            size = round(size/1024,1)

'''
------------------------------------------------------------------------------------------
                                  formatting string
Formats output data into nicely aligned columns for easy viewing
'''
def formatting_string(name,size,storage_class,archive_tier,restore_request,directory,user_args,max_file_length):
    if directory == False:
        return str("{0:<%s} {1:>9}    {2:20}  {3:20} {4:}"%max_file_length).format(name,size,storage_class,archive_tier,restore_request)
    else:
        return user_args.DIRECTORYCOLOR+str("{0:<%s}"%max_file_length).format(name)+user_args.ENDCOLOR + " {0:>9}    {1:20}  {2:20} {3:}".format(size,storage_class,archive_tier,restore_request)
        

def formatting_string_ls(name,size,directory,max_file_length,user_args):
    if directory == False:
        return str("{0:<%s} {1:>9}"%max_file_length).format(name,size)
    else:
        return user_args.DIRECTORYCOLOR+str("{0:<%s}"%max_file_length).format(name)+user_args.ENDCOLOR + " {0:>9}".format(size)
        
        

def mask_string(s):
    if len(s) > 4:
        return '*' * (len(s) - 4) + s[-4:]
    else:
        return s
        
def truncate(string, max_width):
    if len(string) > max_width:
        string = string[:max_width-3]+"..."
    return string