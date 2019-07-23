import json
import random, string

##　相対的な特徴（差分ベクトルー調和平均）のjson形式整理
def Response_Harmonic(data,name,lat,lng,url,description):
    json_harmonic = []
    temp_sql_word = []
    sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word = [],[],[],[],[],""

    for i in range(len(data)):
        response_json = {"unvis_name":"","vis_name":"","cossim":"","unvis_lat":"","unvis_lng":"","word":"","unvis_url":"","unvis_description":""}

        response_json["unvis_name"] = data[i][0]
        sql_unvis.append(data[i][0])

        response_json["vis_name"] = data[i][1]
        sql_vis.append(data[i][1])

        response_json["cossim"] = round(data[i][2],2)
        sql_cossim.append(str(data[i][2]))

        for k in range(len(name)):
            if data[i][0] == name[k]:
                response_json["unvis_lat"] = lat[k]
                sql_lat.append(lat[k])
                response_json["unvis_lng"] = lng[k]
                sql_lng.append(lng[k])
                response_json["unvis_url"] = url[k]
                response_json["unvis_description"] = description[k]

        word_list = []
        temp = []
        for j in range(len(data[i][3])):
            try:
                word_list.append(data[i][3][j][0])
                temp.append(data[i][3][j][0])
            except TypeError:
                continue
        response_json["word"] = word_list
        temp_sql_word.append(temp)

        json_harmonic.append(response_json)

    for l in range(len(temp_sql_word)):
        tmp = "，".join(temp_sql_word[l]) + "--"
        sql_word += tmp
    sql_word = sql_word[:-2]

    print(json.dumps(json_harmonic)) ## 送信

    return sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word


def Response(vis_name,vis_lat,vis_lng,vis_url,vis_description,unvis_name,unvis_lat,unvis_lng,unvis_url,unvis_description,data):
    json_vis, json_unvis = [], []
    response = {"nodes":[],"links":[]}
    for i in range(len(vis_name)):
        response_nodes = {"id":"","group":"","memo":"","lat":"","lng":""}
        response_nodes["id"] = vis_name[i]
        response_nodes["group"] = "1"
        response_nodes["memo"] = vis_description[i]
        response_nodes["lat"] = vis_lat[i]
        response_nodes["lng"] = vis_lng[i]
        json_vis.append(response_nodes)

    for i in range(len(unvis_name)):
        response_nodes = {"id":"","group":"","memo":"","lat":"","lng":""}
        response_nodes["id"] = unvis_name[i]
        response_nodes["group"] = "2"
        response_nodes["memo"] = unvis_description[i]
        response_nodes["lat"] = unvis_lat[i]
        response_nodes["lng"] = unvis_lng[i]
        json_unvis.append(response_nodes)

    json_data = []
    for i in range(len(data)):
        response_links = {"source":"","target":"","value":"","word":""}
        response_links["source"] = data[i][0] ##未訪問
        response_links["target"] = data[i][1] ##既訪問
        response_links["value"] = math.floor(data[i][2],2) ##類似度

        word_list = []
        temp = []
        for j in range(len(data[i][3])):
            try:
                word_list.append(data[i][3][j][0])
                temp.append(data[i][3][j][0])
            except TypeError:
                continue
        response_links["word"] = word_list
        json_data.append(response_links)
    response["nodes"] = json_vis + json_unvis
    response["links"] = json_data
    print(json.dumps(response)) ## 送信
