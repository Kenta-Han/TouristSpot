import json
import random, string

def Randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

## 承認コード，乱数生成
def Response_Random():
    json_random = {"randomname":""}
    random = Randomname(12)
    json_random["randomname"] = random
    return random,json_random

## 絶対的な特徴（カテゴリ）のjson形式整理
def Response_Category(cate):
    json_category = []
    temp_sql_word = []
    sql_unvis,sql_vis,sql_word = [],[],""
    for i in range(len(cate)):
        response_catejson = {"unvis_name_c":"","vis_name_c":"","word_c":""}
        response_catejson["unvis_name_c"] = cate[i][0]
        sql_unvis.append(cate[i][0])

        response_catejson["vis_name_c"] = cate[i][1]
        sql_vis.append(cate[i][1])

        temp = []
        word_list = []
        for j in range(len(cate[i][2])):
            try:
                word_list.append(cate[i][2][j][0])
                temp.append(cate[i][2][j][0])
            except TypeError:
                continue
        response_catejson["word_c"] = word_list
        temp_sql_word.append(temp)

        for l in range(len(temp_sql_word)):
            tmp = "，".join(temp_sql_word[l]) + " -- "
            sql_word += tmp
        sql_word = sql_word[:-4]

        json_category.append(response_catejson)
    return sql_unvis,sql_vis,sql_word,json_category

##　絶対的な特徴（特徴ベクトル）のjson形式整理
def Response_Vector_Feature(data,name,lat,lng):
    json_feature = []
    temp_sql_word = []
    sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word = [],[],[],[],[],""

    for i in range(len(data)):
        response_json = {"unvis_name_f":"","vis_name_f":"","cossim_f":"","unvis_lat_f":"","unvis_lng_f":"","word_f":""}

        response_json["unvis_name_f"] = data[i][0]
        sql_unvis.append(data[i][0])

        response_json["vis_name_f"] = data[i][1]
        sql_vis.append(data[i][1])

        response_json["cossim_f"] = data[i][2]
        sql_cossim.append(str(data[i][2]))

        for k in range(len(name)):
            if data[i][0] == name[k]:
                response_json["unvis_lat_f"] = lat[k]
                sql_lat.append(lat[k])
                response_json["unvis_lng_f"] = lng[k]
                sql_lng.append(lng[k])

        word_list = []
        temp = []
        for j in range(len(data[i][3])):
            try:
                word_list.append(data[i][3][j][0])
                temp.append(data[i][3][j][0])
            except TypeError:
                continue
        response_json["word_f"] = word_list
        temp_sql_word.append(temp)

        json_feature.append(response_json)

    for l in range(len(temp_sql_word)):
        tmp = "，".join(temp_sql_word[l]) + " -- "
        sql_word += tmp
    sql_word = sql_word[:-4]

    return sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word,json_feature


##　相対的な特徴（差分ベクトル）のjson形式整理
def Response_Vector(data,name,lat,lng):
    json_vector = []
    temp_sql_word = []
    sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word = [],[],[],[],[],""

    for i in range(len(data)):
        response_json = {"unvis_name_v":"","vis_name_v":"","cossim_v":"","unvis_lat_v":"","unvis_lng_v":"","word_v":""}

        response_json["unvis_name_v"] = data[i][0]
        sql_unvis.append(data[i][0])

        response_json["vis_name_v"] = data[i][1]
        sql_vis.append(data[i][1])

        response_json["cossim_v"] = data[i][2]
        sql_cossim.append(str(data[i][2]))

        for k in range(len(name)):
            if data[i][0] == name[k]:
                response_json["unvis_lat_v"] = lat[k]
                sql_lat.append(lat[k])
                response_json["unvis_lng_v"] = lng[k]
                sql_lng.append(lng[k])

        word_list = []
        temp = []
        for j in range(len(data[i][3])):
            try:
                word_list.append(data[i][3][j][0])
                temp.append(data[i][3][j][0])
            except TypeError:
                continue
        response_json["word_v"] = word_list
        temp_sql_word.append(temp)

        json_vector.append(response_json)

    for l in range(len(temp_sql_word)):
        tmp = "，".join(temp_sql_word[l]) + " -- "
        sql_word += tmp
    sql_word = sql_word[:-4]

    return sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word,json_vector

def Response(category,feature,vector,random,record_id):
    json_record = {"record_id":""}
    json_record["record_id"] = record_id
    all_json = []
    all_json = [category] + [feature] + [vector] + [random] + [json_record]
    print(json.dumps(all_json)) ## 送信
