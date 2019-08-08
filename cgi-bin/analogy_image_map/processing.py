#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
from tqdm import tqdm
import datetime
import re
import json
import numpy as np
import mypackage.other as myp_other
import mypackage.doc2vec_recommend as myp_doc_rec
import mypackage.tfidf as myp_tfidf
import mypackage.harmonic_mean as myp_hmean
import mypackage.response as myp_res
import mypackage.calculation as myp_cal
import mypackage.calculation_2 as myp_cal2
import mypackage.normal_distribution as myp_norm
import mypackage.color as myp_color

import MySQLdb
import os, sys ## 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

cgitb.enable()
form = cgi.FieldStorage()
user_id = form.getvalue('user_id') ## CrowdWorksID
prefecture = form.getvalue('prefecture_name') ## 都道府県
area = form.getvalue('area_name') ## エリア
# history = form.getvalue('visited_name') ## 既訪問スポット名(履歴)
history = form.getlist('visited_name[]')
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
    select_user_history = "SELECT id,name,lat,lng,area_id,url,description from spot_mst where name like '{spot}' AND address like '{area}' AND review=(SELECT max(review) FROM spot_mst WHERE name like '{spot}' AND address like '{area}' AND review != 0);".format(spot=like_spot_list[0][i],area=like_area_list[0][i])
    cur.execute(select_user_history)
    spot_data = cur.fetchone()
    if spot_data is None:
        continue
    else:
        visited_spot_list.append(spot_data)

visited_spot_id_list = []
vis_name,vis_lat,vis_lng,vis_url,vis_description = [],[],[],[],[]
for i in range(len(visited_spot_list)):
    visited_spot_id_list.append(visited_spot_list[i][0])
    if visited_spot_list[i][2]!=0 and visited_spot_list[i][3]!=0:
        vis_name.append(visited_spot_list[i][1])
        vis_lat.append(str(visited_spot_list[i][2]))
        vis_lng.append(str(visited_spot_list[i][3]))
        vis_url.append(str(visited_spot_list[i][5]))
        vis_description.append(str(visited_spot_list[i][6]))
    else:
        continue


############################################################
## DB挿入
############################################################
## ユーザ入力とDBヘ書き込む
sql_insert = "INSERT INTO analogy_map(user_id, prefecture, area, start_datetime, history) VALUES(%s,%s,%s,%s,%s);"
cur.execute(sql_insert,(user_id, prefecture, area, start_datetime, history))
conn.commit()

## ユーザの最新情報を得る
cur.execute("SELECT max(id) FROM analogy_map WHERE user_id='{user}';".format(user = user_id))
record_id = cur.fetchone()[0]


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
# print("<h4>エリアIDの数：\t{}</h4>".format(len(unvisited_area_id_list)))

## 未訪問エリア内(レビュー and [lat or lng])ありスポット
## AND description LIKE '%ショッピング%'
select_unvisited_spot = "SELECT DISTINCT id,name,lat,lng,area_id,review,url,description FROM spot_mst WHERE area_id IN {area} AND review!=0 AND (lat!=0 or lng!=0) AND id NOT IN {vis} AND name NOT LIKE '%レンタ%' AND description LIKE '%ショッピング%' ORDER BY review DESC limit 20;".format(area=tuple(unvisited_area_id_list),vis=tuple(visited_spot_id_list))
unvisited_spot_list = myp_other.spot_or_reviewlist(select_unvisited_spot)

## 未訪問エリア内スポットIDリスト
unvisited_spot_id_list = []
## GoogleMapの表示
unvis_name,unvis_lat,unvis_lng,unvis_url,unvis_description = [],[],[],[],[]
for i in range(len(unvisited_spot_list)):
    for j in range(len(unvisited_spot_list[i])):
        unvisited_spot_id_list.append(unvisited_spot_list[i][j][0])
        if unvisited_spot_list[i][j][2]!=0 and unvisited_spot_list[i][j][3]!=0:
            unvis_name.append(unvisited_spot_list[i][j][1])
            unvis_lat.append(str(unvisited_spot_list[i][j][2]))
            unvis_lng.append(str(unvisited_spot_list[i][j][3]))
            unvis_url.append(str(unvisited_spot_list[i][j][6]))
            unvis_description.append(str(unvisited_spot_list[i][j][7]))
        else:
            continue

