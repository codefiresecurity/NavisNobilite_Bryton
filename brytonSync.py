from pathlib import Path
from dotenv import load_dotenv
import os
import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree
from urllib.parse import urlparse
import zipfile 
import time
import json

def checkRWGPS(api_key, auth_token):
    base_url = "https://ridewithgps.com/api/v1"
    headers = {
        "x-rwgps-api-key": api_key,
        "x-rwgps-auth-token": auth_token,
        "Content-Type": "application/json"
    }
    try:
            url = f"{base_url}/routes.json"
            params = {"page": 1}            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return True
            else:                
                return False
    except:        
        return False

def getRWToken(email, password, apiKey):
    url = "https://ridewithgps.com/api/v1/auth_tokens.json"    
    headers = {
        "x-rwgps-api-key": apiKey,
        "Content-Type": "application/json"
    }    
    payload = {
        "user": {
            "email": email,
            "password": password
        }
    }    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:            
            return response.json()["auth_token"]
        else:
            print(f"Authentication failed. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None            
    except requests.exceptions.RequestException as e:
        print(f"Error during authentication request: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing response: {str(e)}")
        return None

def checkForFiles(nextcloudUrl, username, password, remoteFolder, localFolder, remoteDone):
    try:        
        if not remoteFolder.startswith('/'):
            remoteFolder = '/' + remoteFolder
        if not remoteFolder.endswith('/'):
            remoteFolder += '/'
        if not remoteDone.startswith('/'):
            remoteDone = "/" + remoteDone
        if not remoteDone.endswith('/'):
            remoteDone += "/"    
        webdav_base = f"{nextcloudUrl}/remote.php/webdav"        
        os.makedirs(localFolder, exist_ok=True)
        propfind_url = f"{webdav_base}{remoteFolder}"
        headers = {"Depth": "1"}
        response = requests.request("PROPFIND", propfind_url, auth=HTTPBasicAuth(username, password), headers=headers)
        if response.status_code != 207:
            print(f"Error listing folder {remoteFolder}: {response.status_code} - {response.text}")
            return 0
        files = []
        tree = ElementTree.fromstring(response.content)
        for elem in tree.findall(".//{DAV:}response"):
            href = elem.find("{DAV:}href").text
            if href.lower().endswith('.zip'):
                files.append(href)
        if not files:
            print(f"Found no zip files in {remoteFolder}")
            return 0
        print(f"Found {len(files)} ZIP file(s)")

        for file_path in files:
            file_name = os.path.basename(file_path)
            local_path = os.path.join(localFolder, file_name)
            print(f"Downloading: {file_name}")            
            download_url = f"{nextcloudUrl}{file_path}"            
            response = requests.get(download_url, auth=HTTPBasicAuth(username, password))
            if response.status_code == 200:
                with open(local_path, "wb") as file:
                    file.write(response.content)
                print(f"Successfully downloaded to: {local_path}")
            else:
                print(f"Failed to download {file_name}: {response.status_code}")
                continue
            source_url = f"{nextcloudUrl}{file_path}"            
            destination_url = f"{webdav_base}{remoteFolder}{remoteDone}{file_name}"        
            move_headers = {"Destination": destination_url}
            response = requests.request("MOVE", source_url, auth=HTTPBasicAuth(username, password), headers=move_headers)
            if response.status_code in [201, 204]:  # 201 = Created, 204 = No Content
                print(f"Moved {file_name} to {remoteDone}")
            else:
                print(f"Error moving {file_name}: {response.status_code} - {response.text}")
        return len(files)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 0

def unzipFiles(localFolder):
    localF = Path(localFolder)
    for file in localF.glob("*.zip"):
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(localFolder)

def notify(msg, notifyChannel):
    url = f"https://ntfy.sh/{notifyChannel}"
    try:
        response = requests.post(url, data=msg)
        if response.status_code in [200, 201]:
            print(f"Notification sent successfully to {notifyChannel}")
            return True
        else:
            print(f"Failed to send notification. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        return False

def uploadToRWGPS(localFolder, rwgpsApiK, rwgpsAuthT, notifyChannel):
    url = "https://ridewithgps.com/trips"
    headers = {
        'x-rwgps-api-key': rwgpsApiK,
        'x-rwgps-auth-token': rwgpsAuthT
    }

    localF = Path(localFolder)
    for file in localF.glob("*.fit"):
        print(f"Uploading: {file.name}")
        files = {
            'file': (file.name, open(file, 'rb'), 'application/octet-stream')            
        }

        response = requests.post(url, headers=headers, files=files)
        if response.status_code in [200, 201, 202]:                        
            notify("Successful upload of " + str(file.name), notifyChannel)            
        else:
            print(f"Upload failed. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            notify("Failed upload of " + str(file.name), notifyChannel)

if __name__ == "__main__":
    
    #Load in Vars
    load_dotenv()
    NEXTCLOUD_URL = os.getenv("NEXTCLOUD_URL")
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    REMOTE_FOLDER = os.getenv("REMOTE_FOLDER")
    LOCAL_FOLDER = os.getenv("LOCAL_FOLDER")
    NOTIFY_CHANNEL = os.getenv("NOTIFY_CHANNEL")
    RWGPS_USER = os.getenv("RWGPS_USER")
    RWGPS_PASS = os.getenv("RWGPS_PASS")
    RWGPS_APIK = os.getenv("RWGPS_APIK")
    MAX_CHECK = os.getenv("MAX_CHECK")
    REMOTE_DONE_FOLDER = os.getenv("REMOTE_DONE_FOLDER")

    #Cleanup local folder 
    os.system('rm ' + LOCAL_FOLDER + '/*.zip')
    os.system('rm ' + LOCAL_FOLDER + '/*.fit')

    #Check for api token file
    if os.path.exists("rwGPSToken.key"):
        a = open('rwGPSToken.key', 'r')
        lines = a.readlines()
        a.close()
        for line in lines:
            RWGPS_TOKEN = str(line).strip()

        #Check if token is still valid
        if checkRWGPS(RWGPS_APIK, RWGPS_TOKEN):
            print("Auth check successful...")
        else:
            print("Auth failed, get new token...")
            auth_token = getRWToken(RWGPS_USER, RWGPS_PASS, RWGPS_APIK)
            a=open('rwGPSToken.key', 'w')
            a.write(str(auth_token['auth_token']))
            a.close()
            RWGPS_TOKEN = auth_token
    else:
        print("No token file, need to get token...")
        auth_token = getRWToken(RWGPS_USER, RWGPS_PASS, RWGPS_APIK)
        a=open('rwGPSToken.key', 'w')
        a.write(str(auth_token['auth_token']))
        a.close()
        RWGPS_TOKEN = auth_token

    #Check Nextcloud for files to process
    numFiles = checkForFiles(NEXTCLOUD_URL,USERNAME, PASSWORD, REMOTE_FOLDER, LOCAL_FOLDER, REMOTE_DONE_FOLDER)    
    if numFiles > 0:
        unzipFiles(LOCAL_FOLDER)

        uploadToRWGPS(LOCAL_FOLDER, RWGPS_APIK, RWGPS_TOKEN, NOTIFY_CHANNEL)
        
    print("Run complete, tidying up...")
    os.system('rm ' + LOCAL_FOLDER + '/*.zip')
    os.system('rm ' + LOCAL_FOLDER + '/*.fit')            

    

        
        

