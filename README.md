### Installation

In a virtualenv, run the following:
````
$ pip install -r requirements.txt
$ python dispatch.py
````

You can use *client.py* to test how the system behaves. *client.py* is a VRE rough mockup.

To test dropbox, gdrive or s3 integration, you need api keys and auth token. More specifically, internally we keep a user -> token mapping, so each user can access his own account.
At the moment, there is no mechanism for associating an ldap user to, for example, a S3 account, so everything is harcoded.

Only read operations (list a directory, get a file) are supported. Write operations are not implemented at this point.

### Provider Specific information
##### S3
The token is a json hash with keys: access_key_id, secret_access_key, bucket_name
##### Google Drive
The token is the OAuth2 token.
##### Dropbox
The token is the OAuth2 token.


### TODO
1. Figure out how to dynamically pass credentials for new users
