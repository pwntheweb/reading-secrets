import os
import glob
import stat
import shutil

if not os.path.exist("SteamAuthFiles"):
    os.mkdir("SteamAuthFiles")

steam_dir = "D:\\Steam"
steam_loginusers_path = steam_dir+"\\config\\loginusers.vdf"
steam_config_path = steam_dir+"\\config\\config.vdf"

def getSteamSSFNFileFromPath(file_path):
    """
        Loop through Steam "SSFN" files. Hidden one is the 'real' one. Non-Hidden is a decoy.
        We should not need the non-hidden files.
    """
    for file in glob.glob(file_path+"\\ssfn*"):
        if bool(os.stat(file).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN) == True:
            return file

def copyAuthFiles():
    """
        Here we create copies of the SSFN file and of the user's config files.
    """
    shutil.copy(steam_loginusers_path, "SteamAuthFiles\\loginusers.vdf")
    shutil.copy(steam_config_path, "SteamAuthFiles\\config.vdf")
    shutil.copy(getSteamSSFNFile(steam_dir), "SteamAuthFiles\\"+ssfn_file.split("\\")[len(ssfn_file.split("\\"))-1])

def unloadAuthFiles():
    """
        Looks to see if steam files already exist, if so we remove them and copy our old files to the new location.
    """
    loginusers_copy = "SteamAuthFiles\\loginusers.vdf"
    config_copy = "SteamAuthFiles\\config.vdf"
    ssfn_copy = getSteamSSFNFileFromPath("SteamAuthFiles")
    if os.path.exists(steam_loginusers_path):
        os.remove(steam_loginusers_path)
    if os.path.exists(steam_config_path):
        os.remove(steam_config_path)
    if getSteamSSFNFileFromPath(steam_dir) != None:
        os.remove(getSteamSSFNFileFromPath(steam_dir))
    shutil.copy(loginusers_copy, steam_loginusers_path)
    shutil.copy(config_copy, steam_config_path)
    shutil.copy(ssfn_copy, steam_dir+"\\"+ssfn_copy.split("\\")[len(ssfn_copy.split("\\"))-1])
    os.system('attrib +h '+steam_dir+"\\"+ssfn_copy.split("\\")[len(ssfn_copy.split("\\"))-1])
