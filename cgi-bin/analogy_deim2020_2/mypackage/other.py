import MySQLdb
import os, sys # 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
import copy
conn,cur = jalan_ktylab_new.main()

## 履歴スポットリスト作成(DBでLIKE検索するため)
def make_history_list(history):
    all = []
    spot = []
    area = []
    for i in range(len(history)):
        temp = "%"+ history[i] +"%"
        all.append(temp)
        temp = 0
    spot.append(all[0::2])
    area.append(all[1::2])
    return spot,area

## スポット，レビューリスト作成
def spot_or_reviewlist(spot):
    spot_list = []
    cur.execute(spot)
    for i in cur:
        spot_list.append([i])
    return spot_list

## エリアIDリスト作成
def area_id_list(area):
    area_id_list = []
    cur.execute(area)
    for i in cur:
        area_id_list.append(i[0])
    return area_id_list

## ajaxデータ整形（tfidf_vis_data用）
def stringlist_changeto_clusterset(word):
    numlist = [i for i, x in enumerate(word) if x == '-finish-']

    res = []
    for j in range(len(numlist)):
        if j == 0:
            res.append(word[:numlist[j]])
        else:
            tmp = []
            tmp.extend(word[numlist[j-1]+1:numlist[j]])
            res.append(tmp)

    result = []
    for i in range(len(res)):
        num = copy.copy(res[i][0])
        res[i].pop(0)
        tfidf_dic = []
        for x,y in zip(*[iter(res[i])]*2):
            tfidf_dic.append([x,float(y)])
        result.append([num,tfidf_dic])

    return result

## ajaxデータ整形（vis_score_dic用）
def stringlist_changeto_visscoreset(word):
    numlist = [i for i, x in enumerate(word) if x == '-finish-']

    res = []
    for j in range(len(numlist)):
        if j == 0:
            res.append(word[:numlist[j]])
        else:
            tmp = []
            tmp.extend(word[numlist[j-1]+1:numlist[j]])
            res.append(tmp)

    result = []
    for i in range(len(res)):
        num = copy.copy(res[i][0])
        score = copy.copy(res[i][1])
        res[i].pop(0)
        res[i].pop(0)
        review_id = []
        for j in range(len(res[i])):
            review_id.append(int(res[i][j]))
        result.append([num,float(score),review_id])
    return result

## review_vectorsのリスト作成(review_idつき)
def review_id_and_vectors_list(id):
    review_id_and_vectors_list = []
    cur.execute(id)
    for i in cur:
        review_id_and_vectors_list.append([i[0],list(i[1:-2])])
    return review_id_and_vectors_list

# ## ajaxデータ整形（vis_center_use用）
# def stringlist_changeto_viscenterset(word):
#     numlist = [i for i, x in enumerate(word) if x == '-finish-']
#
#     res = []
#     for j in range(len(numlist)):
#         if j == 0:
#             res.append(word[:numlist[j]])
#         else:
#             tmp = []
#             tmp.extend(word[numlist[j-1]+1:numlist[j]])
#             res.append(tmp)
#     print(res, file=sys.stderr)
#     result = []
#     for i in range(len(res)):
#         num = copy.copy(res[i][0])
#         res[i].pop(0)
#         center_data = []
#         for j in range(len(res[i])):
#             center_data.append(float(res[i][j]))
#         result.append([num,center_data])
#     return result
