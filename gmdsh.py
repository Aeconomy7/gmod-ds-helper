import os
import requests
#import pdb
import subprocess
import argparse
from datetime import datetime
from config import *

# Last update epoch timestamp - stored in file
LAST_UPDATED_TIMESTAMP = 0

# Addons root - where to store the generated files
OUT_FOLDER = os.path.dirname(os.path.realpath(__file__)) + "/"

# Set the base URL for the Steam Workshop API
STEAM_WORKSHOP_API_GET_COLLECTION_DETAILS_URL = "https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/"
STEAM_WORKSHOP_API_GET_DETAILS_URL = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"

#####################
# UTILITY FUNCTIONS #
#####################

def display_banner():
	"""
	Tools need banners.
	"""

	global COLLECTION_IDS
	global STEAM_ROOT
	global GMOD_SERVER_ROOT

	header = '''
/--------------------------------------------------------\\
|   _______ .___  ___.  _______       _______. __    __  |
|  /  _____||   \/   | |       \     /       ||  |  |  | |
| |  |  __  |  \  /  | |  .--.  |   |   (----`|  |__|  | |
| |  | |_ | |  |\/|  | |  |  |  |    \   \    |   __   | |
| |  |__| | |  |  |  | |  '--'  |.----)   |   |  |  |  | |
|  \______| |__|  |__| |_______/ |_______/    |__|  |__| |
|                                                        |
|			 Auther: sc00by			 |
\--------------------------------------------------------/
'''

	print(header)
	print("	Steam Root:     " + STEAM_ROOT)
	print("	Server Root:    " + GMOD_SERVER_ROOT)
	print("	Script Folder:  " + OUT_FOLDER)
	print("	Collection IDs: " + str(WORKSHOP_COLLECTION_IDS) + "\n")


########################
# COLLECTION FUNCTIONS #
########################

def get_collection_title_from_collection_id(workshop_collection_id):
	"""
	Fetches the workshop collection title from specified collection, cuz why not.
	"""
	global STEAM_WORKSHOP_API_GET_DETAILS_URL

	try:
		print("Fetching collection title by id: "  + workshop_collection_id)
		response = requests.post(STEAM_WORKSHOP_API_GET_DETAILS_URL, data={"itemcount": 1, "publishedfileids[0]": workshop_collection_id})
		response.raise_for_status()
		data = response.json()

		if "response" not in data or "publishedfiledetails" not in data["response"] or not data["response"]["publishedfiledetails"]:
			print("Error: No collection title found.")
			return "N/A"

		# Extract the relevant information from the API response
		publishedfiledetails = data["response"]["publishedfiledetails"][0]
		if "title" not in publishedfiledetails:
			print("Error: 'title' not found for workshop ID " + workshop_id)
			title = ""
		else:
			title = publishedfiledetails["title"]

	except requests.exceptions.RequestException as e:
		print("Error " + e)

	return title

def get_workshop_ids_from_collection_id(workshop_collection_id):
	"""
	Fetches the workshop IDs from the specified collection.
	"""
	global STEAM_WORKSHOP_API_GET_COLLECTION_DETAILS_URL

	try:
		print("Fetching collection id: " + workshop_collection_id)
		response = requests.post(STEAM_WORKSHOP_API_GET_COLLECTION_DETAILS_URL, data={"collectioncount": 1, "publishedfileids[0]": workshop_collection_id})
		response.raise_for_status()
		data = response.json()

		if "response" not in data or "collectiondetails" not in data["response"] or not data["response"]["collectiondetails"]:
			print("Error: No collection details found.")
			return []

		workshop_ids = [str(item["publishedfileid"]) for item in data["response"]["collectiondetails"][0]["children"]]
		return workshop_ids
	except requests.exceptions.RequestException as e:
		print("Error " + e)
		return []

