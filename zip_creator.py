import os
import shutil
import pwd
import grp

install_path = '/home/starb-ftp/starbound'
target_path = '/home/starb-ftp/starbound_server/mods/'
updater_path = '/home/starb-ftp/Starbound_updater'
UserID = "starb-ftp"
GroupID = "starb-ftp"


for filename in os.listdir(target_path):
    if os.path.isdir(target_path + filename):
        zip_file = install_path + "/zips" + filename + ".zip"
        if os.path.exists(zip_file):
            os.remove(install_path + "/zips/" + filename + ".zip")
        shutil.make_archive(filename, "zip", target_path, filename)
        shutil.move(updater_path + "/" + filename + ".zip", install_path + "/zips/" + filename + ".zip")
        os.chown(install_path + "/zips/" + filename + ".zip", pwd.getpwnam(UserID).pw_uid, grp.getgrnam(GroupID).gr_gid)
        print(filename + "   [Archivé] !")

print("Terminé !")
