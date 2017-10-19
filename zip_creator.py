from os import path
import zipfile
import sys, os
import shutil


installPath = os.getcwd()
target_path = os.getcwd() + "/mods/"

for filename in os.listdir(target_path):
    if os.path.isdir(target_path + filename):
        shutil.make_archive(filename, "zip", target_path, filename)
        shutil.move(installPath + "/" + filename + ".zip", installPath + "/zips/" + filename + ".zip")

print ("Terminé !")
