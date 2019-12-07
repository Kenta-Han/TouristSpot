#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
from tqdm import tqdm
import datetime, re, json, random, string, time
import numpy as np
import mypackage.other as myp_other
import mypackage.tfidf as myp_tfidf
import mypackage.normal_distribution_map_line as myp_norm_l
import mypackage.cos_sim_tfidf as myp_cos_tfidf
import pandas as pd
import pandas.io.sql as psql
import mypackage.cluster as myp_cluster
import mypackage.json_cluster as myp_json_cluster

import MySQLdb
import os, sys ## 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

cgitb.enable()
form = cgi.FieldStorage()
user_id = form.getvalue('user_id') ## CrowdWorksID
history = form.getlist('visited_name[]')
prefecture = form.getvalue('prefecture_name') ## 都道府県
area = form.getvalue('area_name') ## エリア
# history = form.getvalue('visited_name') ## 既訪問スポット名(履歴)
orders = form.getvalue('orders') ## CrowdWorksID
start_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
print('Content-type: text/html\nAccess-Control-Allow-Origin: *\n')

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

start_time = time.time()
## 既訪問スポットのレビューベクトルを得る
select_vis_spot_vectors = "SELECT * FROM review_vectors_spotname WHERE spot_id IN ({});".format(str(vis_spot_id)[1:-1])
vis_review_vectors = myp_cluster.review_vectors_list(select_vis_spot_vectors)
# print(len(vis_review_vectors), file=sys.stderr)

threshold = 0.7 ## クラスタ分けの閾値
vis_res = myp_cluster.kaisoClustering(select_vis_spot_vectors,threshold)
# print(vis_res, file=sys.stderr)
## 階層的クラスタリングの結果から，各クラスタの重心を求める
vis_center = myp_cluster.calculateCenter(vis_res)
## 階層的クラスタリングの結果から，各クラスタのスコアを求める
vis_score_dic = myp_cluster.clusterScorering(vis_res, len(visited_spot_list))
# print(vis_score_dic, file=sys.stderr)
## 利用するクラスタ数を設定
# use_cluster = len(score_dic)
# norm_threshold = 1.95 ## 提示レビューのL2ノルムの閾値
## 検索スポットの全レビューをクラスタスコアと類似度で重み付け
# review_score = myp_cluster.reviewScorering(center, str(vis_spot_id)[1:-1], use_cluster, norm_threshold, score_dic)

vis_reviews = []
for i in range(len(vis_score_dic)):
    select_review = "SELECT wakachi_neologd5 FROM review_all WHERE review_id IN ({}) ;".format(str(vis_score_dic[i][2])[1:-1])
    cur.execute(select_review)
    tmp = []
    for i in cur:
        tmp.extend(list(i)[0].split())
    vis_reviews.append(tmp)
visited_tfidf,visited_mean = myp_tfidf.tfidf_hm(vis_reviews)
visited_tfidf_set = []
for i in range(len(vis_score_dic)):
    visited_tfidf_set.append([vis_score_dic[i][0],visited_tfidf[i]])
# print(visited_tfidf_set, file=sys.stderr)

############################################################
## DB挿入
############################################################
## ユーザ入力とDBヘ書き込む
sql_insert = "INSERT INTO analogy_sti(user_id, prefecture, area, start_datetime, history, orders) VALUES(%s,%s,%s,%s,%s,%s);"
cur.execute(sql_insert,(user_id, prefecture, area, start_datetime, history,orders))
conn.commit()

## ユーザの最新情報を得る
cur.execute("SELECT max(id) FROM analogy_sti WHERE user_id='{user}';".format(user = user_id))
record_id = cur.fetchone()[0]


# ############################################################
# ## 未訪問エリア情報
# ############################################################
# ## 未訪問エリアIDリスト
# if area == None:
#     select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND id < 30435;".format(pre = prefecture)
#     unvisited_area_id_list = myp_other.area_id_list(select_unvisited_area_id)
#     unvisited_area_id_list = myp_other.area_id_list(select_unvisited_area_id)
# else:
#     select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND (area2 LIKE '%{area}%' OR area3 LIKE '%{area}%') AND id < 30435;".format(pre = prefecture, area = area)
#     unvisited_area_id_list = myp_other.area_id_list(select_unvisited_area_id)
#
# ## 未訪問エリア内(レビュー and [lat or lng])ありスポット
# unvisited_spot_list = []
# for i in range(len(vis_cate)):
#     select_unvisited_spot = "SELECT DISTINCT id,name,lat,lng,area_id,review,url,description,category1 FROM spot_mst2 WHERE area_id IN {area} AND review!=0 AND (lat!=0 or lng!=0) AND id NOT IN {vis} AND name NOT LIKE '%レンタ%' AND category1 LIKE '%{vis_cate}%' ORDER BY review DESC limit 12;".format(area=tuple(unvisited_area_id_list),vis=tuple(visited_spot_id_list),vis_cate=vis_cate[i])
#     tmp = myp_other.spot_or_reviewlist(select_unvisited_spot)
#     unvisited_spot_list.append(tmp)
#
# unvisited_spot_list_map_l,unvisited_spot_list_map_t,unvisited_spot_list_map_p = [],[],[]
# for i in range(len(unvisited_spot_list)):
#     n = 0
#     unvisited_spot_list_map_p.extend(unvisited_spot_list[i][n:n+3])
#     n = 3
#     unvisited_spot_list_map_l.extend(unvisited_spot_list[i][n:n+3])
#     n = 6
#     unvisited_spot_list_map_t.extend(unvisited_spot_list[i][n:n+3])
# if len(unvisited_spot_list_map_l) != len(unvisited_spot_list_map_t) or len(unvisited_spot_list_map_t) != len(unvisited_spot_list_map_p) or len(unvisited_spot_list_map_l) != len(unvisited_spot_list_map_p):
#     a = min([len(unvisited_spot_list_map_l),len(unvisited_spot_list_map_t),len(unvisited_spot_list_map_p)])
#     unvisited_spot_list_map_p = unvisited_spot_list_map_p[:a]
#     unvisited_spot_list_map_l = unvisited_spot_list_map_l[:a]
#     unvisited_spot_list_map_t = unvisited_spot_list_map_t[:a]

