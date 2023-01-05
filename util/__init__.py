from . import HavokNames
from . import HavokTransforms
import os
import json

with open(os.path.join(os.getcwd(), 'util', 'PartitionMap.json'), 'r') as f:
	PartitionMap = json.loads(f.read())

with open(os.path.join(os.getcwd(), 'util', 'VariationMap.json'), 'r') as f:
	VariationMap = json.loads(f.read())

with open(os.path.join(os.getcwd(), 'util', 'PhysicsContents.json'), 'r') as f:
	PhysicsContents = json.loads(f.read())