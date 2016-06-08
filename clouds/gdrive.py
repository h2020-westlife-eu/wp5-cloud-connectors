# coding: utf-8


import tempfile
import traceback


def retrieve_file_from_gdrive(storage_key, drive):

    parent_id = storage_key.lstrip('./').rstrip('/')
    parent_ids = parent_id.split('/')
    key_for_dl = find_parent_id_by_hand(drive, parent_ids, 0)

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfilename = tmpfile.name

            print('Using storage_key: %s' % key_for_dl)
            file1 = drive.CreateFile({'id': key_for_dl})
            print('Detected title is: %s' % file1['title'])
            file1.GetContentFile(tmpfilename)

            return tmpfilename

    except:
        print('Download failed: %s' % traceback.format_exc())
        return None


def list_from_gdrive(drive, parent_id=None):
    children = []

    if parent_id == '.':
        parent_id = 'root'

    if parent_id is None or parent_id == 'root':
        query = "('root' in parents) and trashed=false"
    else:
        # We need to retrieve the parent_id by hand
        parent_id = parent_id.lstrip('./').rstrip('/')
        parent_ids = parent_id.split('/')

        gdrive_parent_id = find_parent_id_by_hand(drive, parent_ids, 0)

        query = "('%s' in parents) and trashed=false" % gdrive_parent_id

    for f in drive.ListFile({'q': query}).GetList():
        children.append(f)

    return children


def find_parent_id_by_hand(drive, parent_ids, count, parent_id=None):
    """We get a path from webdav request.
    We need to retrieve the file or its children on gdrive.
    We need for that to get its id to performs propfind request on it.
    We split the path and look recursively for the children we want until we
    get the id needed.
    """
    title = parent_ids[count]
    parent_for_query = parent_id if parent_id is not None else 'root'
    query = "'%s' in parents and trashed=false" % parent_for_query
    list_files = drive.ListFile({'q': query}).GetList()
    if not list_files and count != (len(parent_ids) - 1):
        return None
    for f in list_files:
        if f['title'] == title:
            if count == (len(parent_ids) - 1):
                return f['id']
            else:
                return find_parent_id_by_hand(drive, parent_ids, count + 1, f['id'])


# def upload_file_to_gdrive(datafile, drive, tempfile_path):
#     file1 = drive.CreateFile({
#         'title': datafile.filename,
#         'parents': [{'id': datafile.folder.storage_key}]
#     })
#     file1.SetContentFile(tempfile_path)
#     file1.Upload()

#     return file1['id']


# def create_folder_on_gdrive(folder, drive):
#     file1 = drive.CreateFile({
#         'title': folder.name,
#         'mimeType': FOLDER_MIMETYPE,
#         'parents': [{'id': folder.parent.storage_key}]
#     })
#     file1.Upload()

#     return file1['id']


# def delete_file_from_gdrive(drive, storage_key):
#     try:
#         drive.auth.service.files().trash(fileId=storage_key).execute()
#         return True
#     except:
#         print('Delete failed: %s' % traceback.format_exc())
#         return False
