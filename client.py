import easywebdav
import tempfile

DOMAIN = '127.0.0.1'
PATH = 'webdav'

DEPTH_0 = '0'
DEPTH_1 = '1'
DEPTH_INFINITY = 'Infinity'


class Webdav():
    def __init__(self, provider):
        self.provider = easywebdav.connect(
            DOMAIN,
            protocol='http',
            path='/'.join([PATH, provider]),
            port=5000,
            username="test",
            password='foo',
        )


if __name__ == "__main__":
    pass
    # webdav = Webdav('DROPBOX_PROVIDER')
    # print(webdav.provider.ls(remote_path='.', depth=DEPTH_0))
    # with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
    #     tmpfilename = tmpfile.name
    #     print(
    #         webdav.provider.download('prise en main de dropbox.pdf', tmpfilename)
    #     )

    # webdav = Webdav('S3_PROVIDER')
    # print(webdav.provider.ls(remote_path='.', depth=DEPTH_0))
    # with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
    #     tmpfilename = tmpfile.name
    #     print(
    #         webdav.provider.download('066e3018-bc30-4063-8c89-9612637aea4f', tmpfilename)
    #     )

    # webdav = Webdav('GDRIVE_PROVIDER')
    # print(webdav.provider.ls(remote_path='Folder2/Folder3/', depth=DEPTH_0))
    # print(webdav.provider.ls(remote_path='.', depth=DEPTH_0))
    # with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
    #         tmpfilename = tmpfile.name
    #         print(
    #             webdav.provider.download('Getting started', tmpfilename)
    #         )

