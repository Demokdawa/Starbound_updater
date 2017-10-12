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

def get_serv_dict():
    channel = grpc.insecure_channel('163.172.30.174:50051')
    stub = starbound_pb2_grpc.DictSenderStub(channel)
    response = stub.send_dict(starbound_pb2.Empty())
    serv_dict = dict(response.dictionary)
    return serv_dict

def find_all_hash():
    client_dict = {}
    for filename in os.listdir(modPath):
        if os.path.isdir(modPath + '/' + filename):
            client_dict[filename] = \
                get_folder_hash(filename)
        else:
            client_dict[filename] = \
                get_file_hash(filename)
    return client_dict

def get_folder_hash(filename):
    hash = checksumdir.dirhash(modPath + '/'
            + filename)
    return hash

def get_file_hash(filename):
    openedFile = open(modPath + '/' + filename, 'rb')
    readFile = openedFile.read()
    md5Hash = hashlib.md5(readFile)
    md5Hashed = md5Hash.hexdigest()
    return md5Hashed


#A_dict = {'hash1' : "jsonobj1","hash2" : "jsonobj2"}
#B_dict = {'hash3' : "jsonobj3","hash2" : "jsonobj2"}

#client_dict = {'hash1' : "jsonobj1","hash2" : "jsonobj2"}
#serv_dict = {'hash3' : "jsonobj3","hash2" : "jsonobj2"}

#setA = set(A_dict.keys())
#setB = set(B_dict.keys())

setClient = set(get_serv_dict().keys())
setServ = set(find_all_hash().keys())

#print(setA - setB)
#print(setB - setA)

print(setClient - setServ)
print(setServ - setClient)

#are only on a:
#items_only_in_a = list(setA)
#for x in items_only_in_a:
#    del A_dict[x]

#items_only_in_b = list(setB)
#for x in items_only_in_b:
#    download(B_dict[x])
