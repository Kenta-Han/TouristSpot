#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
from tqdm import tqdm
import datetime, re, json, random, string, copy, time
import numpy as np
import mypackage.other as myp_other
import mypackage.doc2vec_recommend as myp_doc_rec
import mypackage.tfidf as myp_tfidf
import mypackage.feature_mean as myp_feature
import mypackage.normal_distribution_map_line as myp_norm_l
import mypackage.cos_sim_tfidf as myp_cos_tfidf
import mypackage.cluster as myp_cluster
from collections import defaultdict

import MySQLdb
import os, sys ## 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

def Randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

## 承認コード，乱数生成
def Response_Random():
    json_random = {"randomname":""}
    random = Randomname(12)
    json_random["randomname"] = random
    return random,json_random

cgitb.enable()
form = cgi.FieldStorage()
record_id = form.getvalue('record_id')
choice_num = form.getvalue('choice')
history = form.getlist('visited_name[]')
# tfidf_vis_data = form.getlist('tfidf_vis_data[]')
# visited_tfidf_set = myp_other.stringlist_changeto_clusterset(tfidf_vis_data)
vis_score = form.getlist('vis_score[]')
vis_score_dic = myp_other.stringlist_changeto_visscoreset(vis_score)
print('Content-type: text/html\nAccess-Control-Allow-Origin: *\n')

############################################################
## DB
############################################################
## ユーザの最新情報を得る
cur.execute("SELECT * FROM analogy_deim2020 WHERE id='{}';".format(record_id))
user_data = cur.fetchone()

prefecture = user_data[4]
area = user_data[5]

# ############################################################
## 既訪問スポット情報
############################################################
## 既訪問を利用
history_list = []
visited_spot_list = [] ## 履歴スポット
history = "---".join(history)
history_list = re.split("---", history)
like_spot_list,like_area_list = myp_other.make_history_list(history_list)
for i in range(len(like_spot_list[0])):
    select_user_history = "SELECT id,name,lat,lng,area_id,url,description,category1 from spot_mst2 where name like '{spot}' AND address like '{area}' AND review=(SELECT max(review) FROM spot_mst WHERE name like '{spot}' AND address like '{area}' AND review != 0);".format(spot=like_spot_list[0][i],area=like_area_list[0][i])
    cur.execute(select_user_history)
    spot_data = cur.fetchone()
    if spot_data is None:
        continue
    else:
        visited_spot_list.append(spot_data)

visited_spot_id_list = []
vis_spot_id,vis_name,vis_lat,vis_lng,vis_url,vis_description,vis_cate = [],[],[],[],[],[],[]
for i in range(len(visited_spot_list)):
    visited_spot_id_list.append(visited_spot_list[i][0])
    if visited_spot_list[i][2]!=0 and visited_spot_list[i][3]!=0:
        vis_spot_id.append(visited_spot_list[i][0])
        vis_name.append(visited_spot_list[i][1])
        vis_lat.append(str(visited_spot_list[i][2]))
        vis_lng.append(str(visited_spot_list[i][3]))
        vis_url.append(str(visited_spot_list[i][5]))
        vis_description.append(str(visited_spot_list[i][6]))
        vis_cate.append(str(visited_spot_list[i][7]))
    else:
        continue

vis_cate = [x for x in set(vis_cate) if vis_cate.count(x) >= 1]
# print(vis_cate, file=sys.stderr)

############################################################
## 未訪問エリア情報
############################################################
## 未訪問エリアIDリスト
if area == None:
    select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND id < 30435;".format(pre = prefecture)
    unvisited_area_id_list = myp_other.area_id_list(select_unvisited_area_id)
    unvisited_area_id_list = myp_other.area_id_list(select_unvisited_area_id)
else:
    select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND (area2 LIKE '%{area}%' OR area3 LIKE '%{area}%') AND id < 30435;".format(pre = prefecture, area = area)
    unvisited_area_id_list = myp_other.area_id_list(select_unvisited_area_id)

## 未訪問エリア内(レビュー and [lat or lng])ありスポット
unvisited_spot_list = []
for i in range(len(vis_cate)):
    select_unvisited_spot = "SELECT DISTINCT id,name,lat,lng,area_id,review,url,description,category1 FROM spot_mst2 WHERE area_id IN {area} AND review!=0 AND (lat!=0 or lng!=0) AND id NOT IN {vis} AND name NOT LIKE '%レンタ%' AND category1 LIKE '%{vis_cate}%' ORDER BY review DESC limit 12;".format(area=tuple(unvisited_area_id_list),vis=tuple(visited_spot_id_list),vis_cate=vis_cate[i])
    tmp = myp_other.spot_or_reviewlist(select_unvisited_spot)
    unvisited_spot_list.append(tmp)

unvisited_spot_list_map_l,unvisited_spot_list_map_t,unvisited_spot_list_map_p = [],[],[]
for i in range(len(unvisited_spot_list)):
    n = 0
    unvisited_spot_list_map_p.extend(unvisited_spot_list[i][n:n+3])
    n = 3
    unvisited_spot_list_map_l.extend(unvisited_spot_list[i][n:n+3])
    n = 6
    unvisited_spot_list_map_t.extend(unvisited_spot_list[i][n:n+3])
