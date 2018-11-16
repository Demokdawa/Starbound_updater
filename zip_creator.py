from os import path
from pathlib import Path
import zipfile
import sys, os
import shutil


install_path = '/home/starb-ftp/starbound'
target_path = '/home/starb-ftp/starbound_server/mods/'
updater_path = '/home/starb-ftp/Starbound_updater'

for filename in os.listdir(target_path):
    if os.path.isdir(target_path + filename):
        zip_file = install_path + "/zips" + filename + ".zip"
        if os.path.exists(zip_file):
            os.remove(install_path + "/zips/" + filename + ".zip")
        shutil.make_archive(filename, "zip", target_path, filename)
        shutil.move(updater_path + "/" + filename + ".zip", install_path + "/zips/" + filename + ".zip")
        print(filename + "   [Archivé] !")

print("Terminé !")
