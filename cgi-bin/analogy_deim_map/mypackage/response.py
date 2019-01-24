# import json
import random, string

def Randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

## 承認コード，乱数生成
def Response_Random():
    random = Randomname(12)
    return random

##　相対的な特徴（差分ベクトルー調和平均）のjson形式整理
def Response_Harmonic(data,name,lat,lng,url):
    json_harmonic = []
    temp_sql_word = []
    sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word = [],[],[],[],[],""

    for i in range(len(data)):
        response_json = {"unvis_name":"","vis_name":"","cossim":"","unvis_lat":"","unvis_lng":"","word":"","unvis_url":""}
        #
        response_json["unvis_name"] = data[i][0]
        sql_unvis.append(data[i][0])

        response_json["vis_name"] = data[i][1]
        sql_vis.append(data[i][1])

        response_json["cossim"] = data[i][2]
        sql_cossim.append(str(data[i][2]))

        for k in range(len(name)):
            if data[i][0] == name[k]:
                response_json["unvis_lat"] = lat[k]
                sql_lat.append(lat[k])
                response_json["unvis_lng"] = lng[k]
                sql_lng.append(lng[k])
                response_json["unvis_url"] = url[k]

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

    return json_harmonic,sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word
