import sys
import collections, copy
import numpy as np
import json, random
from scipy.stats import norm

def random_latlng(list, n, lat_s, lat_f, lng_s, lng_f):
    i = 0
    while i < n:
       list.append([random.uniform(lat_s, lat_f),random.uniform(lng_s, lng_f)])
       i += 1
    return list

def euclid_distance(x,t):
    return np.linalg.norm(x-t)

def normal_distribution(data,num=0):
    for i in range(len(data)):
        ## ランダム座標作成
        min_lat, max_lat = float(min([j[1] for j in data[i]]))-0.02, float(max([j[1] for j in data[i]]))+0.02
        min_lng, max_lng = float(min([j[2] for j in data[i]]))-0.02, float(max([j[2] for j in data[i]]))+0.02
        latlng = []
        rlatlng = random_latlng(latlng, 50, min_lat, max_lat, min_lng, max_lng)

        res = []
        for t_latlng in rlatlng:
            tmp = []
            for j in range(len(data[i])):
                cossim, average, alpha = data[i][j][6], 0, 700
                standard_deviation = (1 - abs(cossim)) * alpha
                x_latlng = np.array([float(data[i][j][1]),float(data[i][j][2])])
                dis = euclid_distance(x_latlng, t_latlng)
                P_xt = norm.pdf(dis, average, standard_deviation)
                # print("P_xt:{}\tcossim:{}".format(P_xt,cossim), file=sys.stderr)
                tmp.append(cossim * P_xt)
                # print(tmp, file=sys.stderr)
            res.append([t_latlng, sum(tmp)])
        # print("res_50:{}\n".format(res), file=sys.stderr)
        sortedRes = sorted(res, key=lambda x: x[1], reverse=True)
        # print("sorted_res_50:{}\n".format(sortedRes), file=sys.stderr)
        for j in range(len(data[i])):
            data[i][j][4] = str(sortedRes[0][0][0])
            data[i][j][5] = str(sortedRes[0][0][1])
    # print(data, file=sys.stderr)
    if num < 2:
        data = normal_distribution(data,num+1)
    return data

def select_and_resp_data(data,color):
    res, json_data = [], []
    ## 単語2つ以下切り捨て
    for i in range(len(data)):
        tmp = []
        for j in range(len(data[i])):
            if len(data[i][j][7]) >= 2:
                tmp.append(data[i][j])
        res.append(tmp)
    print("\nselect_data:{}".format(res), file=sys.stderr)
    ## 類似度に応じて色ずけ
    max_cossim = max([j[6] for i in res for j in i])
    min_cossim = min([j[6] for i in res for j in i])
    for i in range(len(res)):
        for j in range(len(res[i])):
            c = 0
            for k in range(len(color)):
                ## 正規化（最大値を1，最小値を0）
                cossim = (res[i][j][6] - min_cossim) / (max_cossim - min_cossim)
                if color[k][0] == round(cossim,2):
                    c = color[k][1]
            response_json = resp(res[i][j][0],res[i][j][1],res[i][j][2],res[i][j][3],res[i][j][4],res[i][j][5],res[i][j][6],c,res[i][j][7])
            json_data.append(response_json)
    print(json.dumps(json_data)) ## 送信

def resp(unvis,unlat,unlng,vis,vislat,vislng,cos,color,word):
    response_json = {"unvis_name":"","unvis_lat":"","unvis_lng":"","vis_name":"","vis_lat":"","vis_lng":"","cossim":"","color":"","word":""}
    response_json["unvis_name"] = unvis
    response_json["unvis_lat"] = unlat
    response_json["unvis_lng"] = unlng
    response_json["vis_name"] = vis
    response_json["vis_lat"] = vislat
    response_json["vis_lng"] = vislng
    response_json["cossim"] = cos
    response_json["color"] = color
    response_json["word"] = word
    return response_json

def calculation(vis_name,vis_lat,vis_lng,unvis_name,unvis_lat,unvis_lng,data,color):
    print(data ,file=sys.stderr)
    cluster, visname_tmp = [], []
    for i in range(len(data)):
        group = []
        group.append(data[i][0]) ## unvis_name

        for j in range(len(unvis_name)):
            if data[i][0] == unvis_name[j]:
                group.append(unvis_lat[j])
                group.append(unvis_lng[j])

        group.append(data[i][1]) ## vis_name

        visname_tmp.append(data[i][1])
        for j in range(len(vis_name)):
            if data[i][1] == vis_name[j]:
                group.append(vis_lat[j])
                group.append(vis_lng[j])

        group.append(data[i][2]) ## cossim

        word_list = []
        temp = []
        for j in range(len(data[i][3])):
            try:
                word_list.append(data[i][3][j][0])
            except TypeError:
                continue
        group.append(word_list) ## word
        cluster.append(group)

    vis_list = collections.Counter(visname_tmp).most_common()
    print(vis_list, file=sys.stderr)
    result = []
    for i in range(len(vis_list)):
        tmp = []
        for j in range(len(cluster)):
            if vis_list[i][0] == cluster[j][3]:
                tmp.append(cluster[j])
        result.append(tmp)
    print(result, file=sys.stderr)
    data = normal_distribution(result) ## 正規分布計算
    select_and_resp_data(data, color)
