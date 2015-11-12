# pyorg
Small library to organize files by scripts.

### UTILS

- make_sure_path_exists(path)
- get_md5(file_path)
- read_EXIF(image_path)

### LISTING

- get_files(origin='.', extension_filter=None)

  return all files from one or more folders. The extension filter can let you filter file by their extensions.
  
  ex: `get_files(origin='.', extension_filter=('mkv', 'mp4'))`: get all the mp4 or mkv files under the current directory.

- list_photos(files)

  return all the files that are photos.
  
- list_files_by_keys_name(files, keys)
  
  return all the files that match one of the keys.

- list_duplicates(paths)

  return all the duplicates.
  
### RENAME

- rename_format(file_path, format="%Y%m%d_%H%M%S")

- rename_gdrive_format(file_path)

- rename_dropbox_format(file_path)

### ANALYSIS

- get_folder_types(origin='.')

- count_types_occurence(origin)

- count_types_size(origin)

### ACTIONS

- extract_files(files, directory, copy=True)

- del_empty_dirs(s_dir, del_hidden)

- remove_files(paths)

### IDEAS / TO ADD

- delete file on all services: locally/cloud-service (dropbox, gdrive, gphotos, facebook).

- create tree organization according to date of creation

- add compress function (photos & videos)

- add encrypt function

- upload/archive function (dropbox, gdrive, ...)
