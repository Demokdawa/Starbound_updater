## Starbound_updater

Welcome to the Starbound_updater project page ! The goal of the project is to make mods distribution for Starbounds clients easier for bother Server Owners and their Users ! 

The release package include :

- One client executable that is semi-automatic (You just enter the ip address of the server, and it do the job).
- One Starbound_updater_server.py script that will be executed server-side to handle client requests and manage updates.

The lines you need to configure are in the "CONFIG-PART" of Starbound_updater_server.py ! 

### R͟͟͟e͟͟͟q͟͟͟u͟͟͟i͟͟͟r͟͟͟e͟͟͟m͟͟͟e͟͟͟n͟͟͟t͟͟͟s͟͟͟ ͟t͟o͟ ͟r͟u͟n͟ ͟s͟e͟r͟v͟e͟r͟

- GRPC (python -m pip install grpcio)
- Checksumdir (pip install checksumdir)
- Python 3.5+
- An FTP server to send mods to client


Keep in mind the fact that i'm just a beginner in python, so the code may be dirty for you if you read it, or the implementation may not be perfect. But it's just the first project i get in a stable state, and i done it to learn python and because i love starbound. It was designed for my personnal use, but since it's in a relatively stable state, why not share it with the community, eh ?
