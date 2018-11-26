#!/usr/bin/python
# -*- coding: utf-8 -*-
from concurrent import futures
import time
import checksumdir
import os
import hashlib
import grpc
import starbound_pb2
import starbound_pb2_grpc

# CONFIG-PART | THAT IS THE ONLY LINES YOU HAVE TO MODIFY TO CONFIGURE THE ZIP CREATOR----------------------------------

# The folder where the mod files are located - aka starbound server mod folder
mod_path = '/home/starb-ftp/starbound_server/mods'
# The port used by grpc to connect client and server - make sure to open it on your firewall
grpc_port = '[::]:50051'

# END OF CONFIG-PART ! -------------------------------------------------------------------------------------------------

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def build_server_dict():
    ret_dict = {}
    for filename in os.listdir(mod_path):
        if os.path.isdir(mod_path + '/' + filename):
            folder_hash = checksumdir.dirhash(mod_path + '/' + filename)
            ret_dict[filename] = folder_hash
        else:
            opened_file = open(mod_path + '/' + filename, 'rb')
            read_file = opened_file.read()
            md5_hash = hashlib.md5(read_file)
            file_hash = md5_hash.hexdigest()
            ret_dict[filename] = file_hash
    return ret_dict


class DictSenderServicer(starbound_pb2_grpc.DictSenderServicer):

    def send_dict(self, request, context):
        random_dict = build_server_dict()
        print(random_dict)
        return starbound_pb2.MyDict(dictionary=random_dict)

    def send_config(self, request, context):
        random_dict = build_server_dict()
        print(random_dict)
        return starbound_pb2.MyConfig(dictionary=random_dict)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    starbound_pb2_grpc.add_DictSenderServicer_to_server(DictSenderServicer(), server)
    starbound_pb2_grpc.add_GetConfigServicer_to_server(DictSenderServicer(), server)
    server.add_insecure_port(grpc_port)
    server.start()
    print("Server started !")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
