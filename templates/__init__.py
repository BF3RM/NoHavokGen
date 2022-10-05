import json
import os

path = os.path.join(os.getcwd(), 'templates', 'SubWorldData.json')

if os.path.exists(path) is False:
    print('FUCK')

with open(path, 'r') as f:
	subWorldDataTemp = json.loads(f.read())

path = os.path.join(os.getcwd(), 'templates', 'ObjectBlueprint.json')

if os.path.exists(path) is False:
    print('FUCK')

with open(path, 'r') as f:
    objectBlueprintTemp = json.loads(f.read())

path = os.path.join(os.getcwd(), 'templates', 'ReferenceObjectData.json')

if os.path.exists(path) is False:
    print('FUCK')

with open(path, 'r') as f:
    referenceObjectDataTemp = json.loads(f.read())
