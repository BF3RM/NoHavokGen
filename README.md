# NoHavokGen
This generates the mod `NoHavok`, which replaces all havok objects with regular, editable objects, so they can be interacted with in [MapEditor](https://github.com/BF3RM/MapEditor).

## Usage
There are two options to install the mod

1. Get Venice Unleashed Mod Manager or [VUMM](https://github.com/BF3RM/vumm-cli) and run `vumm install nohavok`.
2. Get the latest release in the [releases section](https://github.com/BF3RM/NoHavokGen/releases/latest), unzip and place the mod folder on your `.../Server/Admin/Mods` folder, and add `NoHavok` to your modlist file (`.../Server/Admin/ModList.txt`) alongside `MapEditor`. 

To load a `MapEditor` save you need to also run this mod along with the generated level mod (more info in [LevelLoaderGen](https://github.com/BF3RM/LevelLoaderGen) repository).

## Generating NoHavok (developers only)
Generating the mod is fairly simple, just run:

`python generate.py <mod_version>`

This will generate a mod in mods/NoHavok, you can copy this to your `Server/Admin/Mods` folder to run it.

You can also directly make it generate the mod in your mods folder by adding the `-o` flag:

`python generate.py -o "<path_to_documents_bf3>/Server/Admin/Mods" <mod_version>`
