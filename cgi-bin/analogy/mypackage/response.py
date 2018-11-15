import json
import random, string

def Randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

def Response(data,name,lat,lng):
    all_json = []
    temp_sql_word = []
    sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word,sql_code = [],[],[],[],[],"",[]
    for i in range(len(data)):
        response_json={"unvis_name":"","vis_name":"","cossim":"","unvis_lat":"","unvis_lng":"","word":"","randomname":""}

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

        rand = Randomname(12)
        response_json["randomname"] = rand
        sql_code.append(rand)

        all_json.append(response_json)
    print(json.dumps(all_json)) ## 送信

    for l in range(len(temp_sql_word)):
        tmp = "，".join(temp_sql_word[l]) + " -- "
        sql_word += tmp
    sql_word = sql_word[:-3]

    return sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word,sql_code[0]