if len(unvisited_spot_list_map_l) != len(unvisited_spot_list_map_t) or len(unvisited_spot_list_map_t) != len(unvisited_spot_list_map_p) or len(unvisited_spot_list_map_l) != len(unvisited_spot_list_map_p):
    a = min([len(unvisited_spot_list_map_l),len(unvisited_spot_list_map_t),len(unvisited_spot_list_map_p)])
    unvisited_spot_list_map_p = unvisited_spot_list_map_p[:a]
    unvisited_spot_list_map_l = unvisited_spot_list_map_l[:a]
    unvisited_spot_list_map_t = unvisited_spot_list_map_t[:a]

## 未訪問エリア内スポットIDリスト
unvisited_spot_id_list = []
## GoogleMapの表示
unvis_spot_id,unvis_name,unvis_lat,unvis_lng,unvis_url,unvis_description = [],[],[],[],[],[]
for i in range(len(unvisited_spot_list_map_l)):
    for j in range(len(unvisited_spot_list_map_l[i])):
        unvisited_spot_id_list.append(unvisited_spot_list_map_l[i][j][0])
        if unvisited_spot_list_map_l[i][j][2]!=0 and unvisited_spot_list_map_l[i][j][3]!=0:
            unvis_spot_id.append(unvisited_spot_list_map_l[i][j][0])
            unvis_name.append(unvisited_spot_list_map_l[i][j][1])
            unvis_lat.append(str(unvisited_spot_list_map_l[i][j][2]))
            unvis_lng.append(str(unvisited_spot_list_map_l[i][j][3]))
            unvis_url.append(str(unvisited_spot_list_map_l[i][j][6]))
            unvis_description.append(str(unvisited_spot_list_map_l[i][j][7]))
        else:
            continue

############################################################
## 平均類以度
############################################################
def cos_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

## 既訪問スポットのレビューベクトルを得る
vis_cluster_review_vectors = []
for i in range(len(vis_score_dic)):
    select_vis_spot_vectors = "SELECT * FROM review_vectors_spotname WHERE id IN {};".format(tuple(vis_score_dic[i][2]))
    cur.execute(select_vis_spot_vectors)
    review_set = []
    for j in cur:
        review_set.append([j[0],list(j[1:-2])])
    vis_cluster_review_vectors.append([vis_score_dic[i][0],review_set])

## 未訪問スポットのレビューベクトルを得る
select_unvis_spot_vectors = "SELECT * FROM review_vectors_spotname WHERE spot_id IN ({});".format(str(unvis_spot_id)[1:-1])
unvis_review_vectors = myp_other.review_id_and_vectors_list(select_unvis_spot_vectors)

## 計算時間大体3分~5分
unvis_review_groupby_vis_cluster = []
for i in tqdm(range(len(unvis_review_vectors))): ## r1
    unvis_review_cluster_avg = []
    for j in range(len(vis_cluster_review_vectors)): ## A
        tmp = []
        for k in range(len(vis_cluster_review_vectors[j][1])): ## a1,a2
            tmp.append(cos_sim(np.array(unvis_review_vectors[i][1]),np.array(vis_cluster_review_vectors[j][1][k][1])))
        unvis_review_cluster_avg.append([vis_cluster_review_vectors[j][0],np.mean(np.array(tmp))])
    ## 類似度が一番大きいのクラスタを出す
    short = max(unvis_review_cluster_avg,key=lambda x:x[1])
    if short[1] >= 0.125:
        unvis_review_groupby_vis_cluster.append([short,unvis_review_vectors[i][0]])
unvis_use_index_num = [i for i, x in enumerate(unvis_review_groupby_vis_cluster) if x[0][0] == str(choice_num)]
unvis_use_review_id = []
for i in unvis_use_index_num:
    unvis_use_review_id.append(unvis_review_groupby_vis_cluster[i][1])

# start_time = time.time()
# print("処理時間：{} sec".format(time.time() - start_time), file=sys.stderr)

############################################################
## 既訪問スポットと未訪問スポットの計算 ベクトル総当たり
############################################################
## クラスタに属する既訪問スポットレビューベクトル
vis_use_review_id = [j[2] for j in [i for i in vis_score_dic] if j[0] == choice_num][0]
select_vis_spot_vectors = "SELECT * FROM review_vectors_spotname WHERE id IN {};".format(tuple(vis_use_review_id))
cur.execute(select_vis_spot_vectors)
vis_dic = defaultdict(list)
for j in cur:
    vis_dic[j[-1]].append(list(j[1:-2]))
vis_key = list(vis_dic.keys())

## クラスタに属する未訪問スポットレビューベクトル
select_unvis_spot_reviews = "SELECT * FROM review_vectors_spotname WHERE id IN {};".format(tuple(unvis_use_review_id))
cur.execute(select_unvis_spot_vectors)
unvis_dic = defaultdict(list)
for j in cur:
    unvis_dic[j[-1]].append(list(j[1:-2]))
