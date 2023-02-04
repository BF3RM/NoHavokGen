import json
import os

# SubWorldData
path = os.path.join(os.getcwd(), 'templates', 'SubWorldData.json')

if os.path.exists(path) is False:
    print('Error: Missing template')

with open(path, 'r') as f:
	subWorldDataTemp = json.loads(f.read())

# ObjectBlueprint
path = os.path.join(os.getcwd(), 'templates', 'ObjectBlueprint.json')

if os.path.exists(path) is False:
    print('Error: Missing template')

with open(path, 'r') as f:
    objectBlueprintTemp = json.loads(f.read())

# ReferenceObjectData
path = os.path.join(os.getcwd(), 'templates', 'ReferenceObjectData.json')

if os.path.exists(path) is False:
    print('Error: Missing template')

with open(path, 'r') as f:
    referenceObjectDataTemp = json.loads(f.read())

# WorldPartData
path = os.path.join(os.getcwd(), 'templates', 'WorldPartData.json')

if os.path.exists(path) is False:
    print('Error: Missing template')

with open(path, 'r') as f:
    worldPartDataTemp = json.loads(f.read())

# WorldPartReferenceObjectData
path = os.path.join(os.getcwd(), 'templates', 'WorldPartReferenceObjectData.json')

if os.path.exists(path) is False:
    print('Error: Missing template')

with open(path, 'r') as f:
    worldPartReferenceObjectDataTemp = json.loads(f.read())
