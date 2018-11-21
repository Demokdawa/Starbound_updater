#!/usr/bin/python
# -*- coding: utf-8 -*-
from multiprocessing import Pool
import checksumdir
import os
import hashlib

# CONFIG-PART | THAT IS THE ONLY LINES YOU HAVE TO MODIFY TO CONFIGURE THE ZIP CREATOR----------------------------------

# The folder where the mod files are located - aka starbound server mod folder
mod_path = '/home/starb-ftp/starbound_server/mods'
# The port used by grpc to connect client and server - make sure to open it on your firewall
grpc_port = '[::]:50051'

# END OF CONFIG-PART ! -------------------------------------------------------------------------------------------------

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def build_server_dict():
    ret_dict = {}

    def __error_map(n):
        lol = n
        print(lol)
        print("does not work")

    def __add_to_dict(hash_tuple):
        f, h = hash_tuple
        ret_dict[f] = h
        print("Dictionnaire rempli")
    with Pool(processes=4) as pool:
        # Maybe don't let it as a one-liner, especially if you don't understand it fully
        print(pool.map_async(hash_compute, os.listdir(mod_path), callback=__add_to_dict, error_callback=__error_map))
    print(ret_dict)


def hash_compute(filename):
        if os.path.isdir(mod_path + '/' + filename):
            folder_hash = checksumdir.dirhash(mod_path + '/' + filename)
            hash_tuple = (filename, folder_hash)
            print(hash_tuple)
            return hash_tuple
        else:
            opened_file = open(mod_path + '/' + filename, 'rb')
            read_file = opened_file.read()
            md5_hash = hashlib.md5(read_file)
            file_hash = md5_hash.hexdigest()
            hash_tuple = (filename, file_hash)
            print(hash_tuple)
            return hash_tuple


if __name__ == '__main__':
    build_server_dict()
