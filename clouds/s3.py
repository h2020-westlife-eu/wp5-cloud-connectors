# coding: utf-8

import tempfile
import traceback


def list_from_s3(bucket):
    return [f for f in bucket.objects.all()]


def retrieve_file_from_s3(storage_key, bucket):
    if bucket is None:
        print('Could not get S3 connection')
        return None

    else:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                tmpfilename = tmpfile.name

            bucket.download_file(storage_key, tmpfilename)
            return tmpfilename

        except:
            print('Download failed: %s' % traceback.format_exc())
            return None


# def upload_file_to_s3(datafile, s3, tempfile_path):
#     if s3 is None:
#         raise RuntimeError('Could not get S3 connection')

#     storage_key = str(uuid.uuid4())
#     s3.Object(s3_provider.bucket_name, storage_key).put(Body=open(tempfile_path, 'rb'))

#     return storage_key


# def delete_file_from_s3(s3, storage_key):
#     if s3 is None:
#         print('Could not get S3 connection')
#         return False

#     else:
#         try:
#             s3.Object(s3_provider.bucket_name, storage_key).delete()
#             return True
#         except:
#             print('Delete failed: %s' % traceback.format_exc())
#             return False
