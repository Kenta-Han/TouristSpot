import json
import random, string

def Randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

## 承認コード，乱数生成
def Random_Res():
    random_json = {"randomname":""}
    rand = Randomname(12)
    random_json["randomname"] = rand
    return random_json,rand

## 絶対的な特徴のjson形式整理
def Category_Res(cate):
    cate_json = []
    temp_sql_word = []
    sql_unvis,sql_vis,sql_word = [],[],""
    for i in range(len(cate)):
        response_catejson = {"cate_unspot":"","cate_vispot":"","cate_word":""}
        response_catejson["cate_unspot"] = cate[i][0]
        sql_unvis.append(cate[i][0])

        response_catejson["cate_vispot"] = cate[i][1]
        sql_vis.append(cate[i][1])

        temp = []
        word_list = []
        for j in range(len(cate[i][2])):
            try:
                word_list.append(cate[i][2][j][0])
                temp.append(cate[i][2][j][0])
            except TypeError:
                continue
        response_catejson["cate_word"] = word_list
        temp_sql_word.append(temp)

        for l in range(len(temp_sql_word)):
            tmp = "，".join(temp_sql_word[l]) + " -- "
            sql_word += tmp
        sql_word = sql_word[:-4]

        cate_json.append(response_catejson)
    return cate_json,sql_unvis,sql_vis,sql_word

##　メイン，相対的な特徴のjson形式整理
def Response(data,name,lat,lng,cate):
    random_json,rand = Random_Res()
    cate_json,sql_cate_unvis,sql_cate_vis,sql_cate_word = Category_Res(cate)

    all_json = []
    temp_sql_word = []
    sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word,sql_code = [],[],[],[],[],"",rand

    for i in range(len(data)):
        response_json = {"unvis_name":"","vis_name":"","cossim":"","unvis_lat":"","unvis_lng":"","word":""}

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

        all_json.append(response_json)

    all_json = [all_json] + [cate_json] + [random_json]
    print(json.dumps(all_json)) ## 送信

    for l in range(len(temp_sql_word)):
        tmp = "，".join(temp_sql_word[l]) + " -- "
        sql_word += tmp
    sql_word = sql_word[:-4]

    return sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word,sql_code,sql_cate_unvis,sql_cate_vis,sql_cate_word
