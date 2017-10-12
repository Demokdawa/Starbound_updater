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

channel = grpc.insecure_channel('localhost:50051')
stub = starbound_pb2_grpc.DictSenderStub(channel)
response = stub.send_dict(starbound_pb2.Empty())
dict_from_server = dict(response.dictionary)
print(dict_from_server)

#A_dict = {'hash1' : "jsonobj1","hash2" : "jsonobj2"}
#B_dict = {'hash3' : "jsonobj3","hash2" : "jsonobj2"}
#setA = set(A_dict.keys())
#setB = set(B_dict.keys())

#print(setA - setB)
#print(setB - setA)

#are only on a:
#items_only_in_a = list(setA)
#for x in items_only_in_a:
#    del A_dict[x]

#items_only_in_b = list(setB)
#for x in items_only_in_b:
#    download(B_dict[x])
