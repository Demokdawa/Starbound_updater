import os
from os import path

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=254): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename
	
#download_file('https://zenmap.xyz/mods/food_stack.pak')

var = os.path.splitext("C:\\Users\\PRAN152\\Documents\\GitHub\\Starbound_updater\\serverhash.py")
print (var)
