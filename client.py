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

#Variables statiques de paramètrage
zipFolder = "/starbound/zips/"
backup_folder = "/starbound/backups/"
sftp_serv = ftputil.FTPHost("163.172.30.174", "starb_ftp", "Darkbarjot78")
installPath = os.getcwd()
modPath = installPath + "\\mods\\"
remotePath = "/starbound/mods/"
thread_count = 10

#Variables globales
hashdone = 0

#Déclaration des objets
queue = Queue()
hash_dict = {}

#Classe qui calcule les hash sur plusieurs threads a partir de la queue
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
                openedFile = open(target_path + filename, 'rb')
                readFile = openedFile.read()
                md5Hash = hashlib.md5(readFile)
                hash_dict[filename] = md5Hash.hexdigest()
            hashdone += 1
            self.queue.task_done()

class QueueCounter(Thread):

    def __init__(self, queue, hashtotal):
        Thread.__init__(self)
        self.queue = queue
        self.hashtotal = hashtotal

    def run(self):
        global hashdone
        while hashdone < self.hashtotal:
            print(str(hashdone) + '/' + str(self.hashtotal), end='\r', flush=True)

#Récupère le dictionnaire serveur
def get_serv_dict():
    print("Recuperation des informations serveur...", flush=True)
    channel = grpc.insecure_channel('163.172.30.174:50051')
    stub = starbound_pb2_grpc.DictSenderStub(channel)
    response = stub.send_dict(starbound_pb2.Empty())
    serv_dict = dict(response.dictionary)
    print("Termine !")
    return serv_dict

#Creer le dictionnaire client et la queue
def build_client_dict(target_path):
    print("Recuperation des informations locales...", flush=True)
    for filename in os.listdir(target_path):
        queue.put((target_path, filename))
    print("Queue up !")
    hashtotal = queue.qsize()
    thread_creator(queue, thread_count, hashtotal)
    queue.join()
    print("Hash dict builded !")
    return hash_dict

#Creer les threads de calcul hash
def thread_creator(queue, thread_count, hashtotal):
    for i in range(thread_count):
        hashcompute = HashCompute(queue)
        hashcompute.daemon = True
        hashcompute.start()
    queuecounter = QueueCounter(queue, hashtotal)
    queuecounter.daemon = True
    queuecounter.start()

#Supprime les mods en trop
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

#Telecharge les mods manquants
def download_extra_files(target_path, remote_path, zip_folder, client_dict_input, serv_dict_input, sftp_serv):
    for filename_download, server_hash in serv_dict_input.items():
        client_hash = client_dict_input.get(filename_download)
        if client_hash != server_hash:
            if os.path.splitext(target_path + filename_download)[1] == ".pak":
                print("Telechargement de " + filename_download, flush=True)
                download_file(target_path, remote_path, filename_download, sftp_serv)
            else:
                print("Telechargement de " + filename_download, flush=True)
                download_zip_and_extract(target_path, zip_folder, filename_download + ".zip", sftp_serv)

#Telecharge un fichier
def download_file(target_path, remote_path, name_to_dl, sftp_serv):
    local_path_to_dl = target_path + name_to_dl
    remote_path_from_dl = remote_path + name_to_dl
    sftp_serv.download(remote_path_from_dl, local_path_to_dl)

#Telecharge un zip temporaire et l'extrait
def download_zip_and_extract(target_path, zip_path, name_to_dl, sftp_serv):
    local_path_to_dl = target_path + name_to_dl
    remote_path_from_dl = zip_path + name_to_dl
    sftp_serv.download(remote_path_from_dl, local_path_to_dl)

    with zipfile.ZipFile(local_path_to_dl, "r") as zip_ref:
        zip_ref.debug = 3
        zip_ref.extractall(target_path)
    os.remove(local_path_to_dl)

#FONCTION INUTILISEE - Telecharge un dossier depuis le serveur
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

#Sauvegarde les données de personnage locales sur le serveur
def backup_char(local_path, remote_bck_folder, sftp_serv):
    local_save = local_path + "\\storage\\player\\"
    print("Sauvegarde du personnage...", flush=True)
    for filename in os.listdir(local_save):
        sftp_serv.upload(local_save + filename, remote_bck_folder + filename)
    print("Terminé !", flush=True)


if __name__ == '__main__':
    if os.path.isfile(installPath + "\\win64\\" + "starbound.exe"):
        print("Dossier officiel starbound detecte !", flush=True)
        sleep(1)
        "backup_char(installPath, backup_folder, sftp_serv)"
        sleep(1)
        client_dict = build_client_dict(modPath)
        serv_dict = get_serv_dict()
        remove_extra_files(modPath, client_dict, serv_dict)
        download_extra_files(modPath, remotePath, zipFolder, client_dict, serv_dict, sftp_serv)
        print("Mise a jour terminee !", flush=True)
    else:
        print("Le script n'est pas place dans le dossier Starbound !", flush=True)
        sleep(3)
