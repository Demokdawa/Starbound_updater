#!/usr/bin/python
# -*- coding: utf-8 -*-
from concurrent import futures
from threading import Thread
from queue import Queue
import time
import checksumdir
import os
import hashlib
import grpc
import starbound_pb2
import starbound_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
thread_count = 10
modPath = '/home/starb-ftp/starbound_server/mods'

queue = Queue()
MyDict = {}


class DictSenderServicer(starbound_pb2_grpc.DictSenderServicer):

    def send_dict(self, request, context):
        random_dict = self.build_server_dict()
        return starbound_pb2.MyDict(dictionary=random_dict)

    def build_server_dict(self):
        for filename in os.listdir(modPath):
            queue.put((modPath, filename))
        self.thread_creator(queue, thread_count)
        queue.join()
        return MyDict

    def thread_creator(self, queue, thread_count):
        for i in range(thread_count):
            hash_compute = HashCompute(queue)
            hash_compute.daemon = True
            hash_compute.start()


class HashCompute(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            mod_path, filename = self.queue.get()
            if os.path.isdir(mod_path + '/' + filename):
                MyDict[filename] = checksumdir.dirhash(mod_path + '/' + filename)
            else:
                opened_file = open(mod_path + '/' + filename, 'rb')
                read_file = opened_file.read()
                md5_hash = hashlib.md5(read_file)
                MyDict[filename] = md5_hash.hexdigest()
            self.queue.task_done()


def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        starbound_pb2_grpc.add_DictSenderServicer_to_server(DictSenderServicer(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        print("Server started !")
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)


if __name__ == '__main__':
    serve()
