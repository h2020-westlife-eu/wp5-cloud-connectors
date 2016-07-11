# WP5 Cloud Connectors
This project contains a standalone service that exposes a webdav interface to various public cloud providers.

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
For providers that need an OAuth2 token (Dropbox, Google Drive), it is necessary to have a separate web interface to handle the authorization flow.
##### S3
The token is a json hash with keys: access_key_id, secret_access_key, bucket_name
##### Google Drive
The token is the OAuth2 token.
##### Dropbox
The token is the OAuth2 token.


### Code architecture overview

- dispatch.py contains the HTTP layer, that listens on /webdav/
- providers.py contains the classes implementing the translation from the clouds internal api format to the standard webdav format.
  - the ProviderManager class is the generic class it acts both as in interface definition and as a place where the generic parts of the translation are stored.
  - S3Manager, DboxManager, GdriveManager classes are concrete implementations of the interface provided by ProviderManager.
- the clouds/ subdirectory contains modules that implement the actual connection to the clouds.


### TODO
1. Figure out how to dynamically pass credentials for new users
