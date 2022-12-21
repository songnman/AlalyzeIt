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
def ExtractAnimData(path):
	content = []
	try:
		my_file = 'UnitInfo/AnimData.csv'
		column_list = ["BundleName","AnimName","StateName","StateTime"]
		if not exists(my_file):
			f = open(my_file,'w', newline='')
			writer = csv.writer(f)
			writer.writerow(column_list)
			f.close()
		
		if exists("temp.csv"):
			os.remove("temp.csv")
		f = open('temp.csv','w', newline='')
		
		
		#!--------------------------------------------
		writer = csv.writer(f)
		writer.writerow(column_list)
		data = LoadData(path)
		
		for item in data:
			animName = item["animName"]
			del item["animName"]
			bundleName = item["bundleName"]
			del item["bundleName"]
			
			for k, v in item.items():
				content.append([animName,bundleName,v[0],v[1]])
			
			for item in content:
				writer.writerow(item)
		#!--------------------------------------------
		
		f.close()
		
		all_filenames = ["temp.csv", my_file]
		combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
		combined_csv = combined_csv.drop_duplicates(["BundleName","StateName","StateTime"])
		combined_csv.to_csv( my_file, index=False, encoding='utf-8-sig')
		os.remove("temp.csv")
		csvtodb.UpdateToDB('AnimData',column_list)
	except Exception as e:
		print(str(e))
