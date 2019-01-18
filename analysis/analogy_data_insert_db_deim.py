#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import MySQLdb
import re

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

## index_analogy.html 解析用
## DBのanalysis_analogyにデータを挿入

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

select_data = "SELECT * FROM analogy_deim WHERE finish_datetime is not NULL;"
# select_data = "SELECT * FROM analogy_imecs WHERE id=19;"
all_data = Spot_List(select_data)

for i in range(len(all_data)):
    count_c,count_f,count_h,count_m = 0,0,0,0
    user_id = all_data[i][1]
    unfamiliar_group = re.split("，",all_data[i][6])
    familiar_group = re.split("，",all_data[i][7])
    cossim = re.split("，",all_data[i][8])
    spot_set = Spot_Group(unfamiliar_group,familiar_group)
    word_m = re.split("--",all_data[i][11])
    word_k = re.split("--",all_data[i][12])
    word_h = re.split("--",all_data[i][13])

    ## 評価データ
    hyouka_data = re.split("，",all_data[i][14])
    hyouka_text_data = re.split("，",all_data[i][15])

    m,k,h = [],[],[]
    ms,ks,hs = [],[],[]
    mt,kt,ht = [],[],[]
    for j in range(len(hyouka_data)):
        hyouka = hyouka_data[j][-3]
        hyouka_text_set = re.split(" and ",hyouka_text_data[j])
        hyouka_text_set2 = re.split("[_：]",hyouka_text_set[1])
        hyouka_text = hyouka_text_set2[1]
        if hyouka == ("m" or "mt"):
            m.append(hyouka_data[j][:-4])
            ms.append(hyouka_data[j])
            mt.append(hyouka_text_data[j])
        elif hyouka == ("k" or "kt"):
            k.append(hyouka_data[j][:-4])
            ks.append(hyouka_data[j])
            kt.append(hyouka_text_data[j])
        elif hyouka == ("h" or "ht"):
            h.append(hyouka_data[j][:-4])
            hs.append(hyouka_data[j])
            ht.append(hyouka_text_data[j])

    for j in range(len(spot_set)):
        hyouka_set = re.split(" and ",ms[j])
        hyouka_set2 = re.split("[_：]",hyouka_set[1])
        unf = hyouka_set[0]
        fam = hyouka_set2[0]
        hyouka = hyouka_set2[2]

        hyouka_text_set = re.split(" and ",mt[j])
        hyouka_text_set2 = re.split("[_：]",hyouka_text_set[1])
        print(hyouka_text_set2)
        hyouka_text = hyouka_text_set2[2]

        num = spot_set.index(m[j])

        way = "mean"
        sql_insert = f"INSERT INTO analysis_analogy_deim(user_id,way,hyouka,hyouka_text,unfamiliar,familiar,word,cossim,unfamiliar_group,familiar_group) VALUES('{user_id}','{way}','{hyouka}','{hyouka_text}','{unf}','{fam}','{word_m[num]}','{cossim[num]}','{all_data[i][6]}','{all_data[i][7]}');"
        cur.execute(sql_insert)
        conn.commit()

    for j in range(len(spot_set)):
        hyouka_set = re.split(" and ",ks[j])
        hyouka_set2 = re.split("[_：]",hyouka_set[1])
        unf = hyouka_set[0]
        fam = hyouka_set2[0]
        hyouka = hyouka_set2[2]

        hyouka_text_set = re.split(" and ",kt[j])
        hyouka_text_set2 = re.split("[_：]",hyouka_text_set[1])
        print(hyouka_text_set2)
        hyouka_text = hyouka_text_set2[2]

        num = spot_set.index(k[j])

        way = "multi"
        sql_insert = f"INSERT INTO analysis_analogy_deim(user_id,way,hyouka,hyouka_text,unfamiliar,familiar,word,cossim,unfamiliar_group,familiar_group) VALUES('{user_id}','{way}','{hyouka}','{hyouka_text}','{unf}','{fam}','{word_k[num]}','{cossim[num]}','{all_data[i][6]}','{all_data[i][7]}');"
        cur.execute(sql_insert)
        conn.commit()

    for j in range(len(spot_set)):
        hyouka_set = re.split(" and ",hs[j])
        hyouka_set2 = re.split("[_：]",hyouka_set[1])
        unf = hyouka_set[0]
        fam = hyouka_set2[0]
        hyouka = hyouka_set2[2]

        hyouka_text_set = re.split(" and ",ht[j])
        hyouka_text_set2 = re.split("[_：]",hyouka_text_set[1])
        print(hyouka_text_set2)
        hyouka_text = hyouka_text_set2[2]

        num = spot_set.index(h[j])

        way = "harmonic"
        sql_insert = f"INSERT INTO analysis_analogy_deim(user_id,way,hyouka,hyouka_text,unfamiliar,familiar,word,cossim,unfamiliar_group,familiar_group) VALUES('{user_id}','{way}','{hyouka}','{hyouka_text}','{unf}','{fam}','{word_h[num]}','{cossim[num]}','{all_data[i][6]}','{all_data[i][7]}');"
        cur.execute(sql_insert)
        conn.commit()
