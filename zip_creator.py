from os import path
from pathlib import Path
import zipfile
import sys, os
import shutil


installPath = '/home/starb-ftp/starbound'
target_path = '/home/starb-ftp/starbound_server/mods/'

for filename in os.listdir(target_path):
    if os.path.isdir(target_path + filename):
        zip_file = installPath + "/zips" + filename + ".zip"
        if os.path.exists(zip_file):
            os.remove(installPath + "/zips/" + filename + ".zip")
        shutil.make_archive(filename, "zip", target_path, filename)
        shutil.move(installPath + "/" + filename + ".zip", installPath + "/zips/" + filename + ".zip")
        print (filename + "   [Archivé] !")

print ("Terminé !")
