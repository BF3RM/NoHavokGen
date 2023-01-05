---@class CustomLevelLoaderConfig
---@field LOGGER_ENABLED boolean
---@field CLIENT_TIMEOUT number
Config = require "__shared/Config"

local BUNDLE_PREFIX = 'NoHavok'
local m_LazyLoadedCount = 0

local print = function(p_Message, p_IsWarning)
	if Config.LOGGER_ENABLED or p_IsWarning then
		if p_IsWarning then
			p_Message = 'WARNING: ' .. p_Message
		end

		print(p_Message)
	end
end

-- nº 1 in calling order
Events:Subscribe('Level:LoadResources', function(p_LevelName, p_GameMode, p_IsDedicatedServer)
	print("Loading resources")

	local s_SuperBundleName = string.gsub(p_LevelName, 'Levels', BUNDLE_PREFIX)
	print("Mounting SuperBundle: " .. s_SuperBundleName)
	ResourceManager:MountSuperBundle(s_SuperBundleName)
end)

local function _GetHighestIndexInPartition(s_Partition)
	local s_HighestIndexInPartition = 0

	for _, l_Instance in ipairs(s_Partition.instances) do
		if l_Instance:Is("GameObjectData") then
			l_Instance = GameObjectData(l_Instance)

			if l_Instance.indexInBlueprint > s_HighestIndexInPartition and l_Instance.indexInBlueprint ~= 65535 then
				s_HighestIndexInPartition = l_Instance.indexInBlueprint
			end
		end
	end

	return s_HighestIndexInPartition
end

---Patches the level, adding a SubWorldReferenceObjectData to the level that references the SubWorld in the custom bundle
local function _PatchLevel(p_LevelPath)
	local s_Data = LevelData(ResourceManager:SearchForDataContainer(p_LevelPath))
	s_Data:MakeWritable()

	local s_SWROD = SubWorldReferenceObjectData(Guid('73756277-6f72-6c64-6e6f-006861766f6b')) -- subworld no havok

	local s_LevelName = p_LevelPath:gsub(".*/", "")
	
	s_SWROD.bundleName = BUNDLE_PREFIX .. '/' .. s_LevelName .. '/' .. s_LevelName
	s_SWROD.blueprintTransform = LinearTransform()
	s_SWROD.blueprint = nil
	s_SWROD.objectVariation = nil
	s_SWROD.streamRealm = StreamRealm.StreamRealm_Both
	s_SWROD.castSunShadowEnable = true
	s_SWROD.excluded = false
	s_SWROD.inclusionSettings = nil
	s_SWROD.autoLoad = true
	s_SWROD.isWin32SubLevel = true
	s_SWROD.isXenonSubLevel = true
	s_SWROD.isPs3SubLevel = true
	s_SWROD.isEventConnectionTarget  = 2
	s_SWROD.isPropertyConnectionTarget  = 3

	local s_Partition = s_Data.partition

	if not s_Partition then
		print('Partition was nil', true)
		return
	end

	s_Partition:AddInstance(s_SWROD)

	local s_HighestIndexInPartition = _GetHighestIndexInPartition(s_Partition)
	s_SWROD.indexInBlueprint = s_HighestIndexInPartition + 1

	if s_Data.registryContainer ~= nil then
		s_Data.registryContainer:MakeWritable()
		local s_Registry = RegistryContainer(s_Data.registryContainer)
		s_Registry.referenceObjectRegistry:add(s_SWROD)
	end

	local s_LinkConnection = LinkConnection()
	s_LinkConnection.target = s_SWROD

	s_Data.linkConnections:add(s_LinkConnection)
	s_Data.objects:add(s_SWROD)
	print('Patched level')
end

Events:Subscribe('Partition:Loaded', function(p_Partition)
	local s_LevelPath = SharedUtils:GetLevelName()

	if not s_LevelPath then return end

	if p_Partition.name == s_LevelPath:lower() then
		print('Patching level')

		local s_LevelData = LevelData(p_Partition.primaryInstance)

		for _, l_Object in ipairs(s_LevelData.objects) do
			l_Object = _G[l_Object.typeInfo.name](l_Object)

			if l_Object.blueprint and l_Object.blueprint.isLazyLoaded then
				m_LazyLoadedCount = m_LazyLoadedCount + 1
				print("LazyLoadedCount " .. m_LazyLoadedCount)
				
				l_Object.blueprint:RegisterLoadHandlerOnce(function (p_Instance)
					m_LazyLoadedCount = m_LazyLoadedCount - 1
					if m_LazyLoadedCount == 0 then _PatchLevel(s_LevelPath) end
				end)
			end

			if l_Object:Is('StaticModelGroupEntityData') then
				print('Found StaticModelGroupEntityData, excluding')
				local s_StaticModelGroup = StaticModelGroupEntityData(l_Object)
				s_StaticModelGroup:MakeWritable()
				s_StaticModelGroup.memberDatas:clear()
			end
		end

		if m_LazyLoadedCount == 0 then _PatchLevel(s_LevelPath) end
	end
end)

-- Increase timeout 
ResourceManager:RegisterInstanceLoadHandler(Guid('C4DCACFF-ED8F-BC87-F647-0BC8ACE0D9B4'), Guid('B479A8FA-67FF-8825-9421-B31DE95B551A'), function(p_Instance)
	p_Instance = ClientSettings(p_Instance)
	p_Instance:MakeWritable()
	p_Instance.loadedTimeout = math.max(Config.LOADING_TIMEOUT, p_Instance.loadedTimeout or 0)
	p_Instance.loadingTimeout = math.max(Config.LOADING_TIMEOUT, p_Instance.loadingTimeout or 0)
	p_Instance.ingameTimeout = math.max(Config.LOADING_TIMEOUT, p_Instance.ingameTimeout or 0)
	print("Changed ClientSettings")
end)

ResourceManager:RegisterInstanceLoadHandler(Guid('C4DCACFF-ED8F-BC87-F647-0BC8ACE0D9B4'), Guid('818334B3-CEA6-FC3F-B524-4A0FED28CA35'), function(p_Instance)
	p_Instance = ServerSettings(p_Instance)
	p_Instance:MakeWritable()
	p_Instance.loadingTimeout = math.max(Config.LOADING_TIMEOUT, p_Instance.loadingTimeout or 0)
	p_Instance.ingameTimeout = math.max(Config.LOADING_TIMEOUT, p_Instance.ingameTimeout or 0)
	p_Instance.timeoutTime = math.max(Config.LOADING_TIMEOUT, p_Instance.timeoutTime or 0)
	print("Changed ServerSettings")
end)

