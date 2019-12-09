#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
from tqdm import tqdm
import datetime, re, json, random, string, copy, time
import numpy as np
import mypackage.other as myp_other
import mypackage.doc2vec_recommend as myp_doc_rec
import mypackage.tfidf as myp_tfidf
import mypackage.harmonic_mean as myp_hmean
import mypackage.normal_distribution_map_line as myp_norm_l
import mypackage.cos_sim_tfidf as myp_cos_tfidf
import pandas as pd
import pandas.io.sql as psql
import mypackage.cluster as myp_cluster

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
tfidf_vis_data = form.getlist('tfidf_vis_data[]')
visited_tfidf_set = myp_other.stringlist_changeto_clusterset(tfidf_vis_data)
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
# print(user_data, file=sys.stderr)

############################################################
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
## 未訪問スポット 階層的クラスタリング
############################################################
start_time = time.time()
threshold = 0.7 ## クラスタ分けの閾値
## 未訪問スポットのレビューベクトルを得る
select_unvis_spot_vectors = "SELECT * FROM review_vectors_spotname WHERE spot_id IN ({});".format(str(unvis_spot_id)[1:-1])
unvis_review_vectors = myp_cluster.review_vectors_list(select_unvis_spot_vectors)

unvis_res = myp_cluster.kaisoClustering(select_unvis_spot_vectors,threshold)
## 階層的クラスタリングの結果から，各クラスタの重心を求める
unvis_center = myp_cluster.calculateCenter(unvis_res)
## 階層的クラスタリングの結果から，各クラスタのスコアを求める
unvis_score_dic = myp_cluster.clusterScorering(unvis_res, len(unvisited_spot_list))

unvis_reviews = []
for i in range(len(unvis_score_dic)):
    select_review = "SELECT wakachi_neologd5 FROM review_all WHERE review_id IN ({}) ;".format(str(unvis_score_dic[i][2])[1:-1])
    cur.execute(select_review)
    tmp = []
    for i in cur:
        tmp.extend(list(i)[0].split())
    unvis_reviews.append(tmp)
unvisited_tfidf,unvisited_mean = myp_tfidf.tfidf_hm(unvis_reviews)
unvisited_tfidf_set = []
for i in range(len(unvis_score_dic)):
    unvisited_tfidf_set.append([unvis_score_dic[i][0],unvisited_tfidf[i]])
## 類似度降順でソート，各クラスタの上位10件
unvisited_tfidf_top = []
for i in range(len(unvisited_tfidf)):
    unvisited_tfidf_top.append(sorted(unvisited_tfidf[i],key=lambda x:x[1],reverse=True)[:10])

print("処理時間：{} sec".format(time.time() - start_time), file=sys.stderr)

# print("==既訪問スポットtfidf==\n{}".format(visited_tfidf_set), file=sys.stderr)
# print("==未訪問スポットtfidf==\n{}".format(unvisited_tfidf_set), file=sys.stderr)

############################################################
## クラスタ間のコサイン類似度を測る
############################################################
sctfidf = myp_cos_tfidf.SimCalculator()
result_cos_tfidf = []
for i in range(len(visited_tfidf_set)):
    for j in range(len(unvisited_tfidf_set)):
        cos_tfidf = sctfidf.sim_cos(visited_tfidf_set[i],unvisited_tfidf_set[j])
        result_cos_tfidf.append([unvisited_tfidf_set[j][0],visited_tfidf_set[i][0],cos_tfidf])

## result_cos_tfidfの構造 -> [未訪問スポットのクラスタ，既訪問スポットのクラスタ，類似度]
result_cos_tfidf = sorted(result_cos_tfidf,key= lambda x:x[2],reverse=True)
print("Cos類似度\n{}".format(result_cos_tfidf), file=sys.stderr)

############################################################
############################################################
## ユーザが選んだクラスタのレビューIDとレビューが含んでいる既訪問スポット
# print("==vis_score_dic==\n{}".format(vis_score_dic), file=sys.stderr)
target_vis_review_id = vis_score_dic[([i[0] for i in vis_score_dic]).index(str(choice_num))][2]
select_target_vis_spot = "SELECT spot_id FROM review_all WHERE review_id IN {} GROUP BY spot_id;".format(tuple(target_vis_review_id))
cur.execute(select_target_vis_spot)
target_vis_spot = []
for row in cur.fetchall():
    target_vis_spot.append(row[0])

## 既訪問スポットベクトル
select_visited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(target_vis_spot))
visited_spot_vectors = myp_doc_rec.spot_list(select_visited_spot_vectors)
visited_spot_vectors_doc = myp_doc_rec.doc2vec_feature(visited_spot_vectors)

############################################################
############################################################
## result_cos_tfidfにおいてユーザ選択クラスとと類似度がもっとも大きいクラスタのレビューIDとレビューが含んでいる未訪問スポット
tmp = result_cos_tfidf[([i[1] for i in result_cos_tfidf]).index(str(choice_num))][0]
target_unvis_review_id = unvis_score_dic[([i[0] for i in unvis_score_dic]).index(tmp)][2]
select_target_unvis_spot = "SELECT spot_id FROM review_all WHERE review_id IN {} GROUP BY spot_id;".format(tuple(target_unvis_review_id))
cur.execute(select_target_unvis_spot)
target_unvis_spot = []
for row in cur.fetchall():
    target_unvis_spot.append(row[0])

## 未訪問スポットベクトル
select_unvisited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(target_unvis_spot))
unvisited_spot_vectors = myp_doc_rec.spot_list(select_unvisited_spot_vectors)
unvisited_spot_vectors_doc = myp_doc_rec.doc2vec_feature(unvisited_spot_vectors)