#
# ## 未訪問エリア内スポットIDリスト
# unvisited_spot_id_list = []
# ## GoogleMapの表示
# unvis_spot_id,unvis_name,unvis_lat,unvis_lng,unvis_url,unvis_description = [],[],[],[],[],[]
# for i in range(len(unvisited_spot_list_map_l)):
#     for j in range(len(unvisited_spot_list_map_l[i])):
#         unvisited_spot_id_list.append(unvisited_spot_list_map_l[i][j][0])
#         if unvisited_spot_list_map_l[i][j][2]!=0 and unvisited_spot_list_map_l[i][j][3]!=0:
#             unvis_spot_id.append(unvisited_spot_list_map_l[i][j][0])
#             unvis_name.append(unvisited_spot_list_map_l[i][j][1])
#             unvis_lat.append(str(unvisited_spot_list_map_l[i][j][2]))
#             unvis_lng.append(str(unvisited_spot_list_map_l[i][j][3]))
#             unvis_url.append(str(unvisited_spot_list_map_l[i][j][6]))
#             unvis_description.append(str(unvisited_spot_list_map_l[i][j][7]))
#         else:
#             continue
#
# ## 未訪問スポットのレビューベクトルを得る
# select_unvis_spot_vectors = "SELECT * FROM review_vectors_spotname WHERE spot_id IN ({});".format(str(unvis_spot_id)[1:-1])
# unvis_review_vectors = myp_cluster.review_vectors_list(select_unvis_spot_vectors)
# # print(len(unvis_review_vectors), file=sys.stderr)
#
# unvis_res = myp_cluster.kaisoClustering(select_unvis_spot_vectors,threshold)
# # print(unvis_res, file=sys.stderr)
# ## 階層的クラスタリングの結果から，各クラスタの重心を求める
# unvis_center = myp_cluster.calculateCenter(unvis_res)
# ## 階層的クラスタリングの結果から，各クラスタのスコアを求める
# unvis_score_dic = myp_cluster.clusterScorering(unvis_res, len(unvisited_spot_list))
#
# unvis_reviews = []
# for i in range(len(unvis_score_dic)):
#     select_review = "SELECT wakachi_neologd5 FROM review_all WHERE review_id IN ({}) ;".format(str(unvis_score_dic[i][2])[1:-1])
#     cur.execute(select_review)
#     tmp = []
#     for i in cur:
#         tmp.extend(list(i)[0].split())
#     unvis_reviews.append(tmp)
# unvisited_tfidf,unvisited_mean = myp_tfidf.tfidf_hm(unvis_reviews)
# unvisited_tfidf_set = []
# for i in range(len(unvis_score_dic)):
#     unvisited_tfidf_set.append([unvis_score_dic[i][0],unvisited_tfidf[i]])
# print(unvisited_tfidf_set, file=sys.stderr)
# ## 類似度降順でソート，各クラスタの上位10件
# unvisited_tfidf_top = []
# for i in range(len(unvisited_tfidf)):
#     unvisited_tfidf_top.append(sorted(unvisited_tfidf[i],key=lambda x:x[1],reverse=True)[:10])
# print(unvisited_tfidf_top, file=sys.stderr)
#
# print("処理時間：{} sec".format(time.time() - start_time), file=sys.stderr)
#
# sctfidf = myp_cos_tfidf.SimCalculator()
# result_cos_tfidf = []
# for i in range(len(visited_tfidf_set)):
#     for j in range(len(unvisited_tfidf_set)):
#         cos_tfidf = sctfidf.sim_cos(visited_tfidf_set[i],unvisited_tfidf_set[j])
#         result_cos_tfidf.append([unvisited_tfidf_set[j][0],visited_tfidf_set[i][0],cos_tfidf])
#
# print(result_cos_tfidf, file=sys.stderr)


try:
    json_data = myp_json_cluster.response(visited_tfidf_set,record_id)
except:
    import traceback
    traceback.print_exc()

print(json.dumps(json_data))
