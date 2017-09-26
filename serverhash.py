from pathlib import Path
from os import path
import checksumdir
import os
import hashlib
import json

modPath = "/home/steam/starbound/mods"

def find_all_hash ():
	mod_list = {}
	for filename in os.listdir(modPath):
		if os.path.isdir(modPath + "/" + filename):
			mod_list[filename] = get_folder_hash(filename)
			#write_json()
		else:
			mod_list[filename] = get_file_hash(filename)
			#write_json()
	with open('result.json', 'w') as fp:
		json.dump(mod_list, fp, indent=4, sort_keys=True)

def get_folder_hash (filename):
	hash = checksumdir.dirhash(modPath + "/" + filename)
	return hash

def get_file_hash (filename):
	openedFile = open(modPath + "/" + filename, 'rb')
	readFile = openedFile.read()
	md5Hash = hashlib.md5(readFile)
	md5Hashed = md5Hash.hexdigest()
	return md5Hashed

find_all_hash()
