from . import HavokNames
from . import HavokTransforms
from . import PhysicsContent
import os
import json

with open(os.path.join(os.getcwd(), 'util', 'PartitionMap.json'), 'r') as f:
	PartitionMap = json.loads(f.read())

with open(os.path.join(os.getcwd(), 'util', 'VariationMap.json'), 'r') as f:
	VariationMap = json.loads(f.read())