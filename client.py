from __future__ import print_function
from pathlib import Path
from os import path
from concurrent import futures
import time
import math
import checksumdir
import os
import hashlib
import json
import grpc
import starbound_pb2
import starbound_pb2_grpc

modPath = "C:\Users\Demokdawa\Documents\mods"

def get_serv_dict():
    channel = grpc.insecure_channel('163.172.30.174:50051')
    stub = starbound_pb2_grpc.DictSenderStub(channel)
    response = stub.send_dict(starbound_pb2.Empty())
    serv_dict = dict(response.dictionary)
    return serv_dict

def find_all_hash():
    client_dict = {}
    for filename in os.listdir(modPath):
        if os.path.isdir(modPath + "\\" + filename):
            client_dict[filename] = \
                get_folder_hash(filename)
        else:
            client_dict[filename] = \
                get_file_hash(filename)
    return client_dict

def get_folder_hash(filename):
    hash = checksumdir.dirhash(modPath + "\\"
            + filename)
    return hash

def get_file_hash(filename):
    openedFile = open(modPath + "\\" + filename, 'rb')
    readFile = openedFile.read()
    md5Hash = hashlib.md5(readFile)
    md5Hashed = md5Hash.hexdigest()
    return md5Hashed

client_dict = find_all_hash()
serv_dict = get_serv_dict()

setClient = set(client_dict.items())
setServ = set(serv_dict.items())

only_client = setClient - setServ
only_server = setServ - setClient

print(only_client)
print(only_server)
#are only on client:
items_only_in_client = list(only_client)
for x in items_only_in_client:
    #print("Client seulement " + client_dict[x])
    print(".")


#are only on serv:
items_only_in_serv = list(only_server)
for x in items_only_in_serv:
    #print("Serveur seulement " + serv_dict[x])
    print(".")
