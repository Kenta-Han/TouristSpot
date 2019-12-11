#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
from tqdm import tqdm
import datetime, re, json, copy, time
import numpy as np
import mypackage.other as myp_other
import mypackage.tfidf as myp_tfidf
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
start_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
print('Content-type: text/html\nAccess-Control-Allow-Origin: *\n')

print("restart", file=sys.stderr)
############################################################
## 既訪問スポット情報
############################################################
## 既訪問を利用
history_list = []
vis_spot_id = [] ## 履歴スポット
history = "---".join(history)
history_list = re.split("---", history)
like_spot_list,like_area_list = myp_other.make_history_list(history_list)

for i in range(len(like_spot_list[0])):
    select_user_history = "SELECT id from spot_mst2 where name like '{spot}' AND address like '{area}' AND review=(SELECT max(review) FROM spot_mst WHERE name like '{spot}' AND address like '{area}' AND review != 0);".format(spot=like_spot_list[0][i],area=like_area_list[0][i])
    cur.execute(select_user_history)
    spot_data = cur.fetchone()[0]
    if spot_data is None:
        continue
    else:
        vis_spot_id.append(spot_data)

# for i in range(len(like_spot_list[0])):
#     select_user_history = "SELECT id,name,lat,lng,area_id,url,description,category1 from spot_mst2 where name like '{spot}' AND address like '{area}' AND review=(SELECT max(review) FROM spot_mst WHERE name like '{spot}' AND address like '{area}' AND review != 0);".format(spot=like_spot_list[0][i],area=like_area_list[0][i])
#     cur.execute(select_user_history)
#     spot_data = cur.fetchone()
#     if spot_data is None:
#         continue
#     else:
#         visited_spot_list.append(spot_data)
#
# visited_spot_id_list = []
# vis_spot_id,vis_name,vis_lat,vis_lng,vis_url,vis_description,vis_cate = [],[],[],[],[],[],[]
# for i in range(len(visited_spot_list)):
#     visited_spot_id_list.append(visited_spot_list[i][0])
#     if visited_spot_list[i][2]!=0 and visited_spot_list[i][3]!=0:
#         vis_spot_id.append(visited_spot_list[i][0])
#         vis_name.append(visited_spot_list[i][1])
#         vis_lat.append(str(visited_spot_list[i][2]))
#         vis_lng.append(str(visited_spot_list[i][3]))
#         vis_url.append(str(visited_spot_list[i][5]))
#         vis_description.append(str(visited_spot_list[i][6]))
#         vis_cate.append(str(visited_spot_list[i][7]))
#     else:
#         continue
#
# vis_cate = [x for x in set(vis_cate) if vis_cate.count(x) >= 1]

############################################################
## 既訪問スポット 階層的クラスタリング
############################################################
start_time = time.time()
## 既訪問スポットのレビューベクトルを得る
select_vis_spot_vectors = "SELECT * FROM review_vectors_spotname WHERE spot_id IN ({})".format(str(vis_spot_id)[1:-1])
vis_review_vectors = myp_cluster.review_vectors_list(select_vis_spot_vectors)
# print(vis_review_vectors, file=sys.stderr)

threshold = 0.65 ## クラスタ分けの閾値
vis_res = myp_cluster.kaisoClustering(select_vis_spot_vectors,threshold)
## 階層的クラスタリングの結果から，各クラスタの重心を求める
# vis_center = np.array(myp_cluster.calculateCenter(vis_res))
## 階層的クラスタリングの結果から，各クラスタのスコアを求める
vis_score_dic = myp_cluster.clusterScorering(vis_res, len(vis_spot_id))
# print(len(vis_score_dic), file=sys.stderr)
# vis_center_use = []
# for i in range(len(vis_score_dic)):
#     for j in range(len(vis_center)):
#         if vis_score_dic[i][0] == str(j):
#             vis_center_use.append([j,vis_center[j].tolist()])
# print(vis_center_use, file=sys.stderr)
# ## 利用するクラスタ数を設定
# # use_cluster = len(score_dic)
# # norm_threshold = 1.95 ## 提示レビューのL2ノルムの閾値
# ## 検索スポットの全レビューをクラスタスコアと類似度で重み付け
# # review_score = myp_cluster.reviewScorering(vis_center, str(vis_spot_id)[1:-1], use_cluster, norm_threshold, vis_score_dic)

vis_reviews = []
for i in range(len(vis_score_dic)):
    select_review = "SELECT wakachi_neologd5 FROM review_all WHERE review_id IN ({}) ;".format(str(vis_score_dic[i][2])[1:-1])
    cur.execute(select_review)
    tmp = []
    for i in cur:
        tmp.extend(list(i)[0].split())
    vis_reviews.append(tmp)
# print(vis_reviews, file=sys.stderr)
visited_tfidf = myp_tfidf.tfidf(vis_reviews)
visited_tfidf_set = []
for i in range(len(vis_score_dic)):
    visited_tfidf_set.append([vis_score_dic[i][0],visited_tfidf[i]])
# print(visited_tfidf_set, file=sys.stderr)

print("処理時間：{} sec".format(time.time() - start_time), file=sys.stderr)

############################################################
## DB挿入
############################################################
## ユーザ入力とDBヘ書き込む
sql_insert = "INSERT INTO analogy_deim2020(user_id, prefecture, area, start_datetime, history) VALUES(%s,%s,%s,%s,%s);"
cur.execute(sql_insert,(user_id, prefecture, area, start_datetime, history))
conn.commit()

## ユーザの最新情報を得る
cur.execute("SELECT max(id) FROM analogy_deim2020 WHERE user_id='{user}';".format(user = user_id))
record_id = cur.fetchone()[0]

############################################################
## レスポンス
############################################################
try:
    json_data = myp_json_cluster.response(visited_tfidf_set[:3],record_id,vis_score_dic[:3])
except:
    import traceback
    traceback.print_exc()
# print(json_data, file=sys.stderr)

print(json.dumps(json_data))
