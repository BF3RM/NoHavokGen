import os
import subprocess

WIN32_PREFIX = 'Win32'
BUNDLE_PREFIX = 'NoHavok'
FROSTBITE_VER = 'Frostbite2_0'
INTERMEDIATE_FOLDER = 'intermediate'
EBX_JSON_FOLDER = 'ebx_json'
SB_OUTPUT_FOLDER = 'sb'

def generate_bundles(rime_path: str, out_dir: str):
	input_path = os.path.join(
		os.getcwd(), INTERMEDIATE_FOLDER, EBX_JSON_FOLDER)
	output_path = os.path.join(out_dir, SB_OUTPUT_FOLDER)
	
	if not os.path.exists(output_path):
		os.makedirs(output_path)
	commands = []

	super_bundle_names = []
	commands_path = os.path.join(os.getcwd(), INTERMEDIATE_FOLDER, 'commands.txt')

	for map_name in os.listdir(input_path):
		#build superbundle 
		sb_name = WIN32_PREFIX + '/' + BUNDLE_PREFIX + '/' + map_name + '/' + map_name
		commands.append('build_sb ' + sb_name + ' ' + FROSTBITE_VER + ' \"' + output_path + '\"\n')

		for file in os.listdir(os.path.join(input_path, map_name)):
			file_name = os.path.splitext(file)[0] # Remove extension
			file_path = os.path.join(input_path, map_name, file)

			if not os.path.isfile(file_path):
				continue

			# build bundle
			bundle_name_w32 = WIN32_PREFIX + '/' + BUNDLE_PREFIX + '/' + map_name + '/' + file_name
			commands.append('build_bundle ' + bundle_name_w32 + '\n')

			partition_name = BUNDLE_PREFIX + '/' + map_name + '/' + file_name

			# add partition to bundle and build bundle
			commands.append('add_json_partition ' + partition_name.lower() + ' \"' + file_path + '\"\n')
			commands.append('build\n')
		
		#build superbundle
		commands.append('build\n\n')
		super_bundle_names.append(sb_name)
		print('Built superbundle: ' + sb_name)

	#save commands in commands.txt
	with open(commands_path, "w") as f:
		f.writelines(commands)

	# execute commands with rime
	subprocess.run([os.path.join(rime_path, 'RimeREPL.exe'), commands_path], cwd=rime_path)

	return super_bundle_names
