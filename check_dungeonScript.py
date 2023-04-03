from operator import indexOf
import luadata
import re
import csv
import pandas as pd
import os.path
import csvtodb

from ntpath import join
from os import listdir
from os.path import isfile, join, splitext, exists

if not os.path.isdir('UnitInfo'): os.mkdir('UnitInfo') #!폴더 없으면 생성
def LoadData(path):
	code = open(path,'r', encoding='utf-8-sig')
	lines = code.read()
	code.close()
	data = luadata.unserialize(lines,encoding='utf-8-sig')
	return data
def ExtractDungeonScript(path):
	content = []
	dungeon_name = ""
	# try:
	my_file = 'UnitInfo/DungeonScript.csv'
	column_list = ["1","2","3","4","5","6"]
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
	#!--------------------------------------------
	for p in path:
		content = []
		dungeon_name = splitext(os.path.basename(p))[0]
		# print(dungeon_name)
		data = LoadData(p)
		for x,y in data.items():
			if isinstance(y, list):
				for item in y:
					if isinstance(item, dict):
						for k,v in item.items():
							if isinstance (v, list):
								for vItem in v:
									if isinstance (vItem, dict):
										for i,j in vItem.items():
											content.append(["tag1",dungeon_name,x,k,i,j])
									else:
										content.append(["tag2",dungeon_name,x,k,vItem])
							else:
								content.append(["tag3",dungeon_name,x,None,k,v])
					else:
							content.append(["tag4",dungeon_name,None,None,x,y])
			elif isinstance(y, dict):
				for k,v in y.items():
					content.append(["tag6",dungeon_name,x,None,k,v])
			else:
				content.append(["tag5",dungeon_name,None,None,x,y])
			
			for item in content:
				writer.writerow(item)
		# continue
	#!--------------------------------------------
	f.close()
	
	all_filenames = ["temp.csv", my_file]
	combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
	# combined_csv = combined_csv.drop_duplicates(["BundleName","StateName","StateTime"])
	combined_csv.to_csv( my_file, index=False, encoding='utf-8-sig')
	os.remove("temp.csv")
	#! csvtodb.UpdateToDB('AnimData',column_list)
	# except Exception as e:
	# 	print(str(e))
	# 	print(dungeon_name)
