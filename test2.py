from ftplib import FTP
from os import path
import zipfile
import ftputil
import sys, os


sftp_serv = ftputil.FTPHost("163.172.30.174", "starb_ftp", "Darkbarjot78")
installPath = os.getcwd()
target_path = os.getcwd() + "\\mods\\"
remote_path = "/starbound/mods/"
filename_download = "data.zip"


def download_file(target_path, remote_path, name_to_dl, sftp_serv):
    local_path_to_dl = target_path + name_to_dl
    remote_path_from_dl = remote_path + name_to_dl
    sftp_serv.download(remote_path_from_dl, local_path_to_dl)

download_file(target_path, remote_path, filename_download, sftp_serv)
