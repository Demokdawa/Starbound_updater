#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import pwd
import grp

# CONFIG-PART | THAT IS THE ONLY LINES YOU HAVE TO MODIFY TO CONFIGURE THE ZIP CREATOR

zip_repo = '/home/starb-ftp/starbound/zips'
install_path = '/home/starb-ftp/starbound'
target_path = '/home/starb-ftp/starbound_server/mods/'
# Name of user and group to access the FTP files
UserID = "starb-ftp"
GroupID = "starb-ftp"


for filename in os.listdir(target_path):
    if os.path.isdir(target_path + filename):
        zip_file = install_path + "/zips/" + filename + ".zip"
        if os.path.exists(zip_file):
            os.remove(install_path + "/zips/" + filename + ".zip")
        shutil.make_archive(filename, "zip", target_path, filename)
        shutil.move(os.getcwd() + "/" + filename + ".zip", install_path + "/zips/" + filename + ".zip")
        os.chown(install_path + "/zips/" + filename + ".zip", pwd.getpwnam(UserID).pw_uid, grp.getgrnam(GroupID).gr_gid)
        print(filename + "   [Archivé] !")

print("Terminé !")
