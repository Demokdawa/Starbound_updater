from __future__ import print_function
from pathlib import Path
from os import path
from concurrent import futures
from time import sleep
import math
import checksumdir
import hashlib
import grpc
import starbound_pb2
import starbound_pb2_grpc
import sys, os
import shutil
import requests

installPath = os.getcwd()
modPath = os.getcwd() + "\\mods\\"

def get_serv_dict():
    print("Recupération des informations serveur...")
    channel = grpc.insecure_channel('163.172.30.174:50051')
    stub = starbound_pb2_grpc.DictSenderStub(channel)
    response = stub.send_dict(starbound_pb2.Empty())
    serv_dict = dict(response.dictionary)
    print("Termine !")
    return serv_dict

def find_all_hash(target_path):
    hash_dict = {}
    print("Recupération des informations locales...")
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
    extra_files = set(client_dict_input) - set(serv_dict_input)
    for filename_delete in extra_files:
        print("Suppresion de " + filename_delete)
        if os.path.isfile(target_path + filename_delete):
            os.remove(target_path + filename_delete)
        elif os.path.isdir(target_path + filename_delete + "\\"):
            shutil.rmtree(target_path + filename_delete + "\\", ignore_errors=True)
        else:
            print("Erreur lors de la suppression de" + filename_delete)

def download_extra_files(target_path, client_dict_input, serv_dict_input):
    for filename_download, server_hash in serv_dict_input.items():
        client_hash = client_dict_input.get(filename_download)
        if client_hash != server_hash:
            if os.path.splitext(target_path + filename_download)[1] == ".pak":
                print("Telechargement de " + filename_download)
                print(download_file(target_path, "https://zenmap.xyz/mods/" + filename_download))
            else :
                print("taeour")
                print(filename_download)

def download_file(target_path, url):
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(target_path + local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=256):
            if chunk:
                f.write(chunk)
    return local_filename

if os.path.isfile(installPath + "\\" + "Starbound.exe"):
    print("Dossier officiel starbound detecté !")
    sleep(3)
    client_dict = find_all_hash(modPath)
    serv_dict = get_serv_dict()
    #remove_extra_files(modPath, client_dict, serv_dict)
    download_extra_files(modPath, client_dict, serv_dict)
else :
    print("Le script n'est pas place dans le dossier Starbound !")
    sleep(3)
