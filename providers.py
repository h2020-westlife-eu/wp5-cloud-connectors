# coding: utf-8


import json
import pytz
import traceback


import boto3
import botocore.exceptions

from clouds.dbox import (
    list_from_dbox,
    retrieve_file_from_dbox,
)
from clouds.gdrive import (
    list_from_gdrive,
    retrieve_file_from_gdrive,
)
from clouds.s3 import (
    list_from_s3,
    retrieve_file_from_s3,
)


from dropbox.dropbox import Dropbox
from dropbox.files import FolderMetadata

from oauth2client import client

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import xml.etree.ElementTree as ET


S3 = 'S3_PROVIDER'
DBOX = 'DROPBOX_PROVIDER'
GDRIVE = 'GDRIVE_PROVIDER'

DEFAULT_DATE = '1970-01-01T00:00:00Z'


class ProviderManager(object):
    """Abstract object to hold common methods between providers"""

    new_credentials = None

    @staticmethod
    def build_one_node(data, root):
        response = ET.SubElement(root, "D:response", {"xmlns:lp1": 'DAV:', "xmlns:lp2": "http://apache.org/dav/props/"})

        href = ET.SubElement(response, "D:href")
        href.text = data['rel_path']

        propstat = ET.SubElement(response, "D:propstat")

        prop = ET.SubElement(propstat, "D:prop")

        resource_type = ET.SubElement(prop, "lp1:resourcetype")

        if data['isDir']:
            ET.SubElement(resource_type, "D:collection")
        else:
            getcontentlength = ET.SubElement(prop, "D:getcontentlength")
            getcontentlength.text = data['content_length']

            executable = ET.SubElement(prop, "lp2:executable")
            executable.text = "F"  # maybe retrieve this data as well

        creation_date = ET.SubElement(prop, "lp1:creationdate")
        creation_date.text = data['creation_date']

        get_last_modified = ET.SubElement(prop, "lp1:getlastmodified")
        get_last_modified.text = data['last_modified']

        # etag omitted

        supportedlock = ET.SubElement(prop, "D:supportedlock")

        lockentry = ET.SubElement(supportedlock, "D:lockentry")
        lockscope = ET.SubElement(lockentry, "D:lockscope")
        exclusive = ET.SubElement(lockscope, "D:exclusive")
        locktype = ET.SubElement(lockentry, "D:locktype")
        write = ET.SubElement(locktype, "D:write")
        lockentry2 = ET.SubElement(supportedlock, "D:lockentry")
        lockscope2 = ET.SubElement(lockentry2, "D:lockscope")
        shared2 = ET.SubElement(lockscope2, "D:shared")
        locktype2 = ET.SubElement(lockentry2, "D:locktype")
        write2 = ET.SubElement(locktype2, "D:write")

        lockdiscovery = ET.SubElement(prop, "D:lockdiscovery")

        getcontenttype = ET.SubElement(prop, "D:getcontenttype")
        getcontenttype.text = data['content_type']

        status = ET.SubElement(propstat, "D:status")
        status.text = "HTTP/1.1 200 OK"

    def convert_to_xml(self, data):
        """data: a list of dict like the following
            {
                "rel_path": 'foo',
                "isDir": True,
                "creation_date": "2016-05-26T13:32:34Z",
                "last_modified": "Wed, 25 May 2016 20:13:48 GMT",
                "content_type": "httpd/unix-directory",
                "content_length": None
            }
            If no data is available, a default value must have been provided.
        """
        root = ET.Element('D:multistatus', {"xmlns:D": "DAV:"})

        for elt in data:
            self.build_one_node(elt, root)

        # FIXME: missing following line with tostring method
        # <?xml version="1.0" encoding="utf-8"?>
        return ET.tostring(root, encoding="utf-8")

    def ls(self, path):
        """This should list files in a directory. Response need to be
        normalized to be properly serialized in xml later on."""
        raise NotImplemented(" error")

    def download(self, path):
        """This should retrieve one file and save it at local_path"""
        raise NotImplemented(" error")


class S3Manager(ProviderManager):
    def __init__(self, credentials_json):
        credentials = json.loads(credentials_json)
        try:
            self.s3 = boto3.resource(
                's3',
                aws_access_key_id=credentials['access_key_id'],
                aws_secret_access_key=credentials['secret_access_key']
            )
            try:
                self.bucket = self.s3.create_bucket(
                    Bucket=credentials['bucket_name'],
                    CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}
                )
            except:
                self.bucket = self.s3.Bucket(credentials['bucket_name'])
                self.exists = True
                try:
                    self.s3.meta.client.head_bucket(Bucket=credentials['bucket_name'])
                except botocore.exceptions.ClientError as e:
                    # If a client error is thrown, then check if it was a 404 error.
                    # If it was a 404 error, then the bucket does not exist
                    error_code = int(e.response['Error']['Code'])
                    if error_code == 404:
                        self.exists = False

                    # We raise anyway, whatever the error
                    raise
        except:
            print(traceback.format_exc())
            self.s3 = None

    def ls(self, path):
        # s3 api call
        s3_response = list_from_s3(self.bucket)
        # normalize output
        normalized_response = []
        for el in s3_response:
            normalized_response.append({
                "rel_path": el.key,
                "isDir": False,
                "creation_date": DEFAULT_DATE,
                "last_modified": DEFAULT_DATE,
                "content_type": '',
                "content_length": '0'
            })

        return normalized_response

    def download(self, key):
        return retrieve_file_from_s3(key, self.bucket)


class DboxManager(ProviderManager):
    def __init__(self, provider_token):
        self.dropbox = Dropbox(provider_token)

    def ls(self, path):
        # dropbox api call
        response_dbox = list_from_dbox(self.dropbox, path).entries

        # normalize output
        normalized_response = []
        for el in response_dbox:
            is_dir = type(el) == FolderMetadata
            normalized_response.append({
                "rel_path": el.path_lower,
                "isDir": True if is_dir else False,
                "creation_date": DEFAULT_DATE,
                "last_modified": el.client_modified.replace(tzinfo=pytz.UTC). strftime('%c') if hasattr(el, 'client_modified') else DEFAULT_DATE,
                "content_type": "httpd/unix-directory" if is_dir else '',
                "content_length": '0' if is_dir else str(el.size)
            })

        return normalized_response

    def download(self, path):
        return retrieve_file_from_dbox(self.dropbox, path)


class GdriveManager(ProviderManager):
    def __init__(self, provider_credentials):
        credentials = client.OAuth2Credentials.from_json(provider_credentials)

        gauth = GoogleAuth()
        gauth.credentials = credentials

        if gauth.access_token_expired:
            print('Google Drive token expired. Refreshing...')
            gauth.Refresh()
            self.new_credentials = gauth.credentials.to_json()

        gauth.Authorize()

        self.drive = GoogleDrive(gauth)

    def ls(self, path):
        # gdrive call
        response_drive = list_from_gdrive(self.drive, path)

        # normalize output
        normalized_output = []
        for el in response_drive:
            is_dir = el['mimeType'] == u'application/vnd.google-apps.folder'
            normalized_output.append({
                "rel_path": el['title'],
                "isDir": True if is_dir else False,
                "creation_date": el['createdDate'],
                "last_modified": el['modifiedDate'],
                "content_type": "httpd/unix-directory" if is_dir else el['mimeType'],
                "content_length": el['quotaBytesUsed']
            })
        return normalized_output

    def download(self, path):
        return retrieve_file_from_gdrive(path, self.drive)


PROVIDERS = {
    S3: S3Manager,
    DBOX: DboxManager,
    GDRIVE: GdriveManager
}
