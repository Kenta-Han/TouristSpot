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

select_data = "SELECT * FROM analogy_imecs WHERE finish_datetime is not NULL;"
# select_data = "SELECT * FROM analogy_imecs WHERE id=19;"
all_data = Spot_List(select_data)

for i in range(len(all_data)):
    count_c,count_f,count_h,count_m = 0,0,0,0
    user_id = all_data[i][1]
    ## カテゴリー
    unfamiliar_group_c = re.split("，",all_data[i][6])
    familiar_group_c = re.split("，",all_data[i][7])
    c_set = Spot_Group(unfamiliar_group_c,familiar_group_c)
    word_c = re.split("--",all_data[i][8])
    ## 特徴ベクトル
    unfamiliar_group_f = re.split("，",all_data[i][9])
    familiar_group_f = re.split("，",all_data[i][10])
    f_set = Spot_Group(unfamiliar_group_f,familiar_group_f)
    cossim_f = re.split("，",all_data[i][11])
    word_f = re.split("--",all_data[i][12])
    ## 差分ベクトル(調和平均)
    unfamiliar_group_h = re.split("，",all_data[i][15])
    familiar_group_h = re.split("，",all_data[i][16])
    h_set = Spot_Group(unfamiliar_group_h,familiar_group_h)
    cossim_h = re.split("，",all_data[i][17])
    word_h = re.split("--",all_data[i][18])
    ## 差分ベクトル(相加平均)
    unfamiliar_group_m = re.split("，",all_data[i][15])
    familiar_group_m = re.split("，",all_data[i][16])
    m_set = Spot_Group(unfamiliar_group_m,familiar_group_m)
    cossim_m = re.split("，",all_data[i][17])
    word_m = re.split("--",all_data[i][21])

    ## 評価データ
    hyouka_data = re.split("，",all_data[i][22])
    hyouka_text_data = re.split("，",all_data[i][23])

    c,f,h,m = [],[],[],[]
    cs,fs,hs,ms = [],[],[],[]
    ct,ft,ht,mt = [],[],[],[]
    for k in range(len(hyouka_data)):
        hyouka = hyouka_data[k][-3]
        hyouka_text_set = re.split(" and ",hyouka_text_data[k])
        hyouka_text_set2 = re.split("[_：]",hyouka_text_set[1])
        hyouka_text = hyouka_text_set2[1]
        if hyouka == ("c" or "ct"):
            c.append(hyouka_data[k][:-4])
            cs.append(hyouka_data[k])
            ct.append(hyouka_text_data[k])
        elif hyouka == ("f" or "ft"):
            f.append(hyouka_data[k][:-4])
            fs.append(hyouka_data[k])
            ft.append(hyouka_text_data[k])
        elif hyouka == ("h" or "ht"):
            h.append(hyouka_data[k][:-4])
            hs.append(hyouka_data[k])
            ht.append(hyouka_text_data[k])
        elif hyouka == ("m" or "mt"):
            m.append(hyouka_data[k][:-4])
            ms.append(hyouka_data[k])
            mt.append(hyouka_text_data[k])

    ## カテゴリー
    if len(cs) != 0 :
        for j in range(len(c_set)):
            hyouka_set = re.split(" and ",cs[j])
            hyouka_set2 = re.split("[_：]",hyouka_set[1])
            unf = hyouka_set[0]
            fam = hyouka_set2[0]
            hyouka = hyouka_set2[2]

            hyouka_text_set = re.split(" and ",ct[j])
            hyouka_text_set2 = re.split("[_：]",hyouka_text_set[1])
            hyouka_text = hyouka_text_set2[2]

            num = c_set.index(c[j])

            way = "category"
            sql_insert = f"INSERT INTO analysis_analogy_imecs(user_id,way,hyouka,hyouka_text,unfamiliar,familiar,word,unfamiliar_group,familiar_group) VALUES('{user_id}','{way}','{hyouka}','{hyouka_text}','{unf}','{fam}','{word_c[num]}','{all_data[i][6]}','{all_data[i][7]}');"
            cur.execute(sql_insert)
            conn.commit()

    ## 特徴ベクトル
    for j in range(len(f_set)):
        hyouka_set = re.split(" and ",fs[j])
        hyouka_set2 = re.split("[_：]",hyouka_set[1])
        unf = hyouka_set[0]
        fam = hyouka_set2[0]
        hyouka = hyouka_set2[2]

        hyouka_text_set = re.split(" and ",ft[j])
        hyouka_text_set2 = re.split("[_：]",hyouka_text_set[1])
        hyouka_text = hyouka_text_set2[2]

        num = f_set.index(f[j])

        way = "feature"
        sql_insert = f"INSERT INTO analysis_analogy_imecs(user_id,way,hyouka,hyouka_text,unfamiliar,familiar,word,cossim,unfamiliar_group,familiar_group) VALUES('{user_id}','{way}','{hyouka}','{hyouka_text}','{unf}','{fam}','{word_f[num]}','{cossim_f[num]}','{all_data[i][9]}','{all_data[i][10]}');"
        cur.execute(sql_insert)
        conn.commit()

    ## 差分ベクトル(調和平均)
    for j in range(len(h_set)):
        hyouka_set = re.split(" and ",hs[j])
        hyouka_set2 = re.split("[_：]",hyouka_set[1])
        unf = hyouka_set[0]
        fam = hyouka_set2[0]
        hyouka = hyouka_set2[2]

        hyouka_text_set = re.split(" and ",ht[j])
        hyouka_text_set2 = re.split("[_：]",hyouka_text_set[1])
        hyouka_text = hyouka_text_set2[2]

        num = h_set.index(h[j])

        way = "harmonic"
        sql_insert = f"INSERT INTO analysis_analogy_imecs(user_id,way,hyouka,hyouka_text,unfamiliar,familiar,word,cossim,unfamiliar_group,familiar_group) VALUES('{user_id}','{way}','{hyouka}','{hyouka_text}','{unf}','{fam}','{word_h[num]}','{cossim_h[num]}','{all_data[i][15]}','{all_data[i][16]}');"
        cur.execute(sql_insert)
        conn.commit()

    ## 差分ベクトル(相加平均)
    for j in range(len(m_set)):
        hyouka_set = re.split(" and ",ms[j])
        hyouka_set2 = re.split("[_：]",hyouka_set[1])
        unf = hyouka_set[0]
        fam = hyouka_set2[0]
        hyouka = hyouka_set2[2]

        hyouka_text_set = re.split(" and ",mt[j])
        hyouka_text_set2 = re.split("[_：]",hyouka_text_set[1])
        hyouka_text = hyouka_text_set2[2]

        num = m_set.index(m[j])

        way = "mean"
        sql_insert = f"INSERT INTO analysis_analogy_imecs(user_id,way,hyouka,hyouka_text,unfamiliar,familiar,word,cossim,unfamiliar_group,familiar_group) VALUES('{user_id}','{way}','{hyouka}','{hyouka_text}','{unf}','{fam}','{word_m[num]}','{cossim_m[num]}','{all_data[i][15]}','{all_data[i][16]}');"
        cur.execute(sql_insert)
        conn.commit()
