#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import datetime
from tqdm import tqdm
import numpy as np
from pprint import pprint
import re ## 区切り文字を複数指定

from pprint import pprint
import matplotlib.pyplot as plt
import mypackage.package_01 as myp_pk01

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
history = form.getvalue('history_name') ## 履歴
start_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

## ユーザ入力とDBヘ書き込む
sql_insert = "INSERT INTO map_test(user_id, prefecture, area, start_datetime,history) VALUES(%s,%s,%s,%s,%s);"
cur.execute(sql_insert,(user_id, prefecture, area, start_datetime,history))
conn.commit()

## ユーザの最新情報を得る
cur.execute("SELECT max(id) FROM map_test WHERE user_id='{user}';".format(user = user_id))
record_id = cur.fetchone()[0]

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
<link href='../../data/stylesheet_analogy_test.css' rel='stylesheet' type='text/css' />
<title>観光体験マップ選択</title>
</head>

<body>
<header><h1 class='title'>観光体験マップ</h1></header>

"""
print(html_body)

print("<h2>既訪問スポット情報</h2>")
## [伏見稲荷大社,鹿苑寺（金閣寺）,龍安寺,清水寺,八坂神社]
visited_spot_id_list = ['spt_26109ag2130015470','spt_26101ag2130014551','spt_26108ag2130015438','spt_26105ag2130012063','spt_26105ag2130010617']

## 既訪問を利用
# history_list = []
# user_spot = []
# history_list = re.split("[,，]", history)
# like_spot_list,like_area_list = myp_pk01.Make_History_List(history_list)
# for i in range(len(like_area_list[0])):
#     select_user_history = "SELECT id,name,lat,lng,area_id from spot_mst where name like '{spot}' AND address like '{area}' AND review=(SELECT max(review) FROM spot_mst WHERE name like '{spot}' AND address like '{area}' AND review != 0);".format(spot=like_spot_list[0][i],area=like_area_list[0][i])
#     cur.execute(select_user_history)
#     user_spot.append(cur.fetchone())
# print("<h4>履歴スポット(Spot_id, Name, Lat, Lng, Area_id)：</h4>\n{}".format(user_spot))
# visited_spot_id_list = []
# for i in range(len(user_spot)):
#     visited_spot_id_list.append(user_spot[i][0])
# print(visited_spot_id_list)

print("<h2>未訪問エリア情報</h2>")
## 未訪問エリアIDリスト
select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND (area2 LIKE '%{area}%' OR area3 LIKE '%{area}%') AND id < 30435;".format(pre = prefecture, area = area)
unvisited_area_id_list = myp_pk01.Area_id_List(select_unvisited_area_id)
print("<h4>エリアIDの数：\t{}</h4>".format(len(unvisited_area_id_list)))

## 未訪問エリア内(レビュー and [lat or lng])ありスポット
select_unvisited_spot = "SELECT DISTINCT id,name,lat,lng,area_id,review FROM spot_mst WHERE area_id IN {} AND review!=0 AND(lat!=0 or lng!=0) ORDER BY RAND() LIMIT 8;".format(tuple(unvisited_area_id_list))
unvisited_spot_list = myp_pk01.SpotORReview_List(select_unvisited_spot)
# print("<h4>エリアスポット数(レビューあり)：\t{}</h4>".format(len(unvisited_spot_list)))
# print("<h4>エリアスポット</h4>")
print("<ol>")
for i in range(len(unvisited_spot_list)):
    for j in range(len(unvisited_spot_list[i])):
        print("<li>Spot_id：" + str(unvisited_spot_list[i][j][0]) + "，Name：" + str(unvisited_spot_list[i][j][1]) + "，Lat：" + str(unvisited_spot_list[i][j][2])  + "，Lng：" + str(unvisited_spot_list[i][j][3]) + "，Area_id：" + str(unvisited_spot_list[i][j][4]) + "，Review_Count：" + str(unvisited_spot_list[i][j][2]) + "</li>")
print("</ol>")

## 未訪問エリア内スポットIDリスト
unvisited_spot_id_list = []
## GoogleMapの表示
name,lat,lng = [],[],[]
cnt = 0
for i in range(len(unvisited_spot_list)):
    for j in range(len(unvisited_spot_list[i])):
        unvisited_spot_id_list.append(unvisited_spot_list[i][j][0])
        if unvisited_spot_list[i][j][2]!=0 and unvisited_spot_list[i][j][3]!=0:
            name.append(unvisited_spot_list[i][j][1])
            lat.append(str(unvisited_spot_list[i][j][2]))
            lng.append(str(unvisited_spot_list[i][j][3]))
            cnt += 1
        else:
            continue
print(name,lat,lng)
# [東京都庁舎展望室,浅草寺,明治神宮,新宿御苑,皇居東御苑]
unvisited_spot_id_list = ['spt_13104aj2200025349','spt_13106ag2130012302','spt_13113ag2130014473','spt_13104ah2140016473','spt_13101ah2140016178']


###########################################################
###########################################################
# print("<h4>既訪問スポットベクトル</h4>")
select_visited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(visited_spot_id_list))
visited_spot_vectors = myp_pk01.Spot_List(select_visited_spot_vectors)
# print(visited_spot_vectors)
visited_spot_vectors_doc = myp_pk01.Doc2Cec_Feature(visited_spot_vectors)

# print("<h4>未訪問スポットベクトル</h4>")
select_unvisited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(unvisited_spot_id_list))
unvisited_spot_vectors = myp_pk01.Spot_List(select_unvisited_spot_vectors)
# print(unvisited_spot_vectors)
unvisited_spot_vectors_doc = myp_pk01.Doc2Cec_Feature(unvisited_spot_vectors)
# print(unvisited_spot_vectors_doc)

##########################
## 既訪問と未訪問スポットベクトルの差の類似度(1番高い)
visited_spot_name_all,unvisited_spot_name_all = [],[]
visited_spot_review_all,unvisited_spot_review_all = [],[]
for i in range(len(visited_spot_vectors_doc)):
    visited_spot_name_all.append(visited_spot_vectors_doc[i][0])
    visited_spot_review_all.append(visited_spot_vectors_doc[i][1])
for i in range(len(unvisited_spot_vectors_doc)):
    unvisited_spot_name_all.append(unvisited_spot_vectors_doc[i][0])
    unvisited_spot_review_all.append(unvisited_spot_vectors_doc[i][1])
result_VtoU_top,result_UtoV_top = myp_pk01.Recommend_All(visited_spot_name_all,unvisited_spot_name_all,visited_spot_review_all,unvisited_spot_review_all)
# print("<h3>Visited to Unvisited</h3>")
# pprint(result_VtoU_top)
# print("<h3>Unvisited to Visited</h3>")
# pprint(result_UtoV_top)

##########################
select_visited_spot_reviews = "SELECT spot_id,wakachi_neologd2 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd2;".format(tuple(visited_spot_id_list))
visited_spot_reviews = myp_pk01.Spot_List_TFIDF(select_visited_spot_reviews)
visited_tfidf,visited_mean = myp_pk01.Tfidf(visited_spot_reviews)
# print("<h4>既訪問毎平均：</h4>" + str(visited_spot_name_all) + "\n" + str(visited_mean))

select_unvisited_spot_reviews = "SELECT spot_id,wakachi_neologd2 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd2;".format(tuple(unvisited_spot_id_list))
unvisited_spot_reviews = myp_pk01.Spot_List_TFIDF(select_unvisited_spot_reviews)
unvisited_tfidf,unvisited_mean = myp_pk01.Tfidf(unvisited_spot_reviews)
# print("<h4>未訪問毎平均：</h4>" + str(unvisited_spot_name_all) + "\n" + str(unvisited_mean))

##########################
# print("<h2>既訪問と未訪問スポット特徴語TOP10(平均以上)</h2>")
# VtoU_top10 = myp_pk01.Sort_TFIDF_VtoU(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_VtoU_top)
# print("<h3>Visited to Unvisited</h3><ol>")
# for i in range(len(VtoU_top10)):
#     print("<li>既訪問：" + VtoU_top10[i][0] + "，未訪問：" + VtoU_top10[i][1] + "，類似度：" + str(result_VtoU_top[i][1][1]) + "<ul>")
#     for j in range(len(VtoU_top10[i][2])):
#         try:
#             print("<li>特徴語：" + VtoU_top10[i][2][j][0] + "</li>")
#         except TypeError:
#             continue
#     print("</ul></li>")
# print("</ol>")
#
# UtoV_top10 = myp_pk01.Sort_TFIDF_UtoV(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_UtoV_top)
# print("<h3>Unvisited to Visited</h3><ol>")
# for i in range(len(UtoV_top10)):
#     print("<li>未訪問：" + UtoV_top10[i][0] + "，既訪問：" + UtoV_top10[i][1] + "，類似度：" + str(result_UtoV_top[i][1][1]) + "<ul>")
#     for j in range(len(UtoV_top10[i][2])):
#         try:
#             print("<li>特徴語：" + UtoV_top10[i][2][j][0] + "</li>")
#         except TypeError:
#             continue
#     print("</ul></li>")
# print("</ol>")

##########################
print("<h2>既訪問と未訪問スポット特徴語TOP10(調和平均)</h2>")

# VtoU_top10 = myp_pk01.Sort_TFIDF_VtoU_Harmonic(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_VtoU_top)
# print("<h3>Visited to Unvisited</h3><ol>")
# for i in range(len(VtoU_top10)):
#     print("<li>既訪問：" + VtoU_top10[i][0] + "，未訪問：" + VtoU_top10[i][1] + "，類似度：" + str(result_VtoU_top[i][1][1]) + "<ul>")
#     for j in range(len(VtoU_top10[i][2])):
#         try:
#             print("<li>特徴語：" + VtoU_top10[i][2][j][0] + "</li>")
#         except TypeError:
#             continue
#     print("</ul></li>")
# print("</ol>")

UtoV_top10 = myp_pk01.Sort_TFIDF_UtoV_Harmonic(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_UtoV_top)
print("<h3>Unvisited to Visited</h3><ol>")
for i in range(len(UtoV_top10)):
    print("<li>未訪問：" + UtoV_top10[i][0] + "，既訪問：" + UtoV_top10[i][1] + "，類似度：" + str(result_UtoV_top[i][1][1]) + "<ul>")
    for j in range(len(UtoV_top10[i][2])):
        try:
            print("<li>特徴語：" + UtoV_top10[i][2][j][0] + "</li>")
        except TypeError:
            continue
    print("</ul></li>")
print("</ol>")

## DBにスポット名，座標を挿入
finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
sql_update = "UPDATE map_test SET finish_datetime='{finish}', unvisited='{spot_name}', lat='{lat}', lng='{lng}' where id = {record_id};".format(finish=finish_datetime, spot_name=','.join(name), lat=','.join(lat), lng=','.join(lng), record_id=record_id)
cur.execute(sql_update)
conn.commit()

html_map = u"""
<br><div id="map" style="width:100%; height:750px; margin: 0 8px 0 8px;"></div>
<script type="text/javascript" src="../../javascript/googlemap2.js">
</script>
<script type="text/javascript">
    gmap({});
</script>
<script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBzLtrdLAR0doAuGVk0HDIRkZJ1CkmDelo&callback=initMap"></script>
<br></body></html>
""".format(record_id)
print(html_map)
