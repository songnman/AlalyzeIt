from ast import For
import mariadb
import sys
import pandas as pd

def UpdateToDB(my_file_name,column_list):
    column_list_format = []
    for i in range(len(column_list)):
        column_list_format.append('%s')
    column_list_format = ','.join(column_list_format)
    column_list = '`'+'`,`'.join(column_list)+'`'
    
    try:
        for line in open("d:\\accountfile.txt","r").readlines():
            login_info = line.split()
        conn = mariadb.connect(
            user=login_info[0],
            password=login_info[1],
            host=login_info[2],
            port=int(login_info[3]),
            database=login_info[4]
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    cur = conn.cursor() #! Get Cursor
    df = pd.read_csv(f'UnitInfo/{my_file_name}.csv') #! Get DataFrame
    item = df.astype(str)  #!STRING으로 변경
    db_itemlist = item.values.tolist() #!  DataFrame to List
    try:
        cur.execute(f"TRUNCATE {my_file_name}")
        insert_query = f"INSERT INTO {my_file_name} ({column_list}) VALUES ({column_list_format})"
        cur.executemany(insert_query,db_itemlist)
        conn.commit()
        conn.close()
    except mariadb.Error as e:
        print(f"Error: {e}")