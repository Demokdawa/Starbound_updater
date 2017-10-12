#!/usr/bin/python
# -*- coding: utf-8 -*-
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

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class DictSenderServicer(starbound_pb2_grpc.DictSenderServicer):

    modPath = '/home/steam/starbound/mods'

    def send_dict(self, request, context):
        random_dict = self.find_all_hash
        #return starbound_pb2.MyDict(dictionary=random_dict)
        return random_dict

    def find_all_hash(self):
        MyDict = {}
        for filename in os.listdir(self.modPath):
            if os.path.isdir(self.modPath + '/' + filename):
                MyDict[filename] = \
                    self.get_folder_hash(filename)
            else:
                MyDict[filename] = \
                    self.get_file_hash(filename)
        print (MyDict)
        return MyDict

    def get_folder_hash(self, filename):
        hash = checksumdir.dirhash(self.modPath + '/'
                + filename)
        return hash

    def get_file_hash(self, filename):
        openedFile = open(self.modPath + '/' + filename, 'rb')
        readFile = openedFile.read()
        md5Hash = hashlib.md5(readFile)
        md5Hashed = md5Hash.hexdigest()
        return md5Hashed

def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        starbound_pb2_grpc.add_DictSenderServicer_to_server(DictSenderServicer(),
                server)
        server.add_insecure_port('[::]:50051')
        server.start()
        print ("Server started !")
        print (DictSenderServicer.find_all_hash())
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)

if __name__ == '__main__':
    serve()
#servicer = DictSenderServicer()
#servicer.find_all_hash()
#servicer.serve()
