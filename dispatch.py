import json

from flask import Flask
from flask import request

from providers import DBOX, GDRIVE, S3
from providers import PROVIDERS

app = Flask(__name__)


credentials = {
    'test': {
        DBOX: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        GDRIVE: b'{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/drive"], "token_expiry": "2015-12-16T13:03:46Z", "id_token": null, "access_token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"}, "client_id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", "user_agent": null}',
        S3: json.dumps({
            "access_key_id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "secret_access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "bucket_name": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        }),

    }
}


def get_username_from_header(request):
    return request.authorization.username


@app.route("/connect", methods=['GET'], strict_slashes=False)
def get_list_providers():
    """This function lists all the available providers for a given user"""
    user_key = get_username_from_header(request)
    return json.dumps(credentials[user_key].keys())


@app.route("/connect/<provider>", methods=['POST'])
def connect(provider):
    """This function allows us to add credentials for the user.
    Credentials are kept as an in-memory hash at the moment
    but we could use a database here...
    """
    # FIXME: check auth somehow, database? Add it to credentials
    user_key = get_username_from_header(request)

    if request.method == 'POST':
        provider_token = request.data.provider
        credentials[user_key][provider] = provider_token


@app.route("/webdav/<provider>/<path:path>", methods=['PROPFIND'], strict_slashes=False)
def list(provider=None, path=None):
    username = get_username_from_header(request)
    # From that variable, get api keys for given provider
    provider_token = credentials[username][provider]

    # Call Dispatch
    provider_manager = PROVIDERS[provider](provider_token)
    # Some providers can return updated credentials
    if provider_manager.new_credentials is not None:
        credentials[username][provider] = provider_manager.new_credentials

    provider_response = provider_manager.ls(path)
    return provider_manager.convert_to_xml(provider_response), 207, {'Content-Type': 'application/xml'}


@app.route("/webdav/<provider>/<path:path>", methods=['GET'], strict_slashes=False)
def download(provider=None, path=None):
    username = get_username_from_header(request)
    # From that variable, get api keys for given provider
    provider_token = credentials[username][provider]

    # Call Dispatch
    provider_manager = PROVIDERS[provider](provider_token)
    # Some providers can return updated credentials
    if provider_manager.new_credentials is not None:
        credentials[username][provider] = provider_manager.new_credentials

    provider_response = provider_manager.download(path)
    return provider_response


if __name__ == "__main__":
    app.debug = True
    app.run(port=5000)