unvis_key = list(unvis_dic.keys())

unvis_vis_set = []
for i in tqdm(range(len(unvis_key))):
    unvis_vis_one_set = []
    for j in range(len(vis_key)):
        tmp2 = []
        for ix in range(len(unvis_dic[unvis_key[i]])):
            tmp = []
            for jx in range(len(vis_dic[vis_key[j]])):
                tmp.append(cos_sim(np.array(unvis_dic[unvis_key[i]][ix]),np.array(vis_dic[vis_key[j]][jx])))
            tmp2.extend(tmp)
        unvis_vis_one_set.append([unvis_key[i],vis_key[j],np.mean(np.array(tmp2))])
    unvis_vis_set.append(unvis_vis_one_set)
print("unvis_vis_set", unvis_vis_set, file=sys.stderr)


############################################################
## 既訪問スポットと未訪問スポットの計算
############################################################
## クラスタに属する既訪問スポットレビューの単語に重みつけ
vis_use_index_num = [i[0] for i in vis_score_dic].index(str(choice_num))
select_visited_spot_reviews = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE review_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(vis_score_dic[vis_use_index_num][2]))
visited_spot_reviews = myp_tfidf.spot_list_tfidf(select_visited_spot_reviews)
visited_tfidf = myp_tfidf.tfidf(visited_spot_reviews)

## クラスタに属する未訪問スポットレビューの単語に重みつけ
select_unvisited_spot_reviews = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE review_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(unvis_use_review_id))
unvisited_spot_reviews = myp_tfidf.spot_list_tfidf(select_unvisited_spot_reviews)
unvisited_tfidf = myp_tfidf.tfidf(unvisited_spot_reviews)

## TFIDFの結果にスポット名を追加
cur.execute("SELECT name,count(name) FROM review_all WHERE review_id IN {} GROUP BY name;".format(tuple(vis_score_dic[vis_use_index_num][2])))
visited_spot_name_all,visited_spot_review_num = [],[]
for i in cur.fetchall():
    visited_spot_name_all.append(i[0])
    visited_spot_review_num.append(i[1])
cur.execute("SELECT name,count(name) FROM review_all WHERE review_id IN {} GROUP BY name;".format(tuple(unvis_use_review_id)))
unvisited_spot_name_all,unvisited_spot_review_num = [],[]
for i in cur.fetchall():
    unvisited_spot_name_all.append(i[0])
    unvisited_spot_review_num.append(i[1])

## 対応付けされなかった未訪問スポットを入れる
for spot in [i for i in unvis_name]:
    if spot not in [j for j in unvisited_spot_name_all]:
        tmp = unvis_name[[j for j in unvis_name].index(spot)]
        unvisited_spot_name_all.append(tmp)
        unvisited_spot_review_num.append(0)
        unvisited_tfidf.append([])

vis_spot,unvis_spot = [],[]
for i in range(len(visited_spot_name_all)):
    vis_spot.append([visited_spot_name_all[i],visited_tfidf[i]])
for i in range(len(unvisited_spot_name_all)):
    unvis_spot.append([unvisited_spot_name_all[i],unvisited_tfidf[i]])

## TFIDFによるコサイン類似度計算
sctfidf = myp_cos_tfidf.SimCalculator()
result_cos_tfidf = []
for i in range(len(vis_spot)):
    for j in range(len(unvis_spot)):
        cos_tfidf = sctfidf.sim_cos(vis_spot[i],unvis_spot[j])
        result_cos_tfidf.append([unvis_spot[j][0],vis_spot[i][0],cos_tfidf])

print("パターン数：vis({}) * unvis({}) = {}".format(len(visited_tfidf),len(unvisited_tfidf),len(result_cos_tfidf)),file=sys.stderr)
print("~~ tfidfによるコサイン類似度計算結果：\n{}".format(sorted(result_cos_tfidf,key=lambda x:x[2],reverse=True)), file=sys.stderr)

## 既訪問と未訪問スポット特徴語 tfidfcos
UtoV_top10_tfidfcos = myp_feature.sort_tfidf_UtoV_tfidfcos(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,result_cos_tfidf)
print("~~ UtoV_top10_tfidfcos:\n{}".format(UtoV_top10_tfidfcos), file=sys.stderr)

try:
    json_data_map_line = myp_norm_l.calculation(vis_name,vis_lat,vis_lng,unvis_name,unvis_lat,unvis_lng,UtoV_top10_tfidfcos,record_id,unvis_url)
except:
    import traceback
    traceback.print_exc()

random,json_random = Response_Random()
json_data = [json_data_map_line] + [json_random]

finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
sql_insert = "UPDATE analogy_sti SET category='{cate}', code='{rand}',finish_datetime='{finish}' WHERE id = {record_id};".format(cate='，'.join(vis_cate),rand=random,finish=finish_datetime,record_id=record_id)
cur.execute(sql_insert)
conn.commit()
# print(json_data, file=sys.stderr)
print(json.dumps(json_data))
