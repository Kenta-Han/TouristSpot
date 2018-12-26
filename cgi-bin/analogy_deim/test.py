#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
from tqdm import tqdm
import datetime
import re,json
import mypackage.other as myp_other
import mypackage.doc2vec_recommend as myp_doc_rec
import mypackage.tfidf as myp_tfidf
import mypackage.random_harmonic as myp_rh
import mypackage.response as myp_res

import MySQLdb
import os, sys ## 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

############################################################
## 既訪問スポット情報
############################################################
user_id = "test"
prefecture = "東京"
area = ""
history = ["釧路市ふれあいホースパーク---北海道","動物ふれあいランド---北海道","ふれあいファームいずみ---北海道","夕日（あいロード夕日の丘観光案内所）---北海道"]
start_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
## [伏見稲荷大社,鹿苑寺（金閣寺）,龍安寺,清水寺,八坂神社]
# visited_spot_id_list = ['spt_26109ag2130015470','spt_26101ag2130014551','spt_26108ag2130015438','spt_26105ag2130012063','spt_26105ag2130010617']

## 既訪問を利用
history_list = []
user_spot = [] ## 履歴スポット
history = "---".join(history)
history_list = re.split("---", history)
like_spot_list,like_area_list = myp_other.Make_History_List(history_list)
for i in range(len(like_spot_list[0])):
    select_user_history = "SELECT id,name,lat,lng,area_id,url from spot_mst where name like '{spot}' AND address like '{area}' AND review=(SELECT max(review) FROM spot_mst WHERE name like '{spot}' AND address like '{area}' AND review != 0);".format(spot=like_spot_list[0][i],area=like_area_list[0][i])
    cur.execute(select_user_history)
    spot_data = cur.fetchone()
    if spot_data is None:
        continue
    else:
        user_spot.append(spot_data)
visited_spot_id_list = []
visited_spot_url_list = []
for i in range(len(user_spot)):
    visited_spot_id_list.append(user_spot[i][0])
    visited_spot_url_list.append(user_spot[i][5])


############################################################
## DB挿入
############################################################
## ユーザ入力とDBヘ書き込む
sql_insert = "INSERT INTO analogy_deim(user_id, prefecture, area, start_datetime, history) VALUES(%s,%s,%s,%s,%s);"
cur.execute(sql_insert,(user_id, prefecture, area, start_datetime, history))
conn.commit()

## ユーザの最新情報を得る
cur.execute("SELECT max(id) FROM analogy_deim WHERE user_id='{user}';".format(user = user_id))
record_id = cur.fetchone()[0]


############################################################
## 未訪問エリア情報
############################################################
## 未訪問エリアIDリスト
if area == None:
    select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND id < 30435;".format(pre = prefecture)
    unvisited_area_id_list = myp_other.Area_id_List(select_unvisited_area_id)
    unvisited_area_id_list = myp_other.Area_id_List(select_unvisited_area_id)
else:
    select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND (area2 LIKE '%{area}%' OR area3 LIKE '%{area}%') AND id < 30435;".format(pre = prefecture, area = area)
    unvisited_area_id_list = myp_other.Area_id_List(select_unvisited_area_id)

select_unvisited_spot = "SELECT DISTINCT id,name,lat,lng,area_id,review,url FROM spot_mst WHERE area_id IN {area} AND review!=0 AND (lat!=0 or lng!=0) AND id NOT IN {vis} ORDER BY review DESC limit 20;".format(area=tuple(unvisited_area_id_list),vis=tuple(visited_spot_id_list))
unvisited_spot_list = myp_other.SpotORReview_List(select_unvisited_spot)

## 未訪問エリア内スポットIDリスト
unvisited_spot_id_list = []
## GoogleMapの表示
name,lat,lng,url = [],[],[],[]
for i in range(len(unvisited_spot_list)):
    for j in range(len(unvisited_spot_list[i])):
        unvisited_spot_id_list.append(unvisited_spot_list[i][j][0])
        if unvisited_spot_list[i][j][2]!=0 and unvisited_spot_list[i][j][3]!=0:
            name.append(unvisited_spot_list[i][j][1])
            lat.append(str(unvisited_spot_list[i][j][2]))
            lng.append(str(unvisited_spot_list[i][j][3]))
            url.append(str(unvisited_spot_list[i][j][6]))
        else:
            continue

############################################################
############################################################
## 既訪問スポットベクトル
select_visited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(visited_spot_id_list))
## 特徴ベクトル
visited_spot_vectors = myp_doc_rec.Spot_List(select_visited_spot_vectors)
## 特徴ベクトル差分
visited_spot_vectors_doc = myp_doc_rec.Doc2Cec_Feature(visited_spot_vectors)

## 未訪問スポットベクトル
select_unvisited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(unvisited_spot_id_list))
unvisited_spot_vectors = myp_doc_rec.Spot_List(select_unvisited_spot_vectors)
unvisited_spot_vectors_doc = myp_doc_rec.Doc2Cec_Feature(unvisited_spot_vectors)

############################################################
## 相対的な特徴（差分ベクトル）
############################################################
## 既訪問と未訪問スポットベクトルの差の類似度計算(1番高い)
visited_spot_name_all,unvisited_spot_name_all = [],[]
visited_spot_review_all,unvisited_spot_review_all = [],[]
for i in range(len(visited_spot_vectors_doc)):
    visited_spot_name_all.append(visited_spot_vectors_doc[i][0])
    visited_spot_review_all.append(visited_spot_vectors_doc[i][1])
for i in range(len(unvisited_spot_vectors_doc)):
    unvisited_spot_name_all.append(unvisited_spot_vectors_doc[i][0])
    unvisited_spot_review_all.append(unvisited_spot_vectors_doc[i][1])
result_UtoV_top = myp_doc_rec.Recommend_All(visited_spot_name_all,unvisited_spot_name_all,visited_spot_review_all,unvisited_spot_review_all)

## 類似度高い順でソート
result_UtoV_top.sort(key=lambda x:x[1][1],reverse=True)

## 既訪問スポットの単語に重みつけ
select_visited_spot_reviews = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(visited_spot_id_list))
visited_spot_reviews = myp_tfidf.Spot_List_TFIDF(select_visited_spot_reviews)
visited_tfidf,visited_mean = myp_tfidf.Tfidf_HM(visited_spot_reviews)

## 未訪問スポットの単語に重みつけ
select_unvisited_spot_reviews = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(unvisited_spot_id_list))
unvisited_spot_reviews = myp_tfidf.Spot_List_TFIDF(select_unvisited_spot_reviews)
unvisited_tfidf,unvisited_mean = myp_tfidf.Tfidf_HM(unvisited_spot_reviews)

## 既訪問と未訪問スポット特徴語TOP10(調和平均)
top10_random,top10_harmonic = myp_rh.Sort_TFIDF_UtoV(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,result_UtoV_top)
# top10 = myp_hmean.Sort_TFIDF_UtoV(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,result_UtoV_top)

## レスポンス作成，mysqlに入れるためのカラム内容作成
sql_word_r,json_wrandom = myp_res.Response_WRandom(top10_random[:5],name,lat,lng,url)

sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word_h,json_harmonic = myp_res.Response_Harmonic(top10_harmonic[:5],name,lat,lng,url)

random,json_random = myp_res.Response_Random()
