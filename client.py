# coding=utf-8
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
import sys

# Variables statiques de paramètrage
zipFolder = "/starbound/zips/"
backup_folder = "/starbound/backups/"
sftp_serv = ftputil.FTPHost("163.172.30.174", "starb_ftp", "Darkbarjot78")
installPath = os.getcwd()
modPath = installPath + "\\mods\\"
remotePath = "/starbound/mods/"
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
            "self.progressBar(hashdone, self.hashtotal)"


# Récupère le dictionnaire serveur
def get_serv_dict():
    print("Getting update data from server...", flush=True)
    channel = grpc.insecure_channel('163.172.30.174:50051')
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


# FONCTION INUTILISEE - Telecharge un dossier depuis le serveur
def download_folder(target_path, remote_path, name_to_dl, sftp_serv_address):
    local_path_to_dl = target_path + name_to_dl
    remote_path_from_dl = remote_path + name_to_dl
    if not sftp_serv_address.path.exists(remote_path_from_dl):
        return
    if not os.path.exists(local_path_to_dl):
        os.makedirs(local_path_to_dl)

    dir_list = sftp_serv_address.listdir(remote_path_from_dl)
    for i in dir_list:
        if sftp_serv_address.path.isdir(remote_path_from_dl + '/' + i):
            download_folder(target_path, remote_path, name_to_dl + '/' + i, sftp_serv_address)
        else:
            download_file(target_path, remote_path, name_to_dl + '/' + i, sftp_serv_address)


# Sauvegarde les données de personnage locales sur le serveur
def backup_char(local_path, remote_bck_folder, sftp_serv_address):
    local_save = local_path + "\\storage\\player\\"
    print("Backuping local characters...", flush=True)
    for filename in os.listdir(local_save):
        sftp_serv_address.upload(local_save + filename, remote_bck_folder + filename)
    print("Done !", flush=True)


# FONCTION INUTILISEE - Barre de chargement progressive
def progress_bar(value, end_value, bar_length=20):
    percent = float(value) / end_value
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()


# CLASSE INUTILISEE - Classe qui supprime les mods en trop
class RemoveUnusedMods:
    def __init__(self, modPath, client_dict, serv_dict):
        self.target_path = modPath
        self.client_dict_input = client_dict
        self.serv_dict_input = serv_dict

    def remove_extra_files_lol(self):
        for filename_delete, client_hash in self.client_dict_input.items():
            server_hash = self.serv_dict_input.get(filename_delete)
            if server_hash != client_hash:
                print("Suppression de " + filename_delete, flush=True)
                if os.path.isfile(self.target_path + filename_delete):
                    os.remove(self.target_path + filename_delete)
                elif os.path.isdir(self.target_path + filename_delete + "\\"):
                    shutil.rmtree(self.target_path + filename_delete + "\\", ignore_errors=True)
                else:
                    print("Erreur lors de la suppression de" + filename_delete, flush=True)


if __name__ == '__main__':
    if os.path.isfile(installPath + "\\win64\\" + "starbound.exe"):
        print("Starbound installation detected !", flush=True)
        backup_char(installPath, backup_folder, sftp_serv)
        client_dict = build_client_dict(modPath)
        serv_dict = get_serv_dict()
        'remove = RemoveUnusedMods(modPath, client_dict, serv_dict)'
        'remove.remove_extra_files'
        remove_extra_files(modPath, client_dict, serv_dict)
        download_extra_files(modPath, remotePath, zipFolder, client_dict, serv_dict, sftp_serv)
        print("Update done !", flush=True)
    else:
        print("Starbound installation folder not found", flush=True)
        sleep(3)
