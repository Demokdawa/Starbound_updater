#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from time import sleep
from threading import Thread
from queue import Queue
import checksumdir
import hashlib
import grpc
import starbound_pb2
import starbound_pb2_grpc
import os
import shutil
import ftputil
import zipfile

# CONFIG-PART | THAT IS THE ONLY LINES YOU HAVE TO MODIFY TO CONFIGURE THE ZIP CREATOR----------------------------------

# The folder where the zips files will be stored - make sure the permissions are correctly set - It's and FTP PATH
zip_repo = '/starbound/zips/'
# The folder where the caracters will be backuped on the server - It's and FTP PATH
backup_folder = '/starbound/backups/'
# Specify the address, user, and password to access ftp
ftp_serv = ftputil.FTPHost("195.154.173.75", "starb-ftp", "Blackstones32")
# By default, the root directory where the starbound client files are located - NO CHANGES NEEDED
install_path = os.getcwd()
# By default, the directory where the mods files will be downloaded for the client - NO CHANGES NEEDED
mod_path_client = install_path + "\\mods\\"
# The folder where the mod files are located - aka starbound server mod folder - It's and FTP PATH
mod_path_server = "/starbound_server/mods/"
# The ip and port used by grpc to connect client and server - make sure to open the port on your firewall
grpc_connect = '195.154.173.75:50051'

# END OF CONFIG-PART ! -------------------------------------------------------------------------------------------------

# Variables statiques
thread_count = 10

# Variables globales
hashdone = 0

# Déclaration des objets
hash_queue = Queue()
hash_dict = {}


# Classe qui calcule les hash sur plusieurs threads a partir de la queue (queue)
class HashCompute(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        global hashdone
        while True:
            target_path, filename = self.queue.get()
            if os.path.isdir(target_path + filename):
                hash_dict[filename] = checksumdir.dirhash(target_path + filename)
            else:
                opened_file = open(target_path + filename, 'rb')
                read_file = opened_file.read()
                md5_hash = hashlib.md5(read_file)
                hash_dict[filename] = md5_hash.hexdigest()
            hashdone += 1
            self.queue.task_done()


# Classe compteur de progression hashing (queue, hashtotal)
class QueueCounter(Thread):
    def __init__(self, queue, hashtotal):
        Thread.__init__(self)
        self.queue = queue
        self.hashtotal = hashtotal

    def run(self):
        global hashdone
        while hashdone < self.hashtotal:
            print(str(hashdone) + '/' + str(self.hashtotal), end='\r', flush=True)


# Récupère le dictionnaire serveur
def get_serv_dict():
    print("Getting update data from server...", flush=True)
    channel = grpc.insecure_channel(grpc_connect)
    stub = starbound_pb2_grpc.DictSenderStub(channel)
    response = stub.send_dict(starbound_pb2.Empty())
    serv_dict_build = dict(response.dictionary)
    print("Done !")
    return serv_dict_build


# Creer le dictionnaire client et la queue
def build_client_dict(target_path):
    print("Getting local mods data...", flush=True)
    for filename in os.listdir(target_path):
        hash_queue.put((target_path, filename))
    hashtotal = hash_queue.qsize()
    thread_creator(hash_queue, thread_count, hashtotal)
    hash_queue.join()
    print("Done !")
    print(hash_dict)
    return hash_dict


# Creer les threads de calcul hash
def thread_creator(queue, thread_count_value, hashtotal):
    for _ in range(thread_count_value):
        hash_compute = HashCompute(queue)
        hash_compute.daemon = True
        hash_compute.start()
    queue_counter = QueueCounter(queue, hashtotal)
    queue_counter.daemon = True
    queue_counter.start()


# Supprime les mods en trop
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


# Telecharge les mods manquants
def download_extra_files(target_path, remote_path, zip_folder, client_dict_input, serv_dict_input, sftp_serv_address):
    for filename_download, server_hash in serv_dict_input.items():
        client_hash = client_dict_input.get(filename_download)
        if client_hash != server_hash:
            if os.path.splitext(target_path + filename_download)[1] == ".pak":
                print("Download of " + filename_download, flush=True)
                download_file(target_path, remote_path, filename_download, sftp_serv_address)
            else:
                print("Download of " + filename_download, flush=True)
                download_zip_and_extract(target_path, zip_folder, filename_download + ".zip", sftp_serv_address)


# Telecharge un fichier
def download_file(target_path, remote_path, name_to_dl, sftp_serv_address):
    local_path_to_dl = target_path + name_to_dl
    remote_path_from_dl = remote_path + name_to_dl
    sftp_serv_address.download(remote_path_from_dl, local_path_to_dl)


# Telecharge un zip temporaire et l'extrait
def download_zip_and_extract(target_path, zip_path, name_to_dl, sftp_serv_address):
    local_path_to_dl = target_path + name_to_dl
    remote_path_from_dl = zip_path + name_to_dl
    sftp_serv_address.download(remote_path_from_dl, local_path_to_dl)

    with zipfile.ZipFile(local_path_to_dl, "r") as zip_ref:
        zip_ref.debug = 3
        zip_ref.extractall(target_path)
    os.remove(local_path_to_dl)


# Sauvegarde les données de personnage locales sur le serveur
def backup_char(local_path, remote_bck_folder, sftp_serv_address):
    local_save = local_path + "\\storage\\player\\"
    print("Backuping local characters...", flush=True)
    for filename in os.listdir(local_save):
        sftp_serv_address.upload(local_save + filename, remote_bck_folder + filename)
    print("Done !", flush=True)


if __name__ == '__main__':
    if os.path.isfile(install_path + "\\win64\\" + "starbound.exe"):
        print("Starbound installation detected !", flush=True)
        backup_char(install_path, backup_folder, ftp_serv)
        #client_dict = build_client_dict(mod_path_client)
        serv_dict = get_serv_dict()
        print(serv_dict)
        remove_extra_files(mod_path_client, client_dict, serv_dict)
        download_extra_files(mod_path_client, mod_path_server, zip_repo, client_dict, serv_dict, ftp_serv)
        print("Update done !", flush=True)
    else:
        print("Starbound installation folder not found", flush=True)
        sleep(3)
