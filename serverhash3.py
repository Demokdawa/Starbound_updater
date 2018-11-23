#!/usr/bin/python
# -*- coding: utf-8 -*-
from concurrent import futures
from multiprocessing import Pool
from logging.handlers import RotatingFileHandler
import time
import checksumdir
import os
import hashlib
import grpc
import starbound_pb2
import starbound_pb2_grpc
import logging

# CONFIG-PART | THAT IS THE ONLY LINES YOU HAVE TO MODIFY TO CONFIGURE THE ZIP CREATOR----------------------------------

# The folder where the mod files are located - aka starbound server mod folder
mod_path = '/home/starb-ftp/starbound_server/mods'
# The port used by grpc to connect client and server - make sure to open it on your firewall
grpc_port = '[::]:50051'

# END OF CONFIG-PART ! -------------------------------------------------------------------------------------------------

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class DictSenderServicer(starbound_pb2_grpc.DictSenderServicer):

    def build_server_dict(self):

        ret_dict = {}

        def __error_callback(n):
            print(n)
            print("does not work")

        def __add_to_dict(hash_tuple):
            f, h = hash_tuple
            ret_dict[f] = h
            print("Dictionnaire changed")

        pool = Pool(processes=20)
        for filename in os.listdir(mod_path):
            pool.apply_async(self.hash_compute, (filename, ), callback=__add_to_dict, error_callback=__error_callback)
        pool.close()
        pool.join()
        print(ret_dict)
        print("Dictionary sent")
        return ret_dict

    def hash_compute(self, filename):
            if os.path.isdir(mod_path + '/' + filename):
                folder_hash = checksumdir.dirhash(mod_path + '/' + filename)
                hash_tuple = (filename, folder_hash)
                logger.info(hash_tuple)
                return hash_tuple
            else:
                opened_file = open(mod_path + '/' + filename, 'rb')
                read_file = opened_file.read()
                md5_hash = hashlib.md5(read_file)
                file_hash = md5_hash.hexdigest()
                hash_tuple = (filename, file_hash)
                logger.info(hash_tuple)
                return hash_tuple

    def send_dict(self, request, context):
        test_dict = {}
        test_dict['a'] = '2023767489'
        random_dict = test_dict
        ret_dict = self.build_server_dict()
        logger.info(ret_dict)
        logger.info(random_dict)
        return starbound_pb2.MyDict(dictionary=random_dict)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    starbound_pb2_grpc.add_DictSenderServicer_to_server(DictSenderServicer(), server)
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
