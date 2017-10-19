from __future__ import print_function
from pathlib import Path
from os import path
from concurrent import futures
from time import sleep
from ftplib import FTP
import math
import checksumdir
import hashlib
import grpc
import starbound_pb2
import starbound_pb2_grpc
import sys, os
import shutil
import ftputil
import zipfile

installPath = os.getcwd()
modPath = os.getcwd() + "\\mods\\"
remotePath = "/starbound/mods/"
sftp_serv = ftputil.FTPHost("163.172.30.174", "starb_ftp", "Darkbarjot78")
zipFolder = "/starbound/zips/"

def get_serv_dict():
    print("Recuperation des informations serveur...", flush=True)
    channel = grpc.insecure_channel('163.172.30.174:50051')
    stub = starbound_pb2_grpc.DictSenderStub(channel)
    response = stub.send_dict(starbound_pb2.Empty())
    serv_dict = dict(response.dictionary)
    print("Termine !")
    return serv_dict

def find_all_hash(target_path):
    hash_dict = {}
    print("Recuperation des informations locales...", flush=True)
    for filename in os.listdir(target_path):
        if os.path.isdir(target_path + filename):
            hash_dict[filename] = \
                get_folder_hash(target_path, filename)
        else:
            hash_dict[filename] = \
                get_file_hash(target_path, filename)
    print("Termine !")
    return hash_dict

def get_folder_hash(target_path, filename):
    hash = checksumdir.dirhash(target_path + filename)
    return hash

def get_file_hash(target_path, filename):
    openedFile = open(target_path + filename, 'rb')
    readFile = openedFile.read()
    md5Hash = hashlib.md5(readFile)
    md5Hashed = md5Hash.hexdigest()
    return md5Hashed

def remove_extra_files(target_path, client_dict_input, serv_dict_input):
    for filename_delete, client_hash in client_dict_input.items():
        server_hash = serv_dict_input.get(filename_delete)
        if server_hash != client_hash:
            print("Suppression de " + filename_delete, flush=True)
            if os.path.isfile(target_path + filename_delete):
                os.remove(target_path + filename_delete)
            elif os.path.isdir(target_path + filename_delete + "\\"):
                shutil.rmtree(target_path + filename_delete + "\\", ignore_errors=True)
            else:
                print("Erreur lors de la suppression de" + filename_delete, flush=True)

def download_extra_files(target_path, remote_path, zip_folder, client_dict_input, serv_dict_input, sftp_serv):
    for filename_download, server_hash in serv_dict_input.items():
        client_hash = client_dict_input.get(filename_download)
        if client_hash != server_hash:
            if os.path.splitext(target_path + filename_download)[1] == ".pak":
                print("Telechargement de " + filename_download, flush=True)
                download_file(target_path, remote_path, filename_download, sftp_serv)
            else :
                print("Telechargement de " + filename_download, flush=True)
                #download_folder(target_path, remote_path, filename_download, sftp_serv)
                download_zip_and_extract(target_path, zip_folder, filename_download + ".zip", sftp_serv)

def download_file(target_path, remote_path, name_to_dl, sftp_serv):
    local_path_to_dl = target_path + name_to_dl
    remote_path_from_dl = remote_path + name_to_dl
    sftp_serv.download(remote_path_from_dl, local_path_to_dl)

def download_zip_and_extract(target_path, zip_path, name_to_dl, sftp_serv):
    local_path_to_dl = target_path + name_to_dl
    remote_path_from_dl = zip_path + name_to_dl
    sftp_serv.download(remote_path_from_dl, local_path_to_dl)

    with zipfile.ZipFile(local_path_to_dl,"r") as zip_ref:
        zip_ref.extractall(target_path)

    os.remove(local_path_to_dl)

def download_folder(target_path, remote_path, name_to_dl, sftp_serv):
    local_path_to_dl = target_path + name_to_dl
    remote_path_from_dl = remote_path + name_to_dl
    if not sftp_serv.path.exists(remote_path_from_dl):
        return
    if not os.path.exists(local_path_to_dl):
        os.makedirs(local_path_to_dl)

    dirlist = sftp_serv.listdir(remote_path_from_dl)
    for i in dirlist:
        if sftp_serv.path.isdir(remote_path_from_dl + '/' + i):
            download_folder(target_path, remote_path, name_to_dl + '/' + i, sftp_serv)
        else:
            download_file(target_path, remote_path, name_to_dl + '/' + i, sftp_serv)

if os.path.isfile(installPath + "\\win64\\" + "starbound.exe"):
    print("Dossier officiel starbound detecte !", flush=True)
    sleep(3)
    client_dict = find_all_hash(modPath)
    serv_dict = get_serv_dict()
    remove_extra_files(modPath, client_dict, serv_dict)
    download_extra_files(modPath, remotePath, zipFolder, client_dict, serv_dict, sftp_serv)
    print("Mise a jour terminee !", flush=True)
else :
    print("Le script n'est pas place dans le dossier Starbound !", flush=True)
    sleep(3)
