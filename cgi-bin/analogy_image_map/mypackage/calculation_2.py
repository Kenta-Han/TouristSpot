import sys
import collections, copy
import numpy as np
import json

def Calculation(vis_name,vis_lat,vis_lng,unvis_name,unvis_lat,unvis_lng,data,color):
    print(data ,file=sys.stderr)
    # max_cossim,min_cossim = max([i[2] for i in data]), min([i[2] for i in data])
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

        # group.append(str(rounsd(data[i][2],2))) ## cossim
        group.append(data[i][2]) ## cossim

        word_list = []
        temp = []
        for j in range(len(data[i][3])):
            try:
                word_list.append(data[i][3][j][0])
            except TypeError:
                continue
        group.append(word_list)
        cluster.append(group)

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

    result_tmp = copy.copy(result)
    for i in range(len(result)):
        max_spot, min_spot = result_tmp[i][0], result_tmp[i][-1]
        if max_spot == min_spot:
            result[i][0][4] = result[i][0][1]
            result[i][0][5] = str(float(result[i][0][2]) + (1-result[i][0][6])/100)
            # continue
        else:
            print("\nmax_spot:{}\nmin_spot:{}".format(max_spot,min_spot),file=sys.stderr)
            max_spot_latlng = np.array([float(max_spot[1]),float(max_spot[2])])
            min_spot_latlng = np.array([float(min_spot[1]),float(min_spot[2])])
            print("max_spot_latlng:{}\nmin_spot_latlng:{}".format(max_spot_latlng,min_spot_latlng) ,file=sys.stderr)
            tmp = (max_spot_latlng * max_spot[6] + min_spot_latlng * min_spot[6]) / (max_spot[6] + min_spot[6])
            print("new_latlng:{}".format(tmp), file=sys.stderr)
            result_tmp[i][0][4] = str(tmp[0])
            result_tmp[i][0][5] = str(tmp[1])
            result_tmp[i].pop(-1)

            next_target = []
            next_target.extend([result_tmp[i][j] for j in range(len(result_tmp[i])) if np.all((max_spot_latlng-0.02) <= np.array([float(result_tmp[i][j][1]),float(result_tmp[i][j][2])])) and np.all(np.array([float(result_tmp[i][j][1]),float(result_tmp[i][j][2])])<=(max_spot_latlng+0.02))])
            next_target.pop(0)

            if len(next_target) != 0:
                for j in range(len(next_target)):
                    print(len(next_target), file=sys.stderr)
                    print("next_target:{}".format(next_target), file=sys.stderr)
                    if len(next_target) != 0:
                        print(float(next_target[j][1]), file=sys.stderr)
                        print(float(next_target[j][2]), file=sys.stderr)
                        next_target_latlng = np.array([float(next_target[j][1]),float(next_target[j][2])])
                        tmp2 = (max_spot_latlng * max_spot[6] + next_target_latlng * next_target[j][6]) / (max_spot[6] + next_target[j][6])
                        print("new_latlng:{}".format(tmp2), file=sys.stderr)
                        # next_target.pop(0)
                        for k in range(len(result[i])):
                            result[i][k][4] = str(tmp2[0])
                            result[i][k][5] = str(tmp2[1])
            else:
                for k in range(len(result[i])):
                    result[i][k][4] = result_tmp[i][0][4]
                    result[i][k][5] = result_tmp[i][0][5]
    print("\nresult:{}".format(result), file=sys.stderr)

    new_group = []
    for i in range(len(result)):
        tmp = []
        for j in range(len(result[i])):
            if result[i][j][6] > 0.1:
                tmp.append(result[i][j])
        new_group.append(tmp)
    max_cossim = max([j[6] for i in new_group for j in i])
    min_cossim = min([j[6] for i in new_group for j in i])
    print(new_group, file=sys.stderr)
    for i in range(len(new_group)):
        for j in range(len(new_group[i])):
            c = 0
            for k in range(len(color)):
                ## 最大値を1，最小値を0
                cossim = (new_group[i][j][6] - min_cossim) / (max_cossim - min_cossim)
                if color[k][0] == round(cossim,2):
                    c = color[k][1]
            response_json = Resp(new_group[i][j][0],new_group[i][j][1],new_group[i][j][2],new_group[i][j][3],new_group[i][j][4],new_group[i][j][5],new_group[i][j][6],c,new_group[i][j][7])
            print(response_json, file=sys.stderr)
            json_data.append(response_json)
    print(json_data, file=sys.stderr)
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
