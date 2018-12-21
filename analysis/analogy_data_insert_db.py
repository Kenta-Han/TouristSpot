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

select_data = "SELECT * FROM analogy WHERE finish_datetime is not NULL;"
all_data = Spot_List(select_data)

# print(len(all_data))

for i in range(len(all_data)):
    count_c,count_f,count_h,count_m = 0,0,0,0
    user_id = all_data[i][1]
    ## カテゴリー
    unfamiliar_group_c = all_data[i][6]
    familiar_group_c = all_data[i][7]
    word_c = re.split("--",all_data[i][8])
    ## 特徴ベクトル
    unfamiliar_group_f = all_data[i][9]
    familiar_group_f = all_data[i][10]
    cossim_f = re.split("，",all_data[i][11])
    word_f = re.split("--",all_data[i][12])
    ## 差分ベクトル(調和平均)
    unfamiliar_group_h = all_data[i][15]
    familiar_group_h = all_data[i][16]
    cossim_h = re.split("，",all_data[i][17])
    word_h = re.split("--",all_data[i][18])
    ## 差分ベクトル(相加平均)
    unfamiliar_group_m = all_data[i][15]
    familiar_group_m = all_data[i][16]
    cossim_m = re.split("，",all_data[i][17])
    word_m = re.split("--",all_data[i][21])

    ## 評価データ
    hyouka_data = re.split("，",all_data[i][22])
    hyouka_text_data = re.split("，",all_data[i][23])

    for j in range(len(hyouka_data)):
        hyouka_set = re.split(" and ",hyouka_data[j])
        hyouka_set2 = re.split("[_：]",hyouka_set[1])

        unfamiliar = hyouka_set[0]
        familiar = hyouka_set2[0]

        hyouka_text_set = re.split(" and ",hyouka_text_data[j])
        hyouka_text_set2 = re.split("[_：]",hyouka_text_set[1])

        hyouka = hyouka_set2[2]
        hyouka_text = hyouka_text_set2[2]

        if hyouka_set2[1] == "c":
            way = "category"
            sql_insert = f"INSERT INTO analysis_analogy(user_id,way,unfamiliar_group,familiar_group,hyouka,unfamiliar,familiar,hyouka_text,word) VALUES('{user_id}','{way}','{unfamiliar_group_c}','{familiar_group_c}',{hyouka},'{unfamiliar}','{familiar}','{hyouka_text}','{word_c[count_c]}');"
            cur.execute(sql_insert)
            conn.commit()
            count_c += 1

        elif hyouka_set2[1] == "f":
            way = "feature"
            sql_insert = f"INSERT INTO analysis_analogy(user_id,way,unfamiliar_group,familiar_group,hyouka,unfamiliar,familiar,hyouka_text,word,cossim) VALUES('{user_id}','{way}','{unfamiliar_group_f}','{familiar_group_f}',{hyouka},'{unfamiliar}','{familiar}','{hyouka_text}','{word_f[count_f]}',{cossim_f[count_f]});"
            cur.execute(sql_insert)
            conn.commit()
            count_f += 1

        elif hyouka_set2[1] == "h":
            way = "harmonic"
            sql_insert = f"INSERT INTO analysis_analogy(user_id,way,unfamiliar_group,familiar_group,hyouka,unfamiliar,familiar,hyouka_text,word,cossim) VALUES('{user_id}','{way}','{unfamiliar_group_h}','{familiar_group_h}',{hyouka},'{unfamiliar}','{familiar}','{hyouka_text}','{word_h[count_h]}',{cossim_h[count_h]});"
            cur.execute(sql_insert)
            conn.commit()
            count_h += 1

        ## ## 挿入プログラムに問題あり，手動で修正，hyouka=0の部分は単語が入った SELECT * from analysis_analogy where hyouka=0 or word = "";
        elif hyouka_set2[1] == "m":
            way = "mean"
            sql_insert = f"INSERT INTO analysis_analogy(user_id,way,unfamiliar_group,familiar_group,hyouka,unfamiliar,familiar,hyouka_text,word,cossim) VALUES('{user_id}','{way}','{unfamiliar_group_m}','{familiar_group_m}',{hyouka},'{unfamiliar}','{familiar}','{hyouka_text}','{word_m[count_m]}',{cossim_m[count_m]});"
            cur.execute(sql_insert)
            conn.commit()
            count_m += 1
