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
from collections import Counter ## 単語出現頻度

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

vis_reviews = []
for i in range(len(vis_score_dic)):
    select_review = "SELECT wakachi_neologd5 FROM review_all WHERE review_id IN ({}) ;".format(str(vis_score_dic[i][2])[1:-1])
    cur.execute(select_review)
    tmp = []
    for i in cur:
        tmp.extend(list(i)[0].split())
    vis_reviews.append(tmp)

## TFIDFによる特徴語抽出
visited_tfidf = myp_tfidf.tfidf(vis_reviews)
visited_tfidf_set = []
for i in range(len(vis_score_dic)):
    visited_tfidf_set.append([vis_score_dic[i][0],visited_tfidf[i]])

# ## 単語出現頻度による特徴語抽出
# conter_list = []
# for i in range(len(vis_reviews)):
#     tmp = []
#     for word, cnt in Counter(vis_reviews[i]).most_common():
#         tmp.append([word, cnt])
#     conter_list.append([vis_score_dic[i][0],tmp])
#
# ## ATFによる特徴語抽出
# avg_tf = myp_tfidf.atf(conter_list)


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
    ## tfidfによるクラスタ特徴語抽出
    json_data = myp_json_cluster.response_tfidf(visited_tfidf_set[:5],record_id,vis_score_dic[:5])
    ## 単語出現頻度によるクラスタ特徴語抽出
    # json_data = myp_json_cluster.response_conter(conter_list[:5],record_id,vis_score_dic[:5])
    # json_data = myp_json_cluster.response_atf(avg_tf[:5],record_id,vis_score_dic[:5])
except:
    import traceback
    traceback.print_exc()

print("処理時間：{} sec".format(time.time() - start_time), file=sys.stderr)
print(json.dumps(json_data))
