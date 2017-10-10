from pathlib import Path
from os import path
import checksumdir
import os
import hashlib
import json

modPath = "/home/steam/starbound/mods"

def find_all_hash ():
	mod_list_raw = {}
	for filename in os.listdir(modPath):
		if os.path.isdir(modPath + "/" + filename):
			mod_list_raw[filename] = get_folder_hash(filename)
		else:
			mod_list_raw[filename] = get_file_hash(filename)
	print (mod_list_raw)

def get_folder_hash (filename):
	hash = checksumdir.dirhash(modPath + "/" + filename)
	return hash

def get_file_hash (filename):
	openedFile = open(modPath + "/" + filename, 'rb')
	readFile = openedFile.read()
	md5Hash = hashlib.md5(readFile)
	md5Hashed = md5Hash.hexdigest()
	return md5Hashed

def export_hash_json():
	mod_list_raw = find_all_hash()
	d = {"mods":[{'name':name,"hash":hashvalue} for name,hashvalue in mod_list_raw.items()]}
	with open('mods.json', 'w') as fp:
		json.dump(d, fp, indent=4)

#export_hash_json()
find_all_hash()
print ("Value : %s" %  dict.items())