def generate_lua_file(workshop_ids, collection_id):
	"""
	Generates the Lua file with the commented workshop IDs.
	"""

	global STEAM_WORKSHOP_API_GET_DETAILS_URL

	collection_title = get_collection_title_from_collection_id(collection_id)

	lua_content = ""
	lua_content = "-- " + collection_title + "\n"

	for workshop_id in workshop_ids:
		try:
			# Fetch the workshop item details
			response = requests.post(STEAM_WORKSHOP_API_GET_DETAILS_URL, data={"itemcount": 1, "publishedfileids[0]": workshop_id})
			response.raise_for_status()
			data = response.json()

			if "response" not in data or "publishedfiledetails" not in data["response"] or not data["response"]["publishedfiledetails"]:
				print("Error: No details found for workshop ID " + workshop)
				continue

			# Extract the relevant information from the API response
			publishedfiledetails = data["response"]["publishedfiledetails"][0]
			if "title" not in publishedfiledetails:
				print("Error: 'title' not found for workshop ID " + workshop_id)
				title = ""
			else:
				title = publishedfiledetails["title"]

			# Extract date addon was last updated
			if "time_updated" not in publishedfiledetails:
				print("Error: 'time_updated' not found for workshop ID " + workshop_id)
				last_updated = ""
			else:
				epoch = publishedfiledetails["time_updated"]
				last_updated = datetime.fromtimestamp(epoch).strftime("%m/%d/%Y %I:%M %p")
				# If the addon has been updated since last round of updating, add it to list to update
				if epoch > LAST_UPDATED_TIMESTAMP:
					print("Addon " + workshop_id + " (" + title + ") outdated...")
					with open(OUT_FOLDER + "addons_to_update", "a") as file:
						file.write(workshop_id + "\n")

			lua_content += "resource.AddWorkshop(\"" + workshop_id + "\") -- " + title + " -- Last Updated: " + last_updated + "\n"
		except requests.exceptions.RequestException as e:
			print("Error: " + e)

	# Write the Lua file
	with open(OUT_FOLDER + "workshop.lua", "a") as file:
		file.write(lua_content)

	print("Lua file generated: " + OUT_FOLDER + "workshop.lua")


#####################
# EXTRACT FUNCTIONS #
#####################

# Function to extract bin file using 7-zip and rename it as .gma
def extract_bin_file_with_7zip(bin_file_path, destination_dir):
	try:
		# 7-zip command to extract the bin file
		seven_zip_path = r"/usr/bin/7z"  # Adjust this path based on your 7-Zip installation
		extract_cmd = [seven_zip_path, 'x', bin_file_path, "-o" + destination_dir, '-y']

		# Run the 7-zip extraction command
		subprocess.run(extract_cmd, check=True)
		print("Successfully extracted " + bin_file_path + " to " + destination_dir)

		# Look for the extracted file (assuming it's the only one in the destination folder)
		extracted_files = [f for f in os.listdir(destination_dir) if os.path.isfile(os.path.join(destination_dir, f))]
		if not extracted_files:
			raise FileNotFoundError("No file was extracted from " + bin_file_path)

		extracted_file = extracted_files[0]
		extracted_file_path = os.path.join(destination_dir, extracted_file)

		# Rename the extracted file to have a .gma extension
		gma_file_path = extracted_file_path + ".gma"
		os.rename(extracted_file_path, gma_file_path)
		print("Renamed " + extracted_file_path + " to " + gma_file_path)

		return gma_file_path

	except Exception as e:
		print("Error extracting or renaming " + bin_file_path + ": " + e)
		return None


