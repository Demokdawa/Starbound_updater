import pysftp, os
from stat import S_ISDIR
import pysftp

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

sftp = pysftp.Connection(host="163.172.30.174", username="root",password="Darkbarjot78", cnopts=cnopts)

dirpath = "AnTiHair.pak"
target_path = "C:\\Users\\PRAN152\\Documents\\GitHub\\Starbound_updater\\mods\\"
main_path = "/home/steam/starbound/mods/"

def grab_dir_rec(sftp, dirpath):
    local_path = target_path + dirpath
    full_path = main_path + dirpath
    if not sftp.exists(full_path):
        return
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    dirlist = sftp.listdir(remotepath=full_path)
    for i in dirlist:
        if sftp.isdir(full_path + '/' + i):
            grab_dir_rec(sftp, dirpath + '/' + i)
        else:
            grab_file(sftp, dirpath + '/' + i)
			
def grab_file(sftp, dirpath):
    local_path = target_path + dirpath
    full_path = main_path + dirpath
    sftp.get(main_path + dirpath, local_path)
			
#grab_dir_rec(sftp, dirpath)
grab_file(sftp, dirpath)