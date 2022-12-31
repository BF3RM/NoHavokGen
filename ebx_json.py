import uuid
import json
import os
import copy
import util

from templates import subWorldDataTemp, objectBlueprintTemp, referenceObjectDataTemp

INTERMEDIATE_FOLDER_NAME = 'intermediate'
EBX_JSON_FOLDER_NAME = 'ebx_json'

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

def GetPartitionEBX(partitionGuid, dump_dir):
	ebx_file_path = util.PartitionMap[partitionGuid]

	path = os.path.join(dump_dir, ebx_file_path)

	if os.path.exists(path) is False:
		print('Error: Could not find Venice EBX Json dump')
		# continue

	with open(path, 'r') as f:
		partition_ebx = json.loads(f.read())

	return partition_ebx

def GetValidScales(partition, instance_guid):
	static_model_entity_data = partition['Instances'][instance_guid]
	scales = {}

	if 'PhysicsData' in static_model_entity_data and static_model_entity_data['PhysicsData'] and 'InstanceGuid' in static_model_entity_data['PhysicsData'] and static_model_entity_data['PhysicsData']['InstanceGuid'] and static_model_entity_data['PhysicsData']['InstanceGuid'] in partition['Instances']:
		physics_data = partition['Instances'][static_model_entity_data['PhysicsData']['InstanceGuid']]

		for entry in physics_data['ScaledAssets']:
			havok_asset = partition['Instances'][entry['InstanceGuid']]
			name = havok_asset['Name']
			
			# check if actually exists (some collisions dont exist, probably due to optimizations)
			if name.lower() in util.PhysicsContent.physicsContent:
				scales[str(havok_asset['Scale'])] = True

	return scales

def CreateInitialPartitionStruct(og_partition_uuid: uuid.UUID):
	gen = copy.deepcopy(subWorldDataTemp)
	partition_guid = str(uuid.uuid3(og_partition_uuid, 'partition'))
	gen['PartitionGuid'] = partition_guid

	sub_world_data_guid = str(uuid.uuid3(og_partition_uuid, 'subworlddata'))
	descriptor_guid = str(uuid.uuid3(og_partition_uuid, 'descriptor'))
	registry_guid = str(uuid.uuid3(og_partition_uuid, 'registry'))
	world_part_data_guid = str(uuid.uuid3(og_partition_uuid, 'worldpartdata'))
	world_part_ROD_guid = str(uuid.uuid3(og_partition_uuid, 'referenceobjectdata'))
	gen['PrimaryInstanceGuid'] = sub_world_data_guid

	# recreate the dict with the generated guids as keys
	new_dict = {}
	new_dict[sub_world_data_guid] = gen['Instances']['SubWorldDataGuid']
	new_dict[descriptor_guid] = gen['Instances']['DescriptorGuid']
	new_dict[registry_guid] = gen['Instances']['RegistryGuid']
	new_dict[world_part_data_guid] = gen['Instances']['WorldPartDataGuid']
	new_dict[world_part_ROD_guid] = gen['Instances']['WorldPartRODGuid']

	new_dict[sub_world_data_guid]['Descriptor']['InstanceGuid'] = descriptor_guid
	new_dict[sub_world_data_guid]['Descriptor']['PartitionGuid'] = partition_guid
	new_dict[sub_world_data_guid]['RegistryContainer']['InstanceGuid'] = registry_guid
	new_dict[sub_world_data_guid]['RegistryContainer']['PartitionGuid'] = partition_guid

	new_dict[registry_guid]['BlueprintRegistry'][0]['PartitionGuid'] = partition_guid
	new_dict[registry_guid]['BlueprintRegistry'][0]['InstanceGuid'] = sub_world_data_guid
	new_dict[registry_guid]['BlueprintRegistry'][1]['PartitionGuid'] = partition_guid
	new_dict[registry_guid]['BlueprintRegistry'][1]['InstanceGuid'] = world_part_data_guid

	new_dict[world_part_ROD_guid]['Blueprint']['PartitionGuid'] = partition_guid
	new_dict[world_part_ROD_guid]['Blueprint']['InstanceGuid'] = world_part_data_guid

	new_dict[sub_world_data_guid]['Objects'][0]['PartitionGuid'] = partition_guid
	new_dict[sub_world_data_guid]['Objects'][0]['InstanceGuid'] = world_part_ROD_guid
	new_dict[registry_guid]['ReferenceObjectRegistry'][0]['PartitionGuid'] = partition_guid
	new_dict[registry_guid]['ReferenceObjectRegistry'][0]['InstanceGuid'] = world_part_ROD_guid

	new_dict[world_part_data_guid]['Name'] = 'StaticModelGroupEntityData'

	gen['Instances'] = new_dict
	return gen

def ProcessMember(gen, og_partition_uuid: uuid.UUID, level_transforms, transform_index, member_data, invalid_scales_found, dump_dir):
	# add objectblueprint

	partition = GetPartitionEBX(member_data['MemberType']['PartitionGuid'], dump_dir)
	if not partition:
		print('Error: Couldn\'t find partition with guid ' + member_data['MemberType']['PartitionGuid'])
		return

	original_blueprint = partition['Instances'][partition['PrimaryInstanceGuid']]

	swd = gen['Instances'][gen['PrimaryInstanceGuid']]
	rc = gen['Instances'][swd['RegistryContainer']['InstanceGuid']]
	wprod = gen['Instances'][swd['Objects'][0]['InstanceGuid']]
	wpd = gen['Instances'][wprod['Blueprint']['InstanceGuid']]
	
	# needs_network_id = member_data['NetworkIdRange']['First'] != 4294967295 # 0xffffffff
	needs_network_id = False

	if needs_network_id:
		# Needs network id, so we need to clone the blueprint
		object_blueprint = copy.deepcopy(objectBlueprintTemp)
		object_blueprint['NeedNetworkId'] = True
		object_blueprint_guid = str(uuid.uuid3(og_partition_uuid, original_blueprint['Name']))
		object_blueprint['Object']['PartitionGuid'] = member_data['MemberType']['PartitionGuid']
		object_blueprint['Object']['InstanceGuid'] = member_data['MemberType']['InstanceGuid']

		object_blueprint['Name'] = original_blueprint['Name']

		gen['Instances'][object_blueprint_guid] = object_blueprint

		rc['BlueprintRegistry'].append({
			'PartitionGuid': gen['PartitionGuid'],
			'InstanceGuid': object_blueprint_guid
			})

	valid_scales = GetValidScales(partition, member_data['MemberType']['InstanceGuid'])

	for i in range(member_data['InstanceCount']):
		reference_object_data_guid = str(uuid.uuid3(og_partition_uuid, member_data['MemberType']['InstanceGuid'] + str(i)))

		reference_object_data = copy.deepcopy(referenceObjectDataTemp)

		if needs_network_id:
			# use cloned blueprint
			reference_object_data['Blueprint']['InstanceGuid'] = object_blueprint_guid
			reference_object_data['Blueprint']['PartitionGuid'] = gen['PartitionGuid']
		else:
			# use original blueprint
			reference_object_data['Blueprint']['InstanceGuid'] = partition['PrimaryInstanceGuid']
			reference_object_data['Blueprint']['PartitionGuid'] = partition['PartitionGuid']

		if i <= len(member_data['InstanceObjectVariation']) - 1 and member_data['InstanceObjectVariation'][i] != 0:
			variation_hash = member_data['InstanceObjectVariation'][i]
			variation = util.VariationMap.get(str(variation_hash))

			if variation != None:
				reference_object_data['ObjectVariation'] = {
					'PartitionGuid': variation[0],
					'InstanceGuid': variation[1]
					}
			# else:
			#   print('Found variation hash that is not on the variation map: ' + str(variationHash))

		reference_object_data['CastSunShadowEnable'] = True

		if i <= len(member_data['InstanceCastSunShadow']) - 1:
			reference_object_data['CastSunShadowEnable'] = member_data['InstanceCastSunShadow'][i]

		reference_object_data['IndexInBlueprint'] = len(wpd['Objects']) + 30001

		if i <= len(member_data['InstanceTransforms']) - 1:
			reference_object_data['BlueprintTransform'] = member_data['InstanceTransforms'][i]
		else:
			scale = 1.0
						
			if not valid_scales:
				# print('No valid scale for asset: ' + memberData['MemberType']['InstanceGuid'] +', ignoring instance')
				if not (member_data['MemberType']['InstanceGuid'] in invalid_scales_found):
					invalid_scales_found[member_data['MemberType']['InstanceGuid']] = {}
				# If the asset doesnt have any valid scale we can't substitute it with another scale, so we skip adding the ReferenceObjectData
				# of this instance and its reference to EBX
				transform_index += 1
				continue

			if i <= len(member_data['InstanceScale']) - 1:
				target_scale = member_data['InstanceScale'][i]
				
				if str(target_scale) in valid_scales:
					scale = target_scale
				else:
					# Target scale is not valid
					if not member_data['MemberType']['InstanceGuid'] in invalid_scales_found:
						invalid_scales_found[member_data['MemberType']['InstanceGuid']] = {}
					
					invalid_scales_found[member_data['MemberType']['InstanceGuid']][target_scale] = True

					# Find closest valid scale
					for valid_scale in valid_scales.keys():
						if abs(float(valid_scale) - target_scale) < abs(scale - target_scale):
							scale = float(valid_scale)

			quat_and_pos = level_transforms[transform_index]
			rot = QuaternionToRotation(quat_and_pos[0])
			reference_object_data['BlueprintTransform']['right']['x'] = rot[0][0] * scale
			reference_object_data['BlueprintTransform']['right']['y'] = rot[0][1] * scale
			reference_object_data['BlueprintTransform']['right']['z'] = rot[0][2] * scale
			reference_object_data['BlueprintTransform']['up']['x'] = rot[1][0] * scale
			reference_object_data['BlueprintTransform']['up']['y'] = rot[1][1] * scale
			reference_object_data['BlueprintTransform']['up']['z'] = rot[1][2] * scale
			reference_object_data['BlueprintTransform']['forward']['x'] = rot[2][0] * scale
			reference_object_data['BlueprintTransform']['forward']['y'] = rot[2][1] * scale
			reference_object_data['BlueprintTransform']['forward']['z'] = rot[2][2] * scale
			reference_object_data['BlueprintTransform']['trans']['x'] = quat_and_pos[1][0]
			reference_object_data['BlueprintTransform']['trans']['y'] = quat_and_pos[1][1]
			reference_object_data['BlueprintTransform']['trans']['z'] = quat_and_pos[1][2]
			transform_index += 1
	
		ref = {
			'PartitionGuid': gen['PartitionGuid'],
			'InstanceGuid': reference_object_data_guid
			}
		gen['Instances'][reference_object_data_guid] = reference_object_data
		rc['ReferenceObjectRegistry'].append(ref)
		wpd['Objects'].append(ref)

	return transform_index

