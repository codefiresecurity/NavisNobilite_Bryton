import os
from nextcloud import NextCloud
from urllib.parse import urlparse
from dotenv import load_dotenv

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

        os.makedirs(localFolder, exist_ok="True")
        response = nc.list_folders(remoteFolder)
        files = response.data
        zipFiles = [f for f in files if f['href'].lower().endswith('.zip')]

        if not zipFiles:
            print(f"Found no zip files found in {remoteFolder}")
            return
        
        print(f"Found {len(zipFiles)} ZIP file(s)")

        for file in zipFiles:
            filePath = file['href']
            fileName = os.path.basename(filePath)
            localPath = os.path.join(localFolder, fileName)
            print(f"Downloading: {fileName}")
            nc.download_file(remoteFolder + '/' + fileName, localPath)
            print(f"Successfully downloaded to: {localPath}")

    except Exception as e:
        print(f"An error occured: {str(e)}")

if __name__ == "__main__":
    load_dotenv()
    NEXTCLOUD_URL = os.getenv('NEXTCLOUD_URL')
    USERNAME = os.getenv('USERNAME')
    PASSWORD = os.getenv('PASSWORD')
    REMOTE_FOLDER = os.getenv('REMOTE_FOLDER')
    LOCAL_FOLDER = os.getenv('LOCAL_FOLDER')

    downloadFiles(NEXTCLOUD_URL, USERNAME, PASSWORD, REMOTE_FOLDER, LOCAL_FOLDER)