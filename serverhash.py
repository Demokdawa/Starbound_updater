#!/usr/bin/python
# -*- coding: utf-8 -*-
from pathlib import Path
from os import path
from concurrent import futures
from threading import Thread
from queue import Queue
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
thread_count = 10
modPath = '/home/starb-ftp/starbound/mods'

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
            hashcompute = HashCompute(queue)
            hashcompute.daemon = True
            hashcompute.start()

class HashCompute(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            modPath, filename = self.queue.get()
            if os.path.isdir(modPath + '/' + filename):
                MyDict[filename] = checksumdir.dirhash(modPath + '/' + filename)
            else:
                openedFile = open(modPath + '/' + filename, 'rb')
                readFile = openedFile.read()
                md5Hash = hashlib.md5(readFile)
                MyDict[filename] = md5Hash.hexdigest()
            self.queue.task_done()

def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        starbound_pb2_grpc.add_DictSenderServicer_to_server(DictSenderServicer(),
                server)
        server.add_insecure_port('[::]:50051')
        server.start()
        print ("Server started !")
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)

if __name__ == '__main__':
    serve()
