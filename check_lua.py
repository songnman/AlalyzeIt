from operator import indexOf
import luadata
import re
import csv
import pandas as pd
import os.path
import csvtodb
import check_anim_data
import check_dungeonScript

from ntpath import join
from os import listdir
from os.path import isfile, join, splitext, exists

if not os.path.isdir('UnitInfo'): os.mkdir('UnitInfo') #!폴더 없으면 생성
def LoadData(path):
	code = open(path,'r', encoding='utf-8-sig')
	lines = code.read()
	lines = re.sub('--.*', '', lines)
	code.close()
	data = luadata.unserialize(lines,encoding='utf-8-sig')
	return data
def ExtractUnitScript(path,DataName):
	try:
		my_file = f'UnitInfo/{DataName}Script.csv'
		column_list = ["UnitName","Tag","DictName","StateIndex","EventName","EventIndex","Key","Value"]
		if exists(my_file): #TODO 파일 없을 때 새로 생성하는 부분 개선해야함.
			os.remove(my_file)
		f = open(my_file,'w', newline='')
		writer = csv.writer(f)
		writer.writerow(column_list)
		f.close()
		
		if exists("temp.csv"):
			os.remove("temp.csv")
		f = open("temp.csv",'w', newline='')
		writer = csv.writer(f)
		writer.writerow(column_list)
		
		for p in path:
			for item in Writing(p):
				writer.writerow(item)
		f.close()
		
		all_filenames = ["temp.csv", my_file]
		combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
		# combined_csv = combined_csv.drop_duplicates(column_list)#![2021-10-12 10:03:59]Drop 시키면 잃어버리는 데이터가 있음. 주석처리
		combined_csv.to_csv( my_file, index=False, encoding='utf-8-sig')
		os.remove("temp.csv")
		csvtodb.UpdateToDB(f'{DataName}Script',column_list)
	except Exception as e:
		print(str(e))
def Writing(path):
	content = []
	StateSet_List = ["m_listAttackStateData","m_listAirAttackStateData","m_listSkillStateData","m_listHyperSkillStateData","m_listHitCriticalFeedBack"]
	StateInfo_List = ["m_StateName"]
	StateInfo_Avoid_List = ["m_NKM_UNIT_STATE_TYPE"]
	StateInitData_List = ["m_listPhaseChangeData", "m_listAccumStateChangePack", "m_listStaticBuffData"]
	state_index = 0
		
	unit_name = splitext(os.path.basename(path))[0]
	data = LoadData(path)
	if data:
		for k, v in data.items():
			phase_index = 0
			if isinstance(v, list):
				for item in v: #?리스트니까 For문 돌려야됨
					if isinstance(item, dict): #? [2022-11-15 01:36:39] 리스트 값 대응
						phase_index += 1
						for i, j in item.items():
							if isinstance(j, list) and k not in StateInitData_List: #?리스트일 경우 스테이트 이벤트
								tag = "StateEvent"
								event_index = 0
								for item in j:
									if isinstance(item, dict):
										event_index += 1
										for x, y in item.items():
											content.append([unit_name,tag,k,state_index,i,event_index,x,y])
									else:
										tag = "StateInfo"
										content.append([unit_name,tag,k,state_index,None,event_index,i,j])
										break #? [2022-11-15 01:36:39] 리스트 값 대응
								continue
							elif k in StateSet_List: #?스테이트묶음 종류에 포함될 경우 스테이트묶음
								tag = "StateSet"
								
							elif k in StateInitData_List: #?[2022-01-30 22:51:40]스테이트 관련 데이터일경우.
								tag = "StateInitData"
								if isinstance(j, list): #?[2022-01-30 22:51:50]리스트일 경우 어큠스테이트
									for item in j:
										if j.index(item) > 0: phase_index += 1 #?[2022-01-31 00:29:06] List index가 1 이상일 경우 어큠스테이트의 구성요소가 2개 이상인 예외처리로 페이즈 인덱스 증가
										for x, y in item.items():
											content.append([unit_name,tag,k,state_index,None,phase_index,x,y])
								else: #?[2022-01-30 22:51:56] 이아니면 페이즈체인지 or Condition  묶음임.
									content.append([unit_name,tag,k,state_index,None,phase_index,i,j])
								continue
								
							else: #?나머지는 전부 스테이트 정보
								tag = "StateInfo"
							if i in StateInfo_List and k not in StateSet_List : state_index += 1 #! 인포셋에 걸리면 스테이트인덱스 증가
							if i in StateInfo_Avoid_List and k not in StateSet_List : continue
							content.append([unit_name,tag,k,state_index,None,0,i,j])
					else: #? [2022-11-15 01:36:39] 리스트 값 대응
						tag = "BasicInfo"
						content.append([unit_name,tag,None,state_index,None,0,k,v])
						break
			else:
				tag = "BasicInfo"
				content.append([unit_name,tag,None,state_index,None,0,k,v])
	return content
