from glob import glob, escape
from datetime import datetime
from collections import defaultdict
import os, os.path, sys, time
import re
import subprocess
import errno
import itertools
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
import hashlib


"""
Examples
    directories = set(glob('*')) - set(['000 Photos', '000 Videos'])
    
    imagefiles = get_files(directories, ('.jpg', '.jpeg', '.gif', '.png'))
    move_files(imagefiles, '000 GPhotos')

    video_files = get_files(directories, ('.mts', '.mov','.m4v','.mp4','.mpg', '.flv', '.f4v', '.avi'))
    move_files(video_files, '000 GVideos')
    
    del_empty_dirs('.', del_hidden=True)

    remove_dulplicate(get_files(['000 GPhotos']))
    remove_dulplicate(get_files(['000 GVideos']))

    extract_photos(get_files(['000 Images']), '000 Photos', False)

    extract_photos_by_key_name('screenshot', '000 Screenshots')

    for folder in glob('*'):
        types = get_folder_types(folder)
        print(folder, ':', types)

    print(count_types_size('.'))
"""

### UTILS

def make_sure_path_exists(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def get_md5(file_path):
    return hashlib.md5(open(file_path,'rb').read()).hexdigest()

"""
Don't work 100% of the time. To Fix
"""
def read_EXIF(imagepath):
    exif = {}
    try:
        for (k,v) in Image.open(imagepath)._getexif().items():
            exif[TAGS.get(k)] = v
    except Exception as e:
        # print(e)
        pass
    return exif


### LISTING

"""
Get all files,
Don't go into hidden directories
"""
def get_files(origin='.', extension_filter=None):
    files = []
    origins = origin
    if isinstance(origin, str):
        origins = [origin] # this let us support multiple root directories.
    for origin in origins:
        files += glob(origin+'/**/*.*', recursive=True)

    if extension_filter:
        if isinstance(extension_filter, str):
            extension_filter = [extension_filter]  # support string for extensions
        files = [f for f in files if f.lower().endswith(tuple(extension_filter))]
    
    return files

def list_photos(files):
    photos = []
    for file_path in files:
        try:
            exif = read_EXIF(file_path)
            if len(set(['Focal Length', 'Flash', 'ISO Speed Ratings', 'Model']).intersection(set(exif.keys()))) > 0:
                photos.append(file_path)
        except Exception as e:
            print(e)
    return photos

def list_files_by_keys_name(keys):
    files = []
    for file_path in files:
        try:
            filename = os.path.basename(file_path).replace(' ', '').lower()
            if any(keys in filename):
                files.append(file_path)
        except Exception as e:
            print(e)
    return files 


"""We first read the file size, if we have two files with same weight, we will compare their md5.
"""
def list_duplicates(paths):
    duplicates = []
    duplicates_md5 = []
    files_size = defaultdict()
    for file_path in paths:
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(file_path)
        files_size.setdefault(size, []).append(file_path)
    for file_size, files in files_size.items():
        if len(files) > 1:
            for k, g in itertools.groupby(files, get_md5):
                duplicates.append(list(g))
                duplicates_md5.append(k) # useless for now.
    return duplicates 


### RENAME

def rename_format(file_path, format="%Y%m%d_%H%M%S"):
    path = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    filename, extension = os.path.splitext(basename)

    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(file_path)
    new_name = datetime.fromtimestamp(ctime).strftime(format) + extension

    new_path = os.path.join(path, new_name)
    os.rename(file_path, new_path)
    return new_path

def rename_gdrive_format(file_path): # TO FIX
    rename_format(file_path, "%Y%m%d_%H%M%S")


def rename_dropbox_format(file_path):
    rename_format(file_path, "%Y-%m-%d %H.%M.%S")


### ANALYSIS

def get_folder_types(origin='.'): # extensions 
    """
    or simply: get_folder_types().keys() ???
    """
    files = get_files(origin)
    types = set()
    for file in files:
        types.add(file.split('.')[-1].lower())
    return types

def count_types_occurence(origin):
    files = get_files(origin)
    types = defaultdict(int)
    for file in files:
        extension = file.split('.')[-1].lower()
        types[extension] += 1
    return types

def count_types_size(origin):
    files = get_files(origin)
    types = defaultdict(int)
    for filepath in files:
        extension = os.path.splitext(filepath)[1].lower() # will contain the dot.
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filepath)
        types[extension] += size / 1000000. # just for now for simplicity
    return types



### ACTIONS

"""
Doesn't copy or move if the file already exist
"""
def extract_files(files, directory, copy=True):
    operation = shutil.copy2 if copy else shutil.move

    files_extracted = []
    for file_path in files:
        try:
            operation(file_path, directory)
            files_extracted.append(file_path)
        except Exception as e:
            print(e)
    return files_extracted

"""
By kylexlaw
"""
def del_empty_dirs(s_dir, del_hidden):
    b_empty = True

    for s_target in os.listdir(s_dir):
        s_path = os.path.join(s_dir, s_target)

        if os.path.isdir(s_path):
            if not del_empty_dirs(s_path, del_hidden):
                b_empty = False
        elif del_hidden and s_target.startswith('.'): # we delete hidden file
            print("Delete hidden file: %s" % s_path)
            os.remove(s_path)
        else:
            b_empty = False

    if b_empty:
        print('Delete: %s' % s_dir)
        os.rmdir(s_dir)

    return b_empty

def remove_files(paths):
    deleted = []
    for file_path in paths:
        try:
            os.remove(file_path)
            deleted.append(file_path)
        except Exception as e:
            print(e)
        print('Delete:', file_path)
    return deleted

# TO ADD: choose which duplicates to keep.