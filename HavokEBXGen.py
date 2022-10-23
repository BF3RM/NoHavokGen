import uuid
import json
import os
import copy
import argparse
import Util

from templates import subWorldDataTemp, objectBlueprintTemp, referenceObjectDataTemp

EXPORT_FOLDER = 'ebx_json'

def QuaternionToRotation(Q):
	# Extract the values from Q
	q0 = Q[0]
	q1 = Q[1]
	q2 = Q[2]
	q3 = Q[3]
	 
	# First row of the rotation matrix
	r00 = 1 - 2 * (q1 * q1 + q2 * q2)
	r01 = 2 * (q0 * q1 + q2 * q3)
	r02 = 2 * (q0 * q2 - q1 * q3)
	 
	# Second row of the rotation matrix
	r10 = 2 * (q0 * q1 - q2 * q3)
	r11 = 1 - 2 * (q0 * q0 + q2 * q2)
	r12 = 2 * (q1 * q2 + q0 * q3)
	 
	# Third row of the rotation matrix
	r20 = 2 * (q0 * q2+ q1 * q3)
	r21 = 2 * (q1 * q2 - q0 * q3)
	r22 = 1 - 2 * (q0 * q0 + q1 * q1)
	 
	# 3x3 rotation matrix
	return [ [r00, r01, r02], [r10, r11, r12], [r20, r21, r22] ] 

def GetPartitionEBX(partitionGuid):
	ebxFilePath = Util.PartitionMap[partitionGuid]

	path = os.path.join(EBX_DUMP_PATH, ebxFilePath)

	if os.path.exists(path) is False:
		print('Could not find Venice EBX Json dump')
		# continue

	with open(path, 'r') as f:
		partitionEbx = json.loads(f.read())
	f.close()

	return partitionEbx

def GetValidScales(partition, instanceGuid):
	staticModelEntityData = partition['Instances'][instanceGuid]
	scales = {}

	if 'PhysicsData' in staticModelEntityData and staticModelEntityData['PhysicsData'] and 'InstanceGuid' in staticModelEntityData['PhysicsData'] and staticModelEntityData['PhysicsData']['InstanceGuid'] and staticModelEntityData['PhysicsData']['InstanceGuid'] in partition['Instances']:
		physicsData = partition['Instances'][staticModelEntityData['PhysicsData']['InstanceGuid']]

		for entry in physicsData['ScaledAssets']:
			havokAsset = partition['Instances'][entry['InstanceGuid']]
			name = havokAsset['Name']
			
			# check if actually exists (some collisions dont exist, probably due to optimizations)
			if name.lower() in Util.PhysicsContent.physicsContent:
				scales[str(havokAsset['Scale'])] = True

	return scales

def CreateInitialPartitionStruct(havokName):
	gen = copy.deepcopy(subWorldDataTemp)
	partitionGuid = str(uuid.uuid4())
	gen['PartitionGuid'] = partitionGuid

	subWorldDataGuid = str(uuid.uuid4())
	descriptorGuid = str(uuid.uuid4())
	registryGuid = str(uuid.uuid4())
	worldPartDataGuid = str(uuid.uuid4())
	worldPartRODGuid = str(uuid.uuid4())
	gen['PrimaryInstanceGuid'] = subWorldDataGuid

	# recreate the dict with the generated guids as keys
	newDict = {}
	newDict[subWorldDataGuid] = gen['Instances']['SubWorldDataGuid']
	newDict[descriptorGuid] = gen['Instances']['DescriptorGuid']
	newDict[registryGuid] = gen['Instances']['RegistryGuid']
	newDict[worldPartDataGuid] = gen['Instances']['WorldPartDataGuid']
	newDict[worldPartRODGuid] = gen['Instances']['WorldPartRODGuid']

	newDict[subWorldDataGuid]['Descriptor']['InstanceGuid'] = descriptorGuid
	newDict[subWorldDataGuid]['Descriptor']['PartitionGuid'] = partitionGuid
	newDict[subWorldDataGuid]['RegistryContainer']['InstanceGuid'] = registryGuid
	newDict[subWorldDataGuid]['RegistryContainer']['PartitionGuid'] = partitionGuid

	newDict[registryGuid]['BlueprintRegistry'][0]['PartitionGuid'] = partitionGuid
	newDict[registryGuid]['BlueprintRegistry'][0]['InstanceGuid'] = subWorldDataGuid
	newDict[registryGuid]['BlueprintRegistry'][1]['PartitionGuid'] = partitionGuid
	newDict[registryGuid]['BlueprintRegistry'][1]['InstanceGuid'] = worldPartDataGuid

	newDict[worldPartRODGuid]['Blueprint']['PartitionGuid'] = partitionGuid
	newDict[worldPartRODGuid]['Blueprint']['InstanceGuid'] = worldPartDataGuid

	newDict[subWorldDataGuid]['Objects'][0]['PartitionGuid'] = partitionGuid
	newDict[subWorldDataGuid]['Objects'][0]['InstanceGuid'] = worldPartRODGuid
	newDict[registryGuid]['ReferenceObjectRegistry'][0]['PartitionGuid'] = partitionGuid
	newDict[registryGuid]['ReferenceObjectRegistry'][0]['InstanceGuid'] = worldPartRODGuid

	newDict[worldPartDataGuid]['Name'] = 'StaticModelGroupEntityData'

	gen['Instances'] = newDict
	return gen

def ProcessMember(gen, levelTransforms, transformIndex, memberData):
	# add objectblueprint

	partition = GetPartitionEBX(memberData['MemberType']['PartitionGuid'])
	if not partition:
		error('Couldn\'t find partition with guid ' + memberData['MemberType']['PartitionGuid'])

	ogBlueprint = partition['Instances'][partition['PrimaryInstanceGuid']]

	# objectBlueprint = copy.deepcopy(objectBlueprintTemp)     #
	# objectBlueprintGuid = str(uuid.uuid4())     #
	# objectBlueprint['Object']['PartitionGuid'] = memberData['MemberType']['PartitionGuid']     #
	# objectBlueprint['Object']['InstanceGuid'] = memberData['MemberType']['InstanceGuid']     #

	# objectBlueprint['Name'] = ogBlueprint['Name']     #

	# gen['Instances'][objectBlueprintGuid] = objectBlueprint     #

	swd = gen['Instances'][gen['PrimaryInstanceGuid']]
	rc = gen['Instances'][swd['RegistryContainer']['InstanceGuid']]
	
	# rc['BlueprintRegistry'].append({     #
	#   'PartitionGuid': gen['PartitionGuid'],     #
	#   'InstanceGuid': objectBlueprintGuid     #
	#   })     #
	wprod = gen['Instances'][swd['Objects'][0]['InstanceGuid']]
	wpd = gen['Instances'][wprod['Blueprint']['InstanceGuid']]

	# if memberData['NetworkIdRange']['First'] != 0xffffffff:     #
	#   objectBlueprint['NeedNetworkId'] = True     #
	
	validScales = GetValidScales(partition, memberData['MemberType']['InstanceGuid'])

	for i in range(memberData['InstanceCount']):
		referenceObjectDataGuid = str(uuid.uuid4())

		referenceObjectData = copy.deepcopy(referenceObjectDataTemp)
		# referenceObjectData['Blueprint']['InstanceGuid'] = objectBlueprintGuid    #
		# referenceObjectData['Blueprint']['PartitionGuid'] = gen['PartitionGuid']    #
		referenceObjectData['Blueprint']['InstanceGuid'] = partition['PrimaryInstanceGuid']
		referenceObjectData['Blueprint']['PartitionGuid'] = partition['PartitionGuid']

		if i <= len(memberData['InstanceObjectVariation']) - 1 and memberData['InstanceObjectVariation'][i] != 0:
			variationHash = memberData['InstanceObjectVariation'][i]
			variation = Util.VariationMap.get(str(variationHash))

			if variation != None:
				referenceObjectData['ObjectVariation'] = {
					'PartitionGuid': variation[0],
					'InstanceGuid': variation[1]
					}
			# else:
			#   print('Found variation hash that is not on the variation map: ' + str(variationHash))

		referenceObjectData['CastSunShadowEnable'] = True

		if i <= len(memberData['InstanceCastSunShadow']) - 1:
			referenceObjectData['CastSunShadowEnable'] = memberData['InstanceCastSunShadow'][i]

		referenceObjectData['IndexInBlueprint'] = len(wpd['Objects']) + 30001


		if i <= len(memberData['InstanceTransforms']) - 1:
			referenceObjectData['BlueprintTransform'] = memberData['InstanceTransforms'][i]
		else:
			scale = 1.0
						
			if not validScales:
				# print('No valid scale for asset: ' + memberData['MemberType']['InstanceGuid'] +', ignoring instance')
				if not (memberData['MemberType']['InstanceGuid'] in invalidScalesFound):
					invalidScalesFound[memberData['MemberType']['InstanceGuid']] = {}
				# If the asset doesnt have any valid scale we can't substitute it with another scale, so we skip adding the ReferenceObjectData
				# of this instance and its reference to EBX
				transformIndex += 1
				continue

			if i <= len(memberData['InstanceScale']) - 1:
				targetScale = memberData['InstanceScale'][i]
				
				if str(targetScale) in validScales:
					scale = targetScale
				else:
					# Target scale is not valid
					if memberData['MemberType']['InstanceGuid'] in invalidScalesFound:
						invalidScalesFound[memberData['MemberType']['InstanceGuid']][targetScale] = True
					else:
						invalidScalesFound[memberData['MemberType']['InstanceGuid']] = {targetScale: True}

					# Find closest valid scale
					for validScale in validScales.keys():
						if abs(float(validScale) - targetScale) < abs(scale - targetScale):
							scale = float(validScale)

			quatAndPos = levelTransforms[transformIndex]
			rot = QuaternionToRotation(quatAndPos[0])
			referenceObjectData['BlueprintTransform']['right']['x'] = rot[0][0] * scale
			referenceObjectData['BlueprintTransform']['right']['y'] = rot[0][1] * scale
			referenceObjectData['BlueprintTransform']['right']['z'] = rot[0][2] * scale
			referenceObjectData['BlueprintTransform']['up']['x'] = rot[1][0] * scale
			referenceObjectData['BlueprintTransform']['up']['y'] = rot[1][1] * scale
			referenceObjectData['BlueprintTransform']['up']['z'] = rot[1][2] * scale
			referenceObjectData['BlueprintTransform']['forward']['x'] = rot[2][0] * scale
			referenceObjectData['BlueprintTransform']['forward']['y'] = rot[2][1] * scale
			referenceObjectData['BlueprintTransform']['forward']['z'] = rot[2][2] * scale
			referenceObjectData['BlueprintTransform']['trans']['x'] = quatAndPos[1][0]
			referenceObjectData['BlueprintTransform']['trans']['y'] = quatAndPos[1][1]
			referenceObjectData['BlueprintTransform']['trans']['z'] = quatAndPos[1][2]
			transformIndex += 1
		
		ref = {
			'PartitionGuid': gen['PartitionGuid'],
			'InstanceGuid': referenceObjectDataGuid
			}
		gen['Instances'][referenceObjectDataGuid] = referenceObjectData
		rc['ReferenceObjectRegistry'].append(ref)
		wpd['Objects'].append(ref)

	return transformIndex

def ProcessLevel(content, havokName):

	# Create structure
	gen = CreateInitialPartitionStruct(havokName)

	transformIndex = 0

	primaryInstanceGuid = content['PrimaryInstanceGuid']
	instances = content['Instances']
	levelData = instances.get(primaryInstanceGuid)

	for i, objGuids in enumerate(levelData['Objects']):
		objInstanceGuid = objGuids['InstanceGuid']
		obj = instances.get(objInstanceGuid)
		if obj['$type'] == 'StaticModelGroupEntityData':
			# print('Found StaticModelGroupEntityData')
			levelTransforms = Util.HavokTransforms.havokTransforms[havokName.lower()]
			# print(havokName)
			for j, memberData in enumerate(obj['MemberDatas']):
				transformIndex = ProcessMember(gen, levelTransforms, transformIndex, memberData)
			break

	return gen


##############################################


if __name__ == "__main__": 
	try:
		# set it up
		parser = argparse.ArgumentParser(description = '--ebxpath to configure BF3 EBX json dump')
		parser.add_argument("--ebxpath", type = str, default = os.path.join(os.getcwd(), 'Venice-EBX-JSON'), help = "Path to BF3 EBX json dump. Defualt is \".\\Venice-EBX-JSON\"")

		# get it
		args = parser.parse_args()
		EBX_DUMP_PATH = args.ebxpath
		print('parsed args')

		# main()
	except KeyboardInterrupt:
		print('User has exited the program')


for i, havokName in enumerate(Util.HavokNames.names):
	# havokName = 'levels/xp5_002/xp5_002/staticmodelgroup_physics_win32'
	invalidScalesFound = {}

	pathArray = havokName.split('/')

	if pathArray[1].lower() != pathArray[2].lower():
		continue

	path = os.path.join(EBX_DUMP_PATH, pathArray[0], pathArray[1], pathArray[2] + '.json')

	if os.path.exists(path) is False:
		error('Could not find Venice EBX Json dump')

	with open(path, 'r') as f:
		content = json.loads(f.read())
	f.close()
	print('Processing file: ' + havokName + '...')

	gen = ProcessLevel(content, havokName)

	
	if invalidScalesFound:
		print('Found invalid scales in the following assets:')

	for x, y in invalidScalesFound.items():
		if not y:
			print(x + ' does not have any valid scale')
		else:
			print(x, y.keys()) 
	print('File processed!')

	# NoHavok/Levels/XP5_001/Rush
	bundleName = 'NoHavok/' + pathArray[0] + '/' + pathArray[1] + '/' + pathArray[2]
	partitionName = bundleName.lower()
	gen['Name'] = partitionName
	swd = gen['Instances'][gen['PrimaryInstanceGuid']]
	# swd['Name'] = pathArray[2] + '/Havok (StaticModelGroup)'
	swd['Name'] = 'NoHavok'

	genJSON = json.dumps(gen, indent = 2)

	outPath = os.path.join(os.getcwd(), EXPORT_FOLDER, pathArray[0], pathArray[1])
	if not os.path.exists(outPath):
		os.makedirs(outPath)

	with open(os.path.join(outPath, pathArray[2] + '.json'), "w") as f:
		f.write(genJSON)
	f.close()
