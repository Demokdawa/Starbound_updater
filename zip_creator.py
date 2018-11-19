#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import pwd
import grp

# CONFIG-PART | THAT IS THE ONLY LINES YOU HAVE TO MODIFY TO CONFIGURE THE ZIP CREATOR----------------------------------

# The folder where the zips files will be stored - make sure the permissions are correctly set
zip_repo = '/home/starb-ftp/starbound/zips/'
# The folder where the mod files are located - aka starbound server mod folder
target_path = '/home/starb-ftp/starbound_server/mods/'
# Name of user and group to access the FTP files - make sure the user have the correct permissions
user_id = "starb-ftp"
group_id = "starb-ftp"

# END OF CONFIG-PART ! -------------------------------------------------------------------------------------------------


for filename in os.listdir(target_path):
    if os.path.isdir(target_path + filename):
        zip_file = zip_repo + filename + ".zip"
        if os.path.exists(zip_file):
            os.remove(zip_repo + filename + ".zip")
        shutil.make_archive(filename, "zip", target_path, filename)
        shutil.move(os.getcwd() + "/" + filename + ".zip", zip_repo + filename + ".zip")
        os.chown(zip_repo + filename + ".zip", pwd.getpwnam(user_id).pw_uid, grp.getgrnam(group_id).gr_gid)
        print(filename + "   [Archivé] !")

print("Terminé !")
