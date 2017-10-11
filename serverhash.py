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

try:
    while True:


        def send_dict(self, request, context):
            feature = get_feature(self.db, request)
            if feature is None:
                return starbound_pb2.Empty(name='', location=request)
            else:
                return feature


        class DictSenderServicer(starbound_pb2_grpc.DictSenderServicer):

            modPath = '/home/steam/starbound/mods'

            def find_all_hash(self):
                mod_list_raw = {}
                for filename in os.listdir(self.modPath):
                    if os.path.isdir(self.modPath + '/' + filename):
                        mod_list_raw[filename] = \
                            self.get_folder_hash(filename)
                    else:
                        mod_list_raw[filename] = \
                            self.get_file_hash(filename)
                print (mod_list_raw)

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
                server = \
                    grpc.server(futures.ThreadPoolExecutor(max_workers=10))
                starbound_pb2_grpc.add_DictSenderServicer_to_server(DictSenderServicer(),
                        server)
                server.add_insecure_port('[::]:50051')
                server.start()


        servicer = DictSenderServicer()
        servicer.find_all_hash()
        servicer.serve()
except KeyboardInterrupt:

    pass