def ExtractDamageTemplet(path):
	try:
		my_file = 'UnitInfo/Damagetemplet.csv'
		column_list = ["DTName","List","ListIndex","Condition","Key","Value"]
		if not exists(my_file):
			f = open(my_file,'w', newline='')
			writer = csv.writer(f)
			writer.writerow(column_list)
			f.close()
		
		if exists("temp.csv"):
			os.remove("temp.csv")
		f = open('temp.csv','w', newline='')
		
		writer = csv.writer(f)
		writer.writerow(column_list)
		data = LoadData(path)
		for item in data:
			for k, v in item.items():
				if k == "m_DamageTempletName":
					DT_Name = v
				else:
					if isinstance(v, list):
						for item in v: #?리스트니까 For문 돌려야됨
							if isinstance(item, dict):
								for i, j in item.items():
									if isinstance(j, dict):
										for x, y in j.items():
											writer.writerow([DT_Name,k,v.index(item)+1,i,x,y])
									else:
										writer.writerow([DT_Name,k,v.index(item)+1,None,i,j])
							else:
								writer.writerow([DT_Name,None,0,None,k,v])
					elif isinstance(v, dict): #![2023-09-21 16:34:17] EventMove 대응함
						for i, j in v.items():
							writer.writerow([DT_Name,k,0,None,i,j])
					else:
						writer.writerow([DT_Name,None,0,None,k,v])
		f.close()
		all_filenames = ["temp.csv", my_file]
		combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
		# combined_csv = combined_csv.drop_duplicates(["DTName","Key","Value"])#![2021-10-12 10:03:59]Drop 시키면 잃어버리는 데이터가 있음. 주석처리
		combined_csv.to_csv( my_file, index=False, encoding='utf-8-sig')
		os.remove("temp.csv")
		csvtodb.UpdateToDB('Damagetemplet',column_list)
	except Exception as e:
		print(str(e))
def ExtractDamageEffectTemplet(path):
	try:
		my_file = 'UnitInfo/DamageEffectTemplet.csv'
		column_list = ["EffectName","Tag","StateIndex","EventName","EventIndex","Key","Value"]
		if not exists(my_file):
			f = open(my_file,'w', newline='')
			writer = csv.writer(f)
			writer.writerow(column_list)
			f.close()
		
		if exists("temp.csv"):
			os.remove("temp.csv")
		f = open('temp.csv','w', newline='')
		
		writer = csv.writer(f)
		writer.writerow(column_list)
		Effect_Name = None
		data = LoadData(path)
		StateInfo_List = ["m_StateName"]
		
		for item in data:
			for k, v in item.items():
				if k == "m_DamageEffectID":
					Effect_Name = v
					continue
				state_index = 0
				if isinstance(v, list):
					for item in v: #?리스트니까 For문 돌려야됨
						if isinstance(item, list):
							continue
						else:
							for i, j in item.items():
								if isinstance(j, list):
									for item in j:
										if isinstance(item, dict):
											tag = "StateEvent"
											for x, y in item.items():
												writer.writerow([Effect_Name,tag,state_index,i,j.index(item)+1,x,y])
										else:
											writer.writerow([Effect_Name,tag,state_index,k,0,i,item])
								else:
									if "DieEvent" in k:
										tag = "DieEvent"
										writer.writerow([Effect_Name,tag,state_index,k,0,i,j])
									else:
										tag = "StateInfo"
										if i in StateInfo_List : state_index += 1
										writer.writerow([Effect_Name,tag,state_index,None,0,i,j])
				else:
					tag = "BasicInfo"
					writer.writerow([Effect_Name,tag,state_index,None,0,k,v])
		f.close()
		all_filenames = ["temp.csv", my_file]
		combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
		# combined_csv = combined_csv.drop_duplicates(["EffectName","Tag","EventName","EventIndex","Key","Value"]) #![2021-10-12 10:03:59]Drop 시키면 잃어버리는 데이터가 있음. 주석처리
		combined_csv.to_csv( my_file, index=False, encoding='utf-8-sig')
		os.remove("temp.csv")
		csvtodb.UpdateToDB('DamageEffectTemplet',column_list)
	except Exception as e:
		print(str(e))

