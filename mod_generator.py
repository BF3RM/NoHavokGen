import json
import os
import shutil

MOD_JSON_FILE = "mod.json"

def copy_mod_files(out_dir: str):
	mod_source_path = os.path.join(os.path.dirname(__file__), 'NoHavok')

	print("Copying mod files to " + out_dir)
	shutil.copytree(mod_source_path, out_dir, dirs_exist_ok=True)


def generate_mod_json(version: str, superbundles: dict, out_dir: str):
	mod_json = {
		"Name": 'NoHavok',
		"Authors": ["RealityMod Dev Team"],
		"Description": "This mod replaces all static model groups (StaticModelGroupEntityData) with individual entities for easier manipulation.",
		"URL": "https://github.com/BF3RM/NoHavokBundleGen",
		"Version": version,
		"HasWebUI": False,
		"HasVeniceEXT": True,
		"Dependencies": {
			"veniceext": "^1.1.0"
		},
		"Superbundles": superbundles
	}

	print("Generating mod.json")

	with open(os.path.join(out_dir, MOD_JSON_FILE), "w") as mod_json_file:
		json.dump(mod_json, mod_json_file, indent=2)


def generate_mod(version: str, superbundles: dict, out_dir: str):
	copy_mod_files(out_dir)
	generate_mod_json(version, superbundles, out_dir)
