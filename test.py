from ftplib import FTP
import ftputil
import sys
import time
import hashlib

dirpath = "Optimizebound.pak"
target_path = "C:\\Users\\PRAN152\\Documents\\GitHub\\Starbound_updater\\mods\\"
main_path = "/starbound/mods/"
ftpserv = ftputil.FTPHost("163.172.30.174", "starb_ftp", "Darkbarjot78")
total_size = 0
received = 0

def test_callback(chunk):
    received += len(chunk)
    print("     {} Progress : {}Kb / {}Kb".format(
        'Uploading', float(received)/1000, total_size), end='\r', flush=True)

def upload(dirpath, target_path, main_path):
    def test_callback(i):
        print(" .", end='')
    ftpserv.download(main_path + dirpath, target_path + dirpath, callback=test_callback)

upload(dirpath, target_path, main_path)