ScriptBase_Path = "C:\\DOC_leeseunghwan.dev\\CounterSide\\CODE\\CSClient\\Assets\\ASSET_BUNDLE\\AB_SCRIPT\\"
UnitScript_Path = [join(f"{ScriptBase_Path}AB_SCRIPT_UNIT_DATA\\AB_SCRIPT_UNIT_DATA_UNIT_TEMPLET\\", f) for f in listdir(f"{ScriptBase_Path}AB_SCRIPT_UNIT_DATA\\AB_SCRIPT_UNIT_DATA_UNIT_TEMPLET\\") if isfile(join(f"{ScriptBase_Path}AB_SCRIPT_UNIT_DATA\\AB_SCRIPT_UNIT_DATA_UNIT_TEMPLET\\", f) ) and "NKM_UNIT_" in f and splitext(f)[1] == ".txt"]
ShipScript_Path = [join(f"{ScriptBase_Path}AB_SCRIPT_UNIT_DATA\\AB_SCRIPT_UNIT_DATA_UNIT_TEMPLET\\", f) for f in listdir(f"{ScriptBase_Path}AB_SCRIPT_UNIT_DATA\\AB_SCRIPT_UNIT_DATA_UNIT_TEMPLET\\") if isfile(join(f"{ScriptBase_Path}AB_SCRIPT_UNIT_DATA\\AB_SCRIPT_UNIT_DATA_UNIT_TEMPLET\\", f) ) and "NKM_SHIP_" in f and splitext(f)[1] == ".txt"]
MobScript_Path = [join(f"{ScriptBase_Path}AB_SCRIPT_UNIT_DATA\\AB_SCRIPT_UNIT_DATA_UNIT_TEMPLET\\", f) for f in listdir(f"{ScriptBase_Path}AB_SCRIPT_UNIT_DATA\\AB_SCRIPT_UNIT_DATA_UNIT_TEMPLET\\") if isfile(join(f"{ScriptBase_Path}AB_SCRIPT_UNIT_DATA\\AB_SCRIPT_UNIT_DATA_UNIT_TEMPLET\\", f) ) and ("NKM_MONSTER_" in f or "NKM_MOB_" in f or "NKM_SHADOW_" in f) and splitext(f)[1] == ".txt"]
DamageTemplet_Path = [join(ScriptBase_Path, f) for f in listdir(ScriptBase_Path) if isfile(join(ScriptBase_Path, f) ) and "LUA_DAMAGE_TEMPLET" in f and "_BASE" not in f and splitext(f)[1] == ".txt"]
DamageTemplet_Path.reverse()
DamageEffectTemplet_Path = [join(f"{ScriptBase_Path}AB_SCRIPT_EFFECT\\", f) for f in listdir(f"{ScriptBase_Path}AB_SCRIPT_EFFECT\\") if isfile(join(f"{ScriptBase_Path}AB_SCRIPT_EFFECT\\", f) ) and "LUA_DAMAGE_EFFECT_TEMPLET" in f and splitext(f)[1] == ".txt"]
DamageEffectTemplet_Path.reverse()
AnimData_Path = join(f"{ScriptBase_Path}AB_SCRIPT_ANIM_DATA\\", "LUA_ANIM_DATA.txt")
DungeonScript_Path = [join(f"{ScriptBase_Path}AB_SCRIPT_DUNGEON_TEMPLET\\AB_SCRIPT_DUNGEON_TEMPLET_ALL\\", f) for f in listdir(f"{ScriptBase_Path}AB_SCRIPT_DUNGEON_TEMPLET\\AB_SCRIPT_DUNGEON_TEMPLET_ALL\\") if isfile(join(f"{ScriptBase_Path}AB_SCRIPT_DUNGEON_TEMPLET\\AB_SCRIPT_DUNGEON_TEMPLET_ALL\\", f) ) and splitext(f)[1] == ".txt"]

