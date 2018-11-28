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
# The folder where the mod files are located - aka starbound server mod folder - It's and FTP PATH
mod_path_ftp = "/starbound_server/mods/"
# The port used by grpc to connect client and server - make sure to open it on your firewall
grpc_port = '[::]:50051'
# The user used to connect to the ftp
ftp_user = "starb-ftp"
# The password used to connect to the ftp
ftp_pass = "Blackstones32"
# The folder where the zips files will be stored - make sure the permissions are correctly set - It's and FTP PATH
zip_repo = '/starbound/zips/'
# The folder where the caracters will be backuped on the server - It's and FTP PATH
backup_folder = '/starbound/backups/'

# END OF CONFIG-PART ! -------------------------------------------------------------------------------------------------

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def build_conf_dict():
    conf_dict = {
            "ftp_user": ftp_user,
            "ftp_pass": ftp_pass,
            "zip_repo": zip_repo,
            "backup_folder": backup_folder,
            "mod_path_ftp": mod_path_ftp
    }
    return conf_dict


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
        builded_server_dict = build_server_dict()
        print(builded_server_dict)
        return starbound_pb2.MyDict(dictionary=builded_server_dict)


class GetConfigServicer(starbound_pb2_grpc.GetConfigServicer):

    def send_config(self, request, context):
        builded_conf_dict = build_conf_dict()
        print(builded_conf_dict)
        return starbound_pb2.MyConfig(dictionary=builded_conf_dict)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    starbound_pb2_grpc.add_DictSenderServicer_to_server(DictSenderServicer(), server)
    starbound_pb2_grpc.add_GetConfigServicer_to_server(GetConfigServicer(), server)
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
