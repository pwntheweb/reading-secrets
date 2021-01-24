import sqlite3
import shutil
import os
import re
import win32crypt

localappdata = os.getenv('LOCALAPPDATA')

conn = sqlite3.connect(localappdata+"\\Steam\\htmlcache\\Cookies")
cur = conn.cursor()
#cur.execute("select name from sqlite_master where type = 'table';")
cur.execute("SELECT * FROM cookies")
names = list(map(lambda x: x[0], cur.description))


res = cur.fetchall()
for rr in res:
    print("Creation UTC({})".format(rr[0]))
    print("Host({})".format(rr[1]))
    print("Name({})".format(rr[2]))
    print("Value({})".format(rr[3]))
    print("Path({})".format(rr[4]))
    print("Expires UTC({})".format(rr[5]))
    print("Is Secure({})".format(rr[6]))
    print("Is HTTP Only({})".format(rr[7]))
    print("Last Access UTC({})".format(rr[8]))
    print("Has Expires({})".format(rr[9]))
    print("Is Persistent({})".format(rr[10]))
    print("Priority({})".format(rr[11]))
    print("Encrypted Value({})".format(rr[12]))
    key = str(win32crypt.CryptUnprotectData(rr[12], None, None, None, 0)[1].decode('ANSI'))
    print("Decrypted Value({})".format(key))
    print("SameSite({})".format(rr[13]))
    print("\n\n")