print("UnitScript Extract Count :", len(UnitScript_Path))
ExtractUnitScript(UnitScript_Path,"Unit")
print("UnitScript ExtractDone.")

print("ShipScript Extract Count :", len(ShipScript_Path))
ExtractUnitScript(ShipScript_Path,"Ship")
print("ShipScript ExtractDone.")

print("MobScript Extract Count :", len(MobScript_Path))
ExtractUnitScript(MobScript_Path,"Mob")
print("MobScript ExtractDone.")

print("DamageTemplet Extract Count :", len(DamageTemplet_Path))
my_file = 'UnitInfo/Damagetemplet.csv'
if exists(my_file):
	os.remove(my_file)
f = open(my_file,'w', newline='')
writer = csv.writer(f)
writer.writerow(["DTName","List","ListIndex","Condition","Key","Value"])
f.close()
for path in DamageTemplet_Path:
	ExtractDamageTemplet(path)
print("DamageTemplet ExtractDone.")

print("DamageEffectTemplet Extract Count :", len(DamageEffectTemplet_Path))
my_file = 'UnitInfo/DamageEffectTemplet.csv'
if exists(my_file):
	os.remove(my_file)
f = open(my_file,'w', newline='')
writer = csv.writer(f)
writer.writerow(["EffectName","Tag","StateIndex","EventName","EventIndex","Key","Value"])
f.close()
for path in DamageEffectTemplet_Path:
	ExtractDamageEffectTemplet(path)
print("DamageEffectTemplet ExtractDone.")

print("AnimData Extract")
check_anim_data.ExtractAnimData(AnimData_Path)
print("AnimData ExtractDone.")

print("DungeonScript Extract Count :", len(DungeonScript_Path))
check_dungeonScript.ExtractDungeonScript(DungeonScript_Path)
print("DungeonScript ExtractDone.")

print("All ExtractDone.")


# Test_unit_Path = ["C:\\DOC_leeseunghwan.dev\\CounterSide\\CODE\\CSClient\\Assets\\ASSET_BUNDLE\\AB_SCRIPT\\AB_SCRIPT_UNIT_DATA\\AB_SCRIPT_UNIT_DATA_UNIT_TEMPLET\\NKM_UNIT_C_ALPHA_JIA.txt"]
# print("Extract Count :", len(Test_unit_Path))
# ExtractUnitScript(Test_unit_Path,"Test")
# print("TestScript ExtractDone.")

# test_path = [
# "C:\\DOC_leeseunghwan.dev\\CounterSide\\CODE\\CSClient\\Assets\\ASSET_BUNDLE\\AB_SCRIPT\\AB_SCRIPT_UNIT_DATA\\AB_SCRIPT_UNIT_DATA_UNIT_TEMPLET\\NKM_MONSTER_BOSS_BASIC_ADMIN_HILDE_ADMIN_MOVE_H.txt",
# ]
# for path in test_path:
# 	ExtractUnitScript(path,"Test")


# df1 = {}
# df2 = {}
# df3 = {}
# df1 = pd.DataFrame.from_dict(df1, orient='index')
# df2 = pd.DataFrame.from_dict(df2, orient='index')
# df3 = pd.DataFrame.from_dict(df3, orient='index')

# writer = pd.ExcelWriter("LUAsheet.xlsx", engine = 'xlsxwriter')
# df1.to_excel(writer, sheet_name = 'x1')
# df2.to_excel(writer, sheet_name = 'x2')
# df3.to_excel(writer, sheet_name = 'x3')
# writer.save()