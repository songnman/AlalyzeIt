from ntpath import join
import luadata
import re
import csv
import pandas as pd
import os.path

from os import listdir
from os.path import isfile, join, splitext, exists

def LoadData(path):
	code = open(path,'r', encoding='utf-8-sig')
	lines = code.read()
	lines = re.sub('--.*', '', lines)
	code.close()
	data = luadata.unserialize(lines,encoding='utf-8-sig')
	return data

def ExtractUnitScript(path,DataName):
	try:
		if exists("temp.csv"):
			os.remove("temp.csv")
		my_file = f'UnitInfo/{DataName}Script.csv'
		
		if not exists(my_file): #TODO 파일 없을 때 새로 생성하는 부분 개선해야함.
			f = open(my_file,'w', newline='')
			writer = csv.writer(f)
			writer.writerow(["UnitName","Tag","DictName","StateIndex","EventName","EventIndex","Key","Value"])
			f.close()
		
		f = open("temp.csv",'w', newline='')
		writer = csv.writer(f)
		writer.writerow(["UnitName","Tag","DictName","StateIndex","EventName","EventIndex","Key","Value"])
		
		for p in path:
			for item in Writing(p):
				writer.writerow(item)
		f.close()
		
		all_filenames = ["temp.csv", my_file]
		combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
		combined_csv = combined_csv.drop_duplicates(["UnitName","Tag","DictName","StateIndex","EventName","EventIndex","Key","Value"])
		combined_csv.to_csv( my_file, index=False, encoding='utf-8-sig')
		os.remove("temp.csv")
		
	except Exception as e:
		print(str(e))
def Writing(path):
	content = []
	StateSet_List = ["m_listAttackStateData","m_listSkillStateData","m_listHyperSkillStateData","m_listHitCriticalFeedBack"]
	StateInfo_List = ["m_StateName"]
	StateInfo_Avoid_List = ["m_NKM_UNIT_STATE_TYPE"]
	state_index = 0
		
	unit_name = splitext(os.path.basename(path))[0]
	data = LoadData(path)
	if data:
		for k, v in data.items():
			if isinstance(v, list):
				for item in v: #?리스트니까 For문 돌려야됨
					if item:
						for i, j in item.items():
							if isinstance(j, list): #?리스트일 경우 스테이트 이벤트
								tag = "StateEvent"
								for item in j:
									if isinstance(item, dict):
										for x, y in item.items():
											content.append([unit_name,tag,k,state_index,i,j.index(item)+1,x,y])
									else:
										content.append([unit_name,tag,k,state_index,i,j.index(item)+1,item,None])
								continue
							elif k in StateSet_List: #?스테이트묶음 종류에 포함될 경우 스테이트묶음
								tag = "StateSet"
							else: #?나머지는 전부 스테이트 정보
								tag = "StateInfo"
							if i in StateInfo_List and k not in StateSet_List : state_index += 1 #! 인포셋에 걸리면 스테이트인덱스 증가
							if i in StateInfo_Avoid_List and k not in StateSet_List : continue
							content.append([unit_name,tag,k,state_index,None,0,i,j])
			else:
				tag = "BasicInfo"
				content.append([unit_name,tag,None,state_index,None,0,k,v])
	return content
def ExtractDamageTemplet(path):
	try:
		data = LoadData(path)
		my_file = 'UnitInfo/Damagetemplet.csv'
		f = open('temp.csv','w', newline='')
		writer = csv.writer(f)
		writer.writerow(["DTName","Key","Value"])
		state_index = 0
		for item in data:
			for k, v in item.items():
				if k == "m_DamageTempletName":
					DT_Name = v
				else:
					writer.writerow([DT_Name,k,v]) #?유닛 정보
		f.close()
		all_filenames = ["temp.csv", my_file]
		combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
		combined_csv = combined_csv.drop_duplicates(["DTName","Key","Value"])
		combined_csv.to_csv( my_file, index=False, encoding='utf-8-sig')
		os.remove("temp.csv")
	except Exception as e:
		print(str(e))
def ExtractDamageEffectTemplet(path):
	try:
		data = LoadData(path)
		my_file = 'UnitInfo/DamageEffectTemplet.csv'
		f = open('temp.csv','w', newline='')
		writer = csv.writer(f)
		writer.writerow(["EffectName","Tag","EventName","EventIndex","Key","Value"])
		this = ["DieEvent"]
		state_index = 0
		Effect_Name = None
		for item in data:
			for k, v in item.items():
				if k == "m_DamageEffectID":
					Effect_Name = v
					continue
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
												writer.writerow([Effect_Name,tag,i,j.index(item)+1,x,y])
										else:
											writer.writerow([Effect_Name,tag,k,0,i,item])
								else:
									if "DieEvent" in k:
										tag = "DieEvent"
										writer.writerow([Effect_Name,tag,k,0,i,j])
									else:
										tag = "StateInfo"
										writer.writerow([Effect_Name,tag,k,0,i,j])
				else:
					tag = "BasicInfo"
					writer.writerow([Effect_Name,tag,k,0,k,v])
		f.close()
		all_filenames = ["temp.csv", my_file]
		combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
		combined_csv = combined_csv.drop_duplicates(["EffectName","Tag","EventName","EventIndex","Key","Value"])
		combined_csv.to_csv( my_file, index=False, encoding='utf-8-sig')
		os.remove("temp.csv")
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

print("Extract Count :", len(UnitScript_Path))
ExtractUnitScript(UnitScript_Path,"Unit")
print("UnitScript ExtractDone.")

print("Extract Count :", len(ShipScript_Path))
ExtractUnitScript(ShipScript_Path,"Ship")
print("ShipScript ExtractDone.")

print("Extract Count :", len(MobScript_Path))
ExtractUnitScript(MobScript_Path,"Mob")
print("MobScript ExtractDone.")

print("Extract Count :", len(DamageEffectTemplet_Path))
for path in DamageEffectTemplet_Path:
	ExtractDamageEffectTemplet(path)
print("DamageEffectTemplet ExtractDone.")

print("Extract Count :", len(DamageTemplet_Path))
for path in DamageTemplet_Path:
	ExtractDamageTemplet(path)
print("DamageTemplet ExtractDone.")
print("All ExtractDone.")


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