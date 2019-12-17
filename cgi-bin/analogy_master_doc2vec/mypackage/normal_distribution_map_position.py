import sys
import collections, copy
import numpy as np
import json, random, string
from scipy.stats import norm
import datetime

import MySQLdb
import os, sys ## 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

def random_latlng(list, n, lat_s, lat_f, lng_s, lng_f):
    i = 0
    while i < n:
       list.append([random.uniform(lat_s, lat_f),random.uniform(lng_s, lng_f)])
       i += 1
    return list

def euclid_distance(x,t):
    return np.linalg.norm(x-t)

def normal_distribution(data):
    for i in range(len(data)):
        ## ランダム座標作成
        min_lat, max_lat = float(min([j[1] for j in data[i]]))-0.02, float(max([j[1] for j in data[i]]))+0.02
        min_lng, max_lng = float(min([j[2] for j in data[i]]))-0.02, float(max([j[2] for j in data[i]]))+0.02
        latlng = []
        rlatlng = random_latlng(latlng, 200, min_lat, max_lat, min_lng, max_lng)

        res = []
        for t_latlng in rlatlng:
            tmp = []
            for j in range(len(data[i])):
                cossim, average, alpha = data[i][j][7], 0, 1
                standard_deviation = (1 - abs(cossim)) * alpha
                x_latlng = np.array([float(data[i][j][1]),float(data[i][j][2])])
                dis = euclid_distance(x_latlng, t_latlng)
                P_xt = norm.pdf(dis, average, standard_deviation)
                if cossim < 0.65:
                    tmp.append(-0.5 * P_xt)
                elif cossim > 0.65:
                    tmp.append(1 * P_xt)
                else :
                    tmp.append(0)
            res.append([t_latlng, sum(tmp)])
        sortedRes = sorted(res, key=lambda x: x[1], reverse=True)
        for j in range(len(data[i])):
            data[i][j][5] = str(sortedRes[0][0][0])
            data[i][j][6] = str(sortedRes[0][0][1])
    return data

def select_and_resp_data(data,record_id,sql_unvis,sql_vis,sql_word):
    res, json_data = [], []
    ## 単語2つ以下切り捨て
    for i in range(len(data)):
        tmp = []
        for j in range(len(data[i])):
            if len(data[i][j][8]) >= 2:
                tmp.append(data[i][j])
        res.append(tmp)
    for i in range(len(res)):
        for j in range(len(res[i])):
            response_json = resp(record_id,res[i][j][0],res[i][j][1],res[i][j][2],res[i][j][3],res[i][j][4],res[i][j][5],res[i][j][6],res[i][j][7],res[i][j][8],sql_unvis,sql_vis,sql_word)
            json_data.append(response_json)
    return json_data

def resp(record_id,unvis,unlat,unlng,unurl,vis,vislat,vislng,cos,word,sql_unvis,sql_vis,sql_word):
    response_json = {"record_id":"","unvis_name":"","unvis_lat":"","unvis_lng":"","unvis_url":"","vis_name":"","vis_lat":"","vis_lng":"","cossim":"","word":""}
    response_json["record_id"] = record_id
    response_json["unvis_name"] = unvis
    response_json["unvis_lat"] = unlat
    response_json["unvis_lng"] = unlng
    response_json["unvis_url"] = unurl
    response_json["vis_name"] = vis
    response_json["vis_lat"] = vislat
    response_json["vis_lng"] = vislng
    response_json["cossim"] = cos
    response_json["word"] = word
    sql_insert = "UPDATE analogy_master_doc2vec SET unvis_name_map_position='{unv}',vis_name_map_position='{vis}',word_map_position='{word}' WHERE id = {record_id};".format(unv='，'.join(sql_unvis),vis='，'.join(sql_vis),word=sql_word,record_id=record_id)
    cur.execute(sql_insert)
    conn.commit()
    return response_json

def calculation(vis_name,vis_lat,vis_lng,unvis_name,unvis_lat,unvis_lng,data,record_id,unvis_url):
    cluster, visname_tmp = [], []
    sql_unvis, sql_vis, sql_word, temp_sql_word = [], [], "", []
    for i in range(len(data)):
        group = []
        group.append(data[i][0]) ## unvis_name
        sql_unvis.append(data[i][0])

        for j in range(len(unvis_name)):
            if data[i][0] == unvis_name[j]:
                group.append(unvis_lat[j])
                group.append(unvis_lng[j])
                group.append(unvis_url[j])

        group.append(data[i][1]) ## vis_name
        sql_vis.append(data[i][1])

        visname_tmp.append(data[i][1])
        for j in range(len(vis_name)):
            if data[i][1] == vis_name[j]:
                group.append(vis_lat[j])
                group.append(vis_lng[j])

        group.append(data[i][2]) ## cossim

        temp = []
        word_list = []
        for j in range(len(data[i][3])):
            try:
                word_list.append(data[i][3][j][0])
                temp.append(data[i][3][j][0])
            except TypeError:
                continue
        group.append(word_list) ## word
        temp_sql_word.append(word_list)
        cluster.append(group)

    for l in range(len(temp_sql_word)):
        tmp = "，".join(temp_sql_word[l]) + "--"
        sql_word += tmp
    sql_word = sql_word[:-2]

    vis_list = collections.Counter(visname_tmp).most_common()
    # print(vis_list, file=sys.stderr)
    result = []
    for i in range(len(vis_list)):
        tmp = []
        for j in range(len(cluster)):
            if vis_list[i][0] == cluster[j][4]:
                tmp.append(cluster[j])
        result.append(tmp)
    # print(result, file=sys.stderr)
    data = normal_distribution(result) ## 正規分布計算
    json_data = select_and_resp_data(data, record_id, sql_unvis, sql_vis, sql_word)
    return json_data
