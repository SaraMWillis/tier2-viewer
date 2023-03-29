# tier2-viewer
```tier2-viewer``` is a CLI utility to view the contents of an AWS bucket. The naming is an artifact of what is known as [Tier 2 storage](https://public.confluence.arizona.edu/display/UAHPC/Tier+2+Storage) available to UArizona members. 

Since this script was developed specifically for UArizona, the default region is set to ```us-west-2```. I may go through to make this more customizable in a future update. In the meantime, this can be reset in the ```aws_config()``` function in ```config/aws_credentials_config.py``` by modifying ```region_name```. 

## Dependencies

> - I may update the script in the future to eliminate the need for emoji since it's purly aesthetic.
> - The tqdm package is used to update the user on the progress of a long series of aws queries, specifically when requesting storage tiers of each object in a bucket.
> - pwinput is used to disguise user input when entering public and private access keys

- [AWS CLI](https://aws.amazon.com/cli/)
- Python >= 3.6
  - emoji==2.2.0
  - pwinput==1.0.3
  - tqdm==4.64.1
  
## Install
This script can either be run by putting tier2-viewer into your PATH. Alternatively, if you'd like to compile a single executable, one option is to use [pyinstaller](https://pyinstaller.org/en/stable/). For example:
```console
[user@hostname tier2-viewer]$ cd build
[user@hostname build]$ pyinstaller --onefile ../tier2-viewer
<build output>
[user@hostname build]$ ls dist/
tier2-viewer
```
This will generate a single tier2-viewer executable in ```${tier2-viewer-base}/build/dist```.

To set up your python environment, run:
```
[user@hostname tier2-viewer]$ pip install -r build/requirements.txt 
```
If you do not have root authority on the system where you are using this script, you can use a [virtual environment](https://public.confluence.arizona.edu/display/UAHPC/Using+and+Installing+Python#UsingandInstallingPython-InstallingPythonPackagesUsingvirtualenv) or [conda environment](https://public.confluence.arizona.edu/display/UAHPC/Using+and+Installing+Python#UsingandInstallingPython-UsingandInstallingPythonPackageswithConda).

## Configuration
To use tier2-viewer, your AWS keys must be configured with the aws CLI and a bucket name needs to be provided. You can set these credentials using ```tier2-viewer --config```. 

If you need to reconfigure your credentials, either because you have new access keys or you are connecting to a new bucket, you can rerun ```tier2-viewer --config```. As an example of the configuration process:

```console
[user@hostname tier2-viewer]$ ./tier2-viewer --config

Configuring options for ./tier2-viewer

Current credentials:
AWS Access Key ID    : ****************ABCD
AWS Secret Access Key: ************************************EFGH
Reconfigure AWS access tokens? (y/n): y

Entering AWS configuration.
AWS Access Key ID     : ********************
AWS Secret Access Key : ****************************************
Setting default region name to  : us-west-2
Setting default output format to: json
✅ Credentials are valid
aws configured

Current bucket: bucket-name
Reconfigure bucket? (y/n): y

Entering bucket configuration
Bucket Name: new-bucket-name
✅ The new-bucket-name bucket exists. Continuing

Configuration complete.
```

## Usage
Running ```tier2-viewer``` without any arguments will simply list the contents of your bucket. The goal of this script was to transform AWS output to more closely resemble a standard file system.

```console
[user@hostname tier2-viewer]$ ./tier2-viewer 

Object                                       Size
-------------------------------------------------
Archives/                                      0B
DEVEL/                                         0B
gmx21.sif/                                     0B
iqtree2-2.1.2/                                 0B
QNS-master/                                    0B
GCA_947599735.1_LP_J_v3_genomic.gbff.gz     1.0GB
iSALE2D.tar.gz                              51.4MB
tensorflow2-23.01-py3-interactive.sif       7.3GB
```

The ```--size``` option will allow you to get the size of your bucket, or target a "directory" by using the ```--prefix``` flag to view the total size of its contents. This is analogous to a ```du -sh```:
```console
[user@hostname tier2-viewer]$ ./tier2-viewer --size
Total objects found: 3737
Size of bucket: 9.4GB
[user@hostname tier2-viewer]$ ./tier2-viewer --size --prefix=iqtree2-2.1.2
Total objects found: 1929
Size: 733.8MB
```

You can also get the object classes of files by using the ```--tier``` flag:
```console
[user@hostname tier2-viewer]$ tier2-viewer --tier

Object                                       Size    Storage Class         Archive Status       Restore Status
------------------------------------------------------------------------------------------------------------------
Archives/                                      0B    -                     -                    -
DEVEL/                                         0B    -                     -                    -
gmx21.sif/                                     0B    -                     -                    -
iqtree2-2.1.2/                                 0B    -                     -                    -
QNS-master/                                    0B    -                     -                    -
GCA_947599735.1_LP_J_v3_genomic.gbff.gz     1.0GB    GLACIER               -                    -
iSALE2D.tar.gz                             51.4MB    GLACIER               -                    -
tensorflow2-23.01-py3-interactive.sif       7.3GB    INTELLIGENT_TIERING   FREQUENT_ACCESS      -
```

This can be helpful for tracking down the status of restore requests for archived objects.

For more information on usage:
```console
[user@hostname tier2-viewer]$ ./tier2-viewer --help



./tier2-viewer is a command line utility to view the contents of an AWS bucket.
This is used as a wrapper for the aws CLI to list files/directories, their
storage classes⭐, and the status of a restore request.

To retrieve information on the storage tier of an object, use the --tier flag in
your query. This can sometimes take a long time depending on the number of
objects in your bucket. A limit of 1000 objects can be queried for their storage
class.

Objects stored in a UArizona AWS bucket are subject to intelligent tiering⭐⭐.

⭐   Directories do not have storage tiers associated with them, only files.
⭐⭐ Objects smaller than 128KB are not subject to intelligent tiering and will
always be stored as STANDARD.




Usage: ./tier2-viewer [--OPTION=VALUE|--help|--config]

Valid OPTION/VALUE combinations
  --bucket=<bucket_name>                : Specify your bucket name. Not needed if --config used.
  --prefix=</path/to/file/or/directory> : View a specific file or directory in your bucket
                                        : Note: if your path has special characters (spaces, tabs, stars, etc)
                                        : in it, either use quotes, e.g.: --prefix="file name.txt", or escape the 
                                        : special character, e.g. --prefix=file\ name.

Additional flags
  --tiers                               : Get the storage class of a directory's contents or a specific file. This
                                          will also display processing restore requests for archival data.
  --size                                : Get the size of a file or directory in your bucket.
  --config                              : (Re)Configure your aws credentials and bucket name.
  --full-width                          : Display full filenames rather than scaling them to fit your terminal's width.
  --no-color                            : Turn off warning and directory colors.
  --help                                : Show this help message.
  --version                             : Print software version.
```
