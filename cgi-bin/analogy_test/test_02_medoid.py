#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import datetime
from tqdm import tqdm
import numpy as np
import mypackage.other_def_medoid as myp_other_m
# import pandas as pd
# import json
import re ## 区切り文字を複数指定

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
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='../../data/stylesheet_analogy_test.css' rel='stylesheet' type='text/css' />
<title>観光体験マップ選択</title>
</head>

<body>
<header><h1 class='title'>観光体験マップ</h1></header>

"""
print(html_body)

############################################################
############################################################

## 履歴を使って各スポットの特徴を出す
print("<h1>履歴情報</h1>")
## 履歴を利用
history_list = []
history_list = re.split("[,，]", history)
print("<h4>履歴スポット(入力)：</h4>\n{}".format(history_list))
# like_history_list = myp_other_m.Make_History_List(history_list)
# IN と LIKEを同時にやりたい
# select_user_history = "SELECT id,name,lat,lng,area_id,review FROM spot_mst WHERE name IN {} ORDER BY id AND review != 0;".format(tuple(history_list))
# user_spot_list2 = myp_other_m.SpotORReview_List(select_user_history)
# print("<h4>履歴スポット(Spot_id, Name, Lat, Lng, Area_id, Review)：</h4>\n{}".format(user_spot_list2))


## 東京23区 BETWEEN 17698 AND 18516
select_user_spot = "SELECT id,name,lat,lng,area_id,review FROM spot_mst WHERE area_id BETWEEN 17698 AND 18516 AND review != 0 ORDER BY RAND() LIMIT 10;"
user_spot_list = myp_other_m.SpotORReview_List(select_user_spot)
print("<h4>履歴スポット数：\t{}</h4>".format(len(user_spot_list)))
print("<h4>履歴スポット(Spot_id, Name, Lat, Lng, Area_id, Review)：</h4>\n{}".format(user_spot_list))

## レビューリスト
user_spot_id_list = []
for i in range(len(user_spot_list)):
    user_spot_id_list.append(user_spot_list[i][0])
select_user_review = "SELECT spot_id,wakachi2 FROM review_all WHERE spot_id IN {} ORDER BY spot_id ASC;".format(tuple(user_spot_id_list))
user_review_list = myp_other_m.SpotORReview_List(select_user_review)
print("<h4>全スポットのレビューの数：\t{}</h4>".format(len(user_review_list)))

## スポットリスト
spot_list = []
for i in range(len(user_spot_list)):
    spot_list.append(user_spot_list[i][1])

## スポット毎のレビュー
user_review_wkt_group_by = myp_other_m.EverySpot_Review(user_review_list)

##  ユーザ履歴のスポットの全レビュー
user_review_wkt_all = myp_other_m.AllSpot_Review(user_review_list)

## 単語に重み付け(TFIDF)
tfidf_list = []
for i in tqdm(range(len(user_review_wkt_group_by))):
    user_review_wkt_all.insert(0,user_review_wkt_group_by[i])
    user_words = myp_other_m.Tfidf(user_review_wkt_all)
    tfidf_list.append(user_words[0])
    user_words = 0

## 履歴レビューを辞書でリストにまとめる
user_words_all = myp_other_m.Change_To_Dic(tfidf_list)

## 特徴語をスポット毎でまとめてリスト作成
spot_values_list = myp_other_m.spot_values_list(tfidf_list)

## 各スポットリストの長さを出し，最大値を取る
len_list = []
for i in range(len(spot_values_list)):
    len_list.append(len(spot_values_list[i]))
max_len = max(len_list)
## 配列の長さをパディング(長さを統一)
padding = []
for i in range(len(spot_values_list)):
    pad_width = (0, max_len-len(spot_values_list[i]))
    temp = np.pad(spot_values_list[i], pad_width, 'constant', constant_values=0)
    padding.append(list(temp))
    temp = []

padding = np.array(padding)
## 行列 n*mを確認
print("<h4>行×列の確認：\t{}</h4>".format(padding.shape))

## 各データはどのクラスタに属しているか
pre_labels,cen = myp_other_m.KM(padding,len(padding))

## スポット名とクラスタ結合
name_label = list(zip(spot_list, pre_labels))
print("<h4>スポット名，属するクラスタ：</h4>{}".format(name_label))

## 各クラスタのMedoid
medoid_spot = []
for i in cen:
    medoid_spot.append(name_label[i])
print("<h4>各クラスタのMedoid：</h4>{}".format(medoid_spot))

############################################################
############################################################

## エリア内で各スポットの特徴を出す
print("<br><h1>エリア内情報</h1>")
## エリアIDリスト
select_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND (area2 LIKE '%{area}%' OR area3 LIKE '%{area}%') AND id < 30435;".format(pre = prefecture, area = area)
area_id_list = myp_other_m.Area_id_List(select_area_id)
print("<h4>エリアIDの数：\t{}</h4>".format(len(area_id_list)))

## エリア内のレビューありスポットリスト
select_spot = "SELECT DISTINCT id,name,lat,lng,area_id,review FROM spot_mst WHERE area_id IN {} AND review!=0;".format(tuple(area_id_list))
spot_list = myp_other_m.SpotORReview_List(select_spot)
print("<h4>エリアスポット数(レビューあり)：\t{}</h4>".format(len(spot_list)))
# print("<h4>エリアスポット(Spot_id, Name, Lat, Lng, Area_id, Review)，(Areaレビューあり)：</h4>{}".format(spot_list))

## レビューリスト
spot_id_list = []
for i in range(len(spot_list)):
    spot_id_list.append(spot_list[i][0])
select_review = "SELECT spot_id,wakachi2 FROM review_all WHERE spot_id IN {} ORDER BY spot_id ASC;".format(tuple(spot_id_list))
review_list = myp_other_m.SpotORReview_List(select_review)
print("<h4>全スポットのレビューの数：\t{}</h4>".format(len(review_list)))

## スポット毎のレビュー
review_wkt_group_by = myp_other_m.EverySpot_Review(review_list)

## エリア内のスポットの全レビュー
review_wkt_all = myp_other_m.AllSpot_Review(review_list)

## 単語に重み付け(TFIDF)
review_wkt_all.insert(0,review_wkt_group_by[0])
words = myp_other_m.Tfidf(review_wkt_all)

## GoogleMapの表示
name,lat,lng = [],[],[]
cnt = 0
for i in range(len(spot_list)):
    if spot_list[i][2]!=0 and spot_list[i][3]!=0:
        name.append(spot_list[i][1])
        lat.append(str(spot_list[i][2]))
        lng.append(str(spot_list[i][3]))
        cnt += 1
    else:
        continue
## 中心座標
# coordinate = [sum(int(lat))/cnt,sum(int(lng))/cnt]
# print("<br><iframe width='1000' height='850' frameborder='1' scrolling='no' marginheight='0' marginwidth='0' src='http://maps.google.co.jp/maps?ll=" + str(coordinate[0])+ "," + str(coordinate[1]) + "&output=embed&t=m&z=13'></iframe>")

## DBにスポット名，座標を挿入
finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
sql_update = "UPDATE map_test SET finish_datetime='{finish}', spot_name='{spot_name}', lat='{lat}', lng='{lng}' where id = {record_id};".format(finish=finish_datetime, spot_name=','.join(name), lat=','.join(lat), lng=','.join(lng), record_id=record_id)
cur.execute(sql_update)
conn.commit()

html_map = u"""
<div id="map" style="width:100%; height:750px; margin: 0 8px 0 8px;"></div>
<script type="text/javascript" src="../../javascript/googlemap2.js"></script>
<script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBzLtrdLAR0doAuGVk0HDIRkZJ1CkmDelo&callback=initMap"></script>
<br></body></html>
"""
print(html_map)

## スポット座標 jsonファイルに書き出す
# dict = []
# for i in range(len(name)):
#     temp = {'name':name[i],'lat':lat[i],'lng':lng[i]}
#     dict.append(temp)
#     temp = {}
# print(dict)
# f = open("./json/output.json", "w")
# json.dump(dict, f, ensure_ascii=False)

# print("<br></body></html>")
