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
        response_catejson = {"unvis_name":"","vis_name":"","word":"","label":"c","unvis_url":""}
        response_catejson["unvis_name"] = cate[i][0]
        sql_unvis.append(cate[i][0])

        response_catejson["vis_name"] = cate[i][1]
        sql_vis.append(cate[i][1])

        temp = []
        word_list = []
        for j in range(len(cate[i][2])):
            try:
                word_list.append(cate[i][2][j][0])
                temp.append(cate[i][2][j][0])
            except TypeError:
                continue
        response_catejson["word"] = word_list
        temp_sql_word.append(temp)

        response_catejson["unvis_url"] = cate[i][3]

        json_category.append(response_catejson)

    for l in range(len(temp_sql_word)):
        tmp = "，".join(temp_sql_word[l]) + "--"
        sql_word += tmp
    sql_word = sql_word[:-2]

    return sql_unvis,sql_vis,sql_word,json_category

##　絶対的な特徴（特徴ベクトル）のjson形式整理
def Response_Feature(data,name,lat,lng,url):
    json_feature = []
    temp_sql_word = []
    sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word = [],[],[],[],[],""

    for i in range(len(data)):
        response_json = {"unvis_name":"","vis_name":"","cossim":"","unvis_lat":"","unvis_lng":"","word":"","label":"f","unvis_url":""}

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

        json_feature.append(response_json)

    for l in range(len(temp_sql_word)):
        tmp = "，".join(temp_sql_word[l]) + "--"
        sql_word += tmp
    sql_word = sql_word[:-2]

    return sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word,json_feature

##　相対的な特徴（差分ベクトルー調和平均）のjson形式整理
def Response_Harmonic(data,name,lat,lng,url):
    json_harmonic = []
    temp_sql_word = []
    sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word = [],[],[],[],[],""

    for i in range(len(data)):
        response_json = {"unvis_name":"","vis_name":"","cossim":"","unvis_lat":"","unvis_lng":"","word":"","label":"h","unvis_url":""}

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

    return sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word,json_harmonic

##　相対的な特徴（差分ベクトルー相加平均）のjson形式整理
def Response_Mean(data,name,url):
    json_mean = []
    temp_sql_word = []
    sql_word = ""

    for i in range(len(data)):
        response_json = {"unvis_name":"","vis_name":"","cossim":"","word":"","label":"m","unvis_url":""}

        response_json["unvis_name"] = data[i][0]
        response_json["vis_name"] = data[i][1]
        response_json["cossim"] = data[i][2]

        for k in range(len(name)):
            if data[i][0] == name[k]:
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

        json_mean.append(response_json)

    for l in range(len(temp_sql_word)):
        tmp = "，".join(temp_sql_word[l]) + "--"
        sql_word += tmp
    sql_word = sql_word[:-2]

    return sql_word,json_mean

def Response(category,feature,harmonic,mean,random,record_id):
    record = {"record_id":""}
    record["record_id"] = record_id
    spot_json = category
    spot_json.extend(feature)
    spot_json.extend(harmonic)
    spot_json.extend(mean)
    spot_json.sort(key=lambda x:x.get("unvis_name"),reverse=True)
    all_json = []
    all_json = [spot_json] + [random] + [record]
    print(json.dumps(all_json)) ## 送信
