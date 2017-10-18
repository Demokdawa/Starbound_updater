from ftplib import FTP
import ftputil
#ftp = FTP('163.172.30.174', 'starb_ftp', 'Darkbarjot78')
dirpath = "AnTiHair.pak"
target_path = "C:\\Users\\PRAN152\\Documents\\GitHub\\Starbound_updater\\mods\\"
main_path = "/starbound/mods/"
ftpserv = ftputil.FTPHost("163.172.30.174", "starb_ftp", "Darkbarjot78")

ftpserv.download(main_path + dirpath, target_path + dirpath)