def ProcessLevel(content, havok_name, invalid_scales_found, dump_dir):

	# Create structure
	partition_guid = content['PartitionGuid']
	gen = CreateInitialPartitionStruct(uuid.UUID(partition_guid))

	transform_index = 0

	primary_instance_guid = content['PrimaryInstanceGuid']
	instances = content['Instances']
	level_data = instances.get(primary_instance_guid)

	for _, obj_guids in enumerate(level_data['Objects']):
		obj_instance_guid = obj_guids['InstanceGuid']
		obj = instances.get(obj_instance_guid)
		if obj['$type'] == 'StaticModelGroupEntityData':
			# print('Found StaticModelGroupEntityData')
			level_transforms = util.HavokTransforms.havokTransforms[havok_name.lower()]
			# print(havokName)
			for _, member_data in enumerate(obj['MemberDatas']):
				transform_index = ProcessMember(gen, uuid.UUID(partition_guid), level_transforms, transform_index, member_data, invalid_scales_found, dump_dir)
			break

	return gen

def generate_ebx_json(dump_dir: str):
	for _, havok_name in enumerate(util.HavokNames.names):
		# havok_name = 'levels/xp5_002/xp5_002/staticmodelgroup_physics_win32'
		invalid_scales_found = {}

		path_array = havok_name.split('/')

		if path_array[1].lower() != path_array[2].lower():
			continue

		path = os.path.join(dump_dir, path_array[0], path_array[1], path_array[2] + '.json')

		if os.path.exists(path) is False:
			print('Error: Could not find Venice EBX Json dump')
			return

		with open(path, 'r') as f:
			content = json.loads(f.read())
		print('Processing file: ' + havok_name + '...')

		gen = ProcessLevel(content, havok_name, invalid_scales_found, dump_dir)

		
		if invalid_scales_found:
			print('Found invalid scales in the following assets:')

		for x, y in invalid_scales_found.items():
			if not y:
				print(x + ' does not have any valid scale')
			else:
				print("{} has the following invalid scales: {}".format(x, y.keys()))
		print('File processed!')

		# NoHavok/XP5_001/Rush
		bundle_name = 'NoHavok/' + path_array[1] + '/' + path_array[2]
		partition_name = bundle_name.lower()
		gen['Name'] = partition_name
		swd = gen['Instances'][gen['PrimaryInstanceGuid']]
		# swd['Name'] = pathArray[2] + '/Havok (StaticModelGroup)'
		swd['Name'] = 'NoHavok'

		gen_JSON = json.dumps(gen, indent = 2)

		out_path = os.path.join(os.getcwd(), INTERMEDIATE_FOLDER_NAME,  EBX_JSON_FOLDER_NAME, path_array[1])
		if not os.path.exists(out_path):
			os.makedirs(out_path)

		with open(os.path.join(out_path, path_array[2] + '.json'), "w") as f:
			f.write(gen_JSON)
