# -*- coding: utf-8 -*-
# @Author: JinZhang
# @Date:   2019-05-31 11:23:44
# @Last Modified by:   JinZhang
# @Last Modified time: 2020-05-21 16:45:31
import os, sys;
import shutil, json;

# 分割等号
def _splitEqualSign_(modstr):
	modstr = modstr.strip();
	if modstr.find("=") != -1:
		if modstr.find("==") != -1:
			return tuple(modstr.split("=="));
		return tuple(modstr.split("="));
	return (modstr, "");

# 获取json数据
def _getJsonData_(filePath):
	if os.path.exists(filePath):
		with open(filePath, "r") as f:
			return json.loads(f.read());
	return {};

# 根据目录获取md5列表
def _getMd5Map_(tempPath, targetPath):
	tmpMd5, targetMd5 = {}, {};
	fileName = "_file_md5_map_.json";
	filePath = os.path.join(tempPath, fileName);
	if os.path.exists(filePath):
		tmpMd5 = _getJsonData_(filePath);
	filePath = os.path.join(targetPath, fileName);
	if os.path.exists(filePath):
		targetMd5 = _getJsonData_(filePath);
	return tmpMd5, targetMd5;

# 根据目录处理文件
def _copyFileByMd5s_(tempPath, targetPath):
	tmpMd5Map, tgMd5Map = _getMd5Map_(tempPath, targetPath);
	for k,v in tmpMd5Map.items():
		tmpFile, tgFile = os.path.join(tempPath, k), os.path.join(targetPath, k);
		if os.path.exists(tmpFile) and v == tgMd5Map.get(k, ""):
			continue; # 已存在且md5值一样，则跳过
		if not os.path.exists(tgFile):
			return False; # 不存在目标文件，则更新失败
		shutil.copyfile(tgFile, tmpFile); # 拷贝文件
	return True;

# 获取依赖模块列表
def _getDependMods_(assetsPath):
	modList, modFile = [], os.path.join(assetsPath, "depends.mod");
	if not os.path.exists(modFile):
		return modList;
	with open(modFile, "r") as f:
		for line in f.readlines():
			mod = splitEqualSign(line.strip());
			if mod not in modList:
				modList.append(mod);
	return modList;

# 获取不同的依赖模块列表
def _diffDependMods_(tempPath, targetPath):
	modList = [];
	tempModList, tgtModList = _getDependMods_(tempPath), _getDependMods_(targetPath);
	tgtModMap = {};
	for mod, ver in tgtModList:
		tgtModMap[mod] = ver;
	for mod, ver in tempModList:
		if mod not in tgtModMap:
			modList.append((mod, ver));
		elif ver and ver != tgtModMap[mod]:
			modList.append((mod, ver));
	return modList;

# 检测依赖模块列表
def _checkDependMapJson_(tempPath, targetPath, dependMapFile):
	isChange, dependMap = False, _getJsonData_(dependMapFile);
	for mod, ver in _diffDependMods_(tempPath, targetPath):
		if mod not in dependMap:
			dependMap[mod] = {
				"ver" : v,
				"map" : {
					"pytoolsip" : v,
				},
			};
		else:
			depend = dependMap[m];
			depend["ver"] = v;
			depend["map"]["pytoolsip"] = v;
			for ver in depend["map"].values():
				if ver:
					depend["ver"] = ver;
		isChange = True;
	if isChange:
		with open(dependMapFile, "w") as f:
			f.write(json.dumps(dependMap));
	return dependMap;

# 校验平台assets
def verifyAssets(tempPath, targetPath, dependMapFile):
	if _copyFileByMd5s_(tempPath, targetPath):
		# _checkDependMapJson_(tempPath, targetPath, dependMapFile); # 检测依赖模块配置
		return True;
	return False;