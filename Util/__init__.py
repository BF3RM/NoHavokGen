from . import HavokNames
from . import HavokTransforms
from . import PhysicsContent
import os
import json

with open(os.path.join(os.getcwd(), 'Util', 'PartitionMap.json'), 'r') as f:
	PartitionMap = json.loads(f.read())
f.close()

with open(os.path.join(os.getcwd(), 'Util', 'VariationMap.json'), 'r') as f:
	VariationMap = json.loads(f.read())
f.close()