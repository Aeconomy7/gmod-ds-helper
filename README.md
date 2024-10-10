# Garry's Mod Dedicated Server Helper (GMDSH)
This is a tool I created to help managing addons for my Garry's Mod Server. It probably isn't a glove that fits all but if you store your addon files locally like I do this may be helpful, who knows.

NOTE: My Garry's Mod server is on some ancient ubuntu server (16.04 lol) and thus it only support up to Python 3.5. Thus the code is way uglier than it would be with the most recent Python versions.

## Installation and Setup
  1. Populate the `config.py` file
```python
STEAM_ROOT = "/home/USERNAME/.steam"       # Location of Steam root
GMOD_SERVER_ROOT = "/home/USERNAME/CLEAN"  # Location of Garry's Mod Server root (where you installed the server with steamcmd)

# Set the Steam Workshop collection IDs, these are mine, yours will be different (unless you want to host the same TTT server as me :P)
WORKSHOP_COLLECTION_IDS = [ "3257054311", "3223842790", "3224631129", "3223671871" ]

# Set the base URL for the Steam Workshop API (probably don't change these ever, will move these away from here at some point)
STEAM_WORKSHOP_API_GET_COLLECTION_DETAILS_URL = "https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/"
STEAM_WORKSHOP_API_GET_DETAILS_URL = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
```

  2. Create Python venv and install requirements
```bash
python3 -m venv venv
python3 -m pip install -r requirements.txt
```

  3. Run the thing
```bash
python3 gmdsh.py [-h] [-u] [-d] [-e] [-c]
```