# Function to run the external command for each ID
def run_gmad_command(search_dir, steam_dir, id, out_dir):
	global STEAM_ROOT

	#gmad_exe = os.path.join(steam_dir, "GarrysMod", "bin", "gmad.exe")
	gmad_exe = "/home/steam/bin/gmad_linux"
	gma_dir = os.path.join(search_dir, str(id)) + '/'

	# Use glob to search for any .gma file in the directory
	gma_files = glob.glob(os.path.join(gma_dir, "*.gma"))

	if gma_files:
		# If there's at least one .gma file, use the first one found
		gma_file = gma_files[0]
		command = [gmad_exe, "extract", "-file", gma_file, "-out", out_dir, "-quiet"]
		#print(f"Running command: {command}")
		subprocess.run(command)  # Run the command
	else:
		print("No .gma file found for ID " + id + " in directory " + gma_dir + ". Will check for .bin file...")
		# Use glob to search for any .gma file in the directory
		bin_files = glob.glob(os.path.join(gma_dir, "*.bin"))

		if bin_files:
			seven_zip_path = r"/usr/bin/7z"
			# if there's at least one .bin file, use first found
			bin_file = bin_files[0]
			command = [seven_zip_path, 'e', bin_file, "-o" + gma_dir, "-y"]
			subprocess.run(command)

			extracted_file = bin_file.replace(".bin", "")
			gma_file = extracted_file + ".gma"

			# rename the extracted file
			os.rename(extracted_file, gma_file)

			# run the gmad extraction now
			command = [gmad_exe, "extract", "-file", gma_file, "-out", out_dir, "-quiet"]
			subprocess.run(command)

			# Cleanup the new GMA file
			print("Removing generated .gma file " + gma_file)
			os.remove(gma_file)
		else:
			print("No .bin file found, CHECK ADDON " + id)



########
# MAIN #
########

if __name__ == "__main__":
	global GMOD_SERVER_ROOT

	num_outdated_addons = 0

	# Define script args
	parser = argparse.ArgumentParser(description=display_banner())

	parser.add_argument('-u', '--update', action='store_true', default=False, help='Update workshop.lua, if not present, a file named addons_to_check with addon ids must be present in ' + OUT_FOLDER)
	parser.add_argument('-d', '--download', action='store_true', default=False, help='Download addons to update, if you want to download all addons, set last_updated file to 0')
	parser.add_argument('-e', '--extract', action='store_true', default=False, help='Extract downloaded addons files, the will be saved to ' + OUT_FOLDER + 'addons')
	parser.add_argument('-c', '--copy', action='store_true', default=False, help='Copy extracted addons to server dir, copied from ' + OUT_FOLDER + 'addons -> ' + GMOD_SERVER_ROOT + '/garrysmod')

	args = parser.parse_args()

	if not (args.update or args.download or args.extract or args.copy):
		parser.print_help()
		quit()

	# display banner :P
	display_banner()

	### Perform update of workshop.lua
	if args.update:
		# Fetch last_updated epoch timestamp from file
		with open(OUT_FOLDER + "last_updated", 'r') as file:
			LAST_UPDATED_TIMESTAMP = int(file.readline().strip())

		# Delete previous workshop.lua tmp file
		if os.path.exists(OUT_FOLDER + "workshop.lua"):
			os.remove(OUT_FOLDER + "workshop.lua")
			print("Found and Deleted existing workshop.lua file!")

		# Delete previous addons_to_update tmp file
		if os.path.exists(OUT_FOLDER + "addons_to_update"):
			os.remove(OUT_FOLDER + "addons_to_update")
			print("Found and Deleted existing addons_to_update file!")

		# Perform logic
		for id in WORKSHOP_COLLECTION_IDS:
			workshop_data = get_workshop_ids_from_collection_id(id)
			generate_lua_file(workshop_data,id)


		# Copy file to addon staging
		print("Copying file...")
		os.system("cp " + OUT_FOLDER + "workshop.lua " + GMOD_SERVER_ROOT + "/garrysmod/lua/autorun/server/workshop.lua")
		print("File copied successfully!")


	### Download and update outdated addons
	if args.download:
		with open(OUT_FOLDER + "addons_to_update", 'r') as file:
			num_outdated_addons = len([line for line in file if line.strip()])

		# Check if there are no addons to update
		if num_outdated_addons == 0:
			print("No addons were outdated! :)")
		else:
			print("Downloading addons...")

			# Perform addon downloads
			with open(OUT_FOLDER + "addons_to_update", 'r') as file:
				for addon in file:
					print("Downloading addon: " + addon.strip())
					subprocess.run(["/usr/games/steamcmd",
						"+login", "anonymous",
						"+workshop_download_item", "4000", addon.strip(),
						"+quit"])

	### Extract the files
	if args.extract:
		print("Extracting addon files...")

	### Copy the addon files to server
	if args.copy:
		print("Copying files to server....")