############################################################
############################################################
## 既訪問スポットベクトル
select_visited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(visited_spot_id_list))
## 特徴ベクトル
visited_spot_vectors = myp_doc_rec.spot_list(select_visited_spot_vectors)
## 特徴ベクトル差分
visited_spot_vectors_doc = myp_doc_rec.doc2vec_feature(visited_spot_vectors)

## 未訪問スポットベクトル
select_unvisited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(unvisited_spot_id_list))
unvisited_spot_vectors = myp_doc_rec.spot_list(select_unvisited_spot_vectors)
unvisited_spot_vectors_doc = myp_doc_rec.doc2vec_feature(unvisited_spot_vectors)

############################################################
## 相対的な特徴（差分ベクトル）
############################################################
## 既訪問と未訪問スポットベクトルの差の類似度計算
visited_spot_name_all,unvisited_spot_name_all = [],[]
visited_spot_review_all,unvisited_spot_review_all = [],[]
for i in range(len(visited_spot_vectors_doc)):
    visited_spot_name_all.append(visited_spot_vectors_doc[i][0])
    visited_spot_review_all.append(visited_spot_vectors_doc[i][1])
for i in range(len(unvisited_spot_vectors_doc)):
    unvisited_spot_name_all.append(unvisited_spot_vectors_doc[i][0])
    unvisited_spot_review_all.append(unvisited_spot_vectors_doc[i][1])
result_UtoV_top = myp_doc_rec.recommend_all(visited_spot_name_all,unvisited_spot_name_all,visited_spot_review_all,unvisited_spot_review_all)

## 類似度高い順でソート
result_UtoV_top.sort(key=lambda x:x[1][1],reverse=True)

## 既訪問スポットの単語に重みつけ
select_visited_spot_reviews = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(visited_spot_id_list))
visited_spot_reviews = myp_tfidf.spot_list_tfidf(select_visited_spot_reviews)
visited_tfidf,visited_mean = myp_tfidf.tfidf_hm(visited_spot_reviews)

## 未訪問スポットの単語に重みつけ
select_unvisited_spot_reviews = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(unvisited_spot_id_list))
unvisited_spot_reviews = myp_tfidf.spot_list_tfidf(select_unvisited_spot_reviews)
unvisited_tfidf,unvisited_mean = myp_tfidf.tfidf_hm(unvisited_spot_reviews)

## 既訪問と未訪問スポット特徴語(調和平均)
UtoV_top10_harmonic = myp_hmean.sort_tfidf_UtoV_harmonic(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,result_UtoV_top)
# print(UtoV_top10_harmonic,file=sys.stderr)

## 線の色
color_res = myp_color.color_bpr()
# try:
#     myp_cal2.calculation(vis_name,vis_lat,vis_lng,unvis_name,unvis_lat,unvis_lng,UtoV_top10_harmonic,color_res)
# except:
#     import traceback
#     traceback.print_exc()

try:
    myp_norm.calculation(vis_name,vis_lat,vis_lng,unvis_name,unvis_lat,unvis_lng,UtoV_top10_harmonic,color_res)
except:
    import traceback
    traceback.print_exc()

# myp_norm.normal_distribution()

## レスポンス作成，mysqlに入れるためのカラム内容作成(10個まで表示)
# sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word = myp_res.response_harmonic(UtoV_top10_harmonic[:50],unvis_name,unvis_lat,unvis_lng,unvis_url,unvis_description)
#
# myp_res.response(vis_name,vis_lat,vis_lng,vis_url,vis_description,unvis_name,unvis_lat,unvis_lng,unvis_url,unvis_description,UtoV_top10_harmonic[:50])
#
# finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
# sql_update = "UPDATE analogy_map SET unvis_name='{unv}', vis_name='{vis}', cossim='{cos}', word='{word}', unvis_lat='{lat}', unvis_lng='{lng}', word='{word}',finish_datetime='{finish}' WHERE id = {record_id};".format(unv='，'.join(sql_unvis), vis='，'.join(sql_vis), cos='，'.join(sql_cossim), word=sql_word, lat='，'.join(sql_lat), lng='，'.join(sql_lng), finish=finish_datetime, record_id=record_id)
# cur.execute(sql_update)
# conn.commit()
