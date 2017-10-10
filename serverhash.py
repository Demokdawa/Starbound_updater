from pathlib import Path
from os import path
import checksumdir
import os
import hashlib
import json

class RouteGuideServicer(starbound_pb2_grpc.RouteGuideServicer):

modPath = "/home/steam/starbound/mods"

def find_all_hash ():
	mod_list_raw = {}
	for filename in os.listdir(modPath):
		if os.path.isdir(modPath + "/" + filename):
			mod_list_raw[filename] = get_folder_hash(filename)
		else:
			mod_list_raw[filename] = get_file_hash(filename)
	print (mod_list_raw)
	#print ("Value : %s" %  mod_list_raw.items())

def get_folder_hash (filename):
	hash = checksumdir.dirhash(modPath + "/" + filename)
	return hash

def get_file_hash (filename):
	openedFile = open(modPath + "/" + filename, 'rb')
	readFile = openedFile.read()
	md5Hash = hashlib.md5(readFile)
	md5Hashed = md5Hash.hexdigest()
	return md5Hashed

def GetFeature(self, request, context):
  feature = get_feature(self.db, request)
  if feature is None:
    return route_guide_pb2.Feature(name="", location=request)
  else:
    return feature

def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  route_guide_pb2_grpc.add_RouteGuideServicer_to_server(
      RouteGuideServicer(), server)
  server.add_insecure_port('[::]:50051')
  server.start()

#export_hash_json()
find_all_hash()
