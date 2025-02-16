import os
from nextcloud import NextCloud
from urllib.parse import urlparse

def downloadFiles(nextcloudUrl, username, password, remoteFolder, localFolder):
    try:
        nc=NextCloud(
            nextcloudUrl,
            username,
            password
        )
    
        if not remoteFolder.startswith('/'):
            remoteFolder = '/' + remoteFolder
        if not remoteFolder.endswith('/'):
            remoteFolder += '/'

        os.makedir(localFolder, exists_ok=True)
        files = nc.list_folders(remoteFolder)
        zipFiles = [f for f in files if f['path'].lower().endswith('.zip')]

        if not zipFiles:
            print(f"Found no zip files found in {remoteFolder}")
            return
        
        print(f"Found {len(zipFiles)} ZIP file(s)")

    except Exception as e:
        print(f"An error occured: {str(e)}")