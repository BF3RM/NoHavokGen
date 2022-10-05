import json
import os
import argparse
import subprocess

WIN32_PREFIX = 'Win32'
BUNDLE_PREFIX = 'NoHavok/Levels'
FROSTBITE_VER = 'Frostbite2_0'
EBX_JSON_FOLDER = 'ebx_json/Levels'
SB_OUTPUT_FOLDER = 'sb'

def main(rimePath):
	inputPath = os.path.join(os.getcwd(), EBX_JSON_FOLDER)
	outputPath = os.path.join(os.getcwd(), SB_OUTPUT_FOLDER)
	
	if not os.path.exists(outputPath):
		os.makedirs(outputPath)
	commands = []

	for mapName in os.listdir(inputPath):
		#build superbundle 
		sbName = WIN32_PREFIX + '/' + BUNDLE_PREFIX + '/' + mapName + '/' + mapName
		commands.append('build_sb ' + sbName + ' ' + FROSTBITE_VER + ' \"' + outputPath + '\"\n')

		for file in os.listdir(os.path.join(inputPath, mapName)):
			fileName = os.path.splitext(file)[0] # Remove extension
			filePath = os.path.join(inputPath, mapName, file)

			if not os.path.isfile(filePath):
				continue

			# build bundle
			bundleNameW32 = WIN32_PREFIX + '/' + BUNDLE_PREFIX + '/' + mapName + '/' + fileName
			commands.append('build_bundle ' + bundleNameW32 + '\n')

			partitionName = BUNDLE_PREFIX + '/' + mapName + '/' + fileName

			# add partition to bundle and build bundle
			commands.append('add_json_partition ' + partitionName.lower() + ' \"' + filePath + '\"\n')
			commands.append('build\n')
		
		#build superbundle
		commands.append('build\n\n')
		print('Built superbundle: ' + sbName)

	#save commands in commands.txt
	with open(os.path.join(os.getcwd(), 'commands.txt'), "w") as f:
		f.writelines(commands)
	f.close()

	# execute commands with rime
	subprocess.run([rimePath, 'commands.txt'])


if __name__ == "__main__":
	try:
		# set it up
		parser = argparse.ArgumentParser(description = '[--rimepath] RimeREPL.exe path')
		parser.add_argument("--rimepath", type = str, default = 'RimeREPL', help = "Path to RimeREPL.exe. By default it uses rimeREPL as window\'s environment var")

		# get it
		args = parser.parse_args()
		rimePath = args.rimepath
		# print('Parsed arguments')

		main(rimePath)
	except KeyboardInterrupt:
		print('User has exited the program')
