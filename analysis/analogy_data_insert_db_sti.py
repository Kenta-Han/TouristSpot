#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import MySQLdb
import re

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

## analogy_image_map.html 解析用
## DBのanalysis_analogy_stiにデータを挿入

def Spot_List(select_spot):
    spot_list = []
    cur.execute(select_spot)
    for i in cur:
        spot_list.append(i)
    return spot_list

def Spot_Group(unf,fam):
    result = []
    for j in range(len(unf)):
        result.extend([unf[j] + " and " + fam[j]])
    return result

select_data = "SELECT * FROM analogy_sti WHERE finish_datetime is not NULL;"
all_data = Spot_List(select_data)

# print(all_data)

for i in range(len(all_data)):
    user_id = all_data[i][1]

    unfamiliar_group = re.split("，",all_data[i][6])
    familiar_group = re.split("，",all_data[i][7])
    spot_set = Spot_Group(unfamiliar_group,familiar_group)
    word = re.split("--",all_data[i][8])

    for j in range(len(spot_set)):
        unf = unfamiliar_group[j]
        fam = familiar_group[j]
        wo = word[j]
        sql_insert = f"INSERT INTO analysis_analogy_sti(user_id,unfamiliar,familiar,word,unfamiliar_group,familiar_group) VALUES('{user_id}','{unf}','{fam}','{wo}','{all_data[i][6]}','{all_data[i][7]}')"
        cur.execute(sql_insert)
        conn.commit()
