import sys
import collections
import numpy as np
import json

def Calculation(vis_name,vis_lat,vis_lng,unvis_name,unvis_lat,unvis_lng,data,color):
    max_cossim,min_cossim = max([i[2] for i in data]), min([i[2] for i in data])
    cluster = []
    visname_tmp = []
    json_data = []
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

        ## 最大値を1，最小値を0
        cossim = (data[i][2]-min_cossim) / (max_cossim-min_cossim)
        group.append(str(round(cossim,2))) ## cossim

        for j in range(len(color)):
            if color[j][0] == round(cossim,2):
                group.append(str(color[j][1]))

        word_list = []
        temp = []
        for j in range(len(data[i][3])):
            try:
                word_list.append(data[i][3][j][0])
            except TypeError:
                continue
        group.append(word_list)
        cluster.append(group)
        # response_json = Resp(group[0],group[1],group[2],group[3],group[4],group[5],group[6],group[7],group[8])
        # json_data.append(response_json)
    # print(json.dumps(json_data)) ## 送信


    ## 未訪問スポットと関連する既訪問スポットの数の多い順(降順)でソード
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

    ## 既訪問スポット座標変更
    for i in range(len(result)):
        if len(result[i]) > 1:
            sum_res_lat,sum_res_lng = 0, 0
            for j in range(len(result[i])):
                sum_res_lat = sum_res_lat + float(result[i][j][1])
                sum_res_lng = sum_res_lng + float(result[i][j][2])
            mean_res_lat = sum_res_lat / vis_list[i][1]
            mean_res_lng = sum_res_lng / vis_list[i][1]
            for j in range(len(result[i])):
                response_json = Resp(result[i][j][0],result[i][j][1],result[i][j][2],result[i][j][3],mean_res_lat,mean_res_lng,result[i][j][6],result[i][j][7],result[i][j][8])
                json_data.append(response_json)
        else:
            for j in range(len(result[i])):
                response_json = Resp(result[i][j][0],result[i][j][1],result[i][j][2],result[i][j][3],result[i][j][4],result[i][j][5],result[i][j][6],result[i][j][7],result[i][j][8])
                json_data.append(response_json)
    print(json.dumps(json_data)) ## 送信


def Resp(unvis,unlat,unlng,vis,vislat,vislng,cos,color,word):
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
