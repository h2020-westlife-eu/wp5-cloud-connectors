# coding: utf-8

# PYTHON
import os
import tempfile
import traceback

# THIRD PARTY PYTHON
# from dropbox.files import WriteMode


def append_leading_slash(path):
    """To be valid, Dropbox expects '/*' paths"""
    return os.path.join('/', path)


def retrieve_file_from_dbox(dbox, storage_key):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfilename = tmpfile.name

            path = append_leading_slash(storage_key)
            file1 = dbox.files_download(path)
            if file1[1].status_code == 200:
                tmpfile.write(file1[1].content)

            return tmpfilename

    except:
        print('Download failed: %s' % traceback.format_exc())
        return None


def list_from_dbox(dbox, path=''):
    # The root of a dropbox has path ''
    if path is None or path == '/' or path == '.':
        path = ''
    return dbox.files_list_folder(path, recursive=False)#.entries


# def delete_file(dbox, storage_key):

#     try:
#         dbox.files_delete(storage_key)
#         return True
#     except:
#         print('Delete failed: %s' % traceback.format_exc())
#         return False


# def upload_file(datafile, dbox, tempfile_path):
#     dbox = get_dropbox_object(provider_token)
#     path = append_leading_slash(datafile.rel_path)
#     with open(tempfile_path, 'r') as f:
#         file1 = dbox.files_upload(
#             f.read(),
#             path,
#             mode=WriteMode('add', None),
#             autorename=True,
#             client_modified=None,
#             mute=False
#         )

#     return file1.path_lower


# def create_folder(folder, dbox):
#     path = append_leading_slash(folder.rel_path)
#     folder = dbox.files_create_folder(path)
#     return folder.path_lower
