#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import datetime
from tqdm import tqdm
import mypackage.other_def as myp_other
# import pandas as pd

import os, sys # 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

## ====== ユーザ入力とDBヘ書き込む ======
form = cgi.FieldStorage()
user_id = form.getvalue('user_id') ##CrowdWorksID
prefecture = form.getvalue('prefecture_name') ##都道府県
area = form.getvalue('area_name') ##エリア
start_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

sql_insert = "INSERT INTO map_test(user_id, prefecture, area, start_datetime) VALUES(%s,%s,%s,%s);"
cur.execute(sql_insert,(user_id, prefecture, area, start_datetime))
conn.commit()

## ユーザの最新情報
cur.execute("SELECT max(id) FROM map_test WHERE user_id='{user}';".format(user = user_id))
record_id = cur.fetchone()[0]
## ====== ユーザ入力とDBヘ書き込む〆 ======

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='../../data/new_stylesheet.css' rel='stylesheet' type='text/css' />
<title>観光体験マップ選択</title>
</head>

<body>
<header><h1 class='title'>観光体験マップ</h1></header>

"""
print(html_body)
## ====== ユーザ履歴を使って各スポットの特徴を出す ======
print("<h1>ユーザ履歴情報</h1>")
# df = pd.read_sql("SELECT id,name,lat,lng,area_id,review FROM spot_mst WHERE area_id BETWEEN 17698 AND 18516 AND review != 0 ORDER BY RAND() LIMIT 5;",conn)
# # print("<h4>ユーザ履歴スポット(Spot_id, Name, Lat, Lng, Area_id, Review)：</h4>\n{lat}".format(lat = df[["lat"]]))

## 東京23区 BETWEEN 17698 AND 18516
select_user_spot = "SELECT id,name,lat,lng,area_id,review FROM spot_mst WHERE area_id BETWEEN 17698 AND 18516 AND review != 0 ORDER BY RAND() LIMIT 5;"
user_spot_list = myp_other.SpotORReview_List(select_user_spot)
print("<h4>ユーザ履歴スポット(Spot_id, Name, Lat, Lng, Area_id, Review)：</h4>\n{spot}".format(spot = user_spot_list))
print("<h4>ユーザ履歴スポット数：\t{num}</h4>".format(num = len(user_spot_list)))

## ====== レビューリスト ======
user_spot_id_list = []
for i in range(len(user_spot_list)):
    user_spot_id_list.append(user_spot_list[i][0])
select_user_review = "SELECT spot_id,wakachi2 FROM review_all WHERE spot_id IN {spotid} ORDER BY spot_id ASC;".format(spotid = tuple(user_spot_id_list))
user_review_list = myp_other.SpotORReview_List(select_user_review)
print("<h4>レビューの数：\t{num}</h4>".format(num = len(user_review_list)))
## ====== レビューリスト〆 ======

## ====== スポット毎のレビュー(ユーザ履歴で各スポットの特徴を出す) ======
user_review_wkt_group_by = myp_other.EverySpot_Review(user_review_list)
## ==== ユーザ履歴のスポットの全レビュー(ユーザ履歴で各スポットの特徴を出す) ====
user_review_wkt_all = myp_other.AllSpot_Review(user_review_list)

## ====== 単語に重み付け(TFIDF) ======
tfidf_list = []
for i in tqdm(range(len(user_review_wkt_group_by))):
    user_review_wkt_all.insert(0,user_review_wkt_group_by[i])
    user_words = myp_other.Tfidf(user_review_wkt_all)
    tfidf_list.append(user_words[0])
    user_words = 0
user_words_all = myp_other.Change_To_Dic(tfidf_list)

## ====== スポットリスト ======
spot_list = []
for i in range(len(user_spot_list)):
    spot_list.append(user_spot_list[i][1])

## ====== スポット間の類似度算出 ======
print("<h2>類似度</h2>")
for i in range(len(user_words_all[0])):
    temp = [user_words_all[0][i]] + user_words_all[0]
    print("<h3>= 「" + spot_list[i] + "」と履歴中のスポット類似度 =</h3>")
    cos_result = myp_other.Recommend_All(temp,spot_list)
    temp = 0

## ====== ユーザ履歴から代表的なスポットとそれを表す特徴語を出す ======

## ====== ユーザ履歴を使って各スポットの特徴を出す〆 ======


## ====== エリア内で各スポットの特徴を出す ======
print("<br><h1>エリア内情報</h1>")
## ====== エリアIDリスト ======
select_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND (area2 LIKE '%{area}%' OR area3 LIKE '%{area}%') AND id < 30435;".format(pre = prefecture, area = area)
area_id_list = myp_other.Area_id_List(select_area_id)
print("<h4>エリアIDリスト数：\t{num}<//h4>".format(num = len(area_id_list)))
## ====== エリアIDリスト〆 ======

## ====== エリア内のレビューありスポットリスト ======
select_spot = "SELECT DISTINCT id,name,lat,lng,area_id,review FROM spot_mst WHERE area_id IN {area_id} AND review!=0;".format(area_id = tuple(area_id_list))
spot_list = myp_other.SpotORReview_List(select_spot)
print("<h4>エリア内のレビューありスポットリスト数：\t{num}</h4>".format(num = len(spot_list)))
# print("<h4>エリア内のレビューありスポットリスト：\t{name}</h4>".format(name = spot_list))
## ====== エリア内のレビューありスポットリストリスト〆 ======

## ====== レビューリスト ======
spot_id_list = []
for i in range(len(spot_list)):
    spot_id_list.append(spot_list[i][0])
select_review = "SELECT spot_id,wakachi2 FROM review_all WHERE spot_id IN {spotid} ORDER BY spot_id ASC;".format(spotid = tuple(spot_id_list))
review_list = myp_other.SpotORReview_List(select_review)
print("<h4>レビューの数：\t{num}</h4>".format(num = len(review_list)))
## ====== レビューリスト〆 ======

## ====== スポット毎のレビュー(エリア内で各スポットの特徴を出す) ======
review_wkt_group_by = myp_other.EverySpot_Review(review_list)
## ====== エリア内のスポットの全レビュー(エリア内で各スポットの特徴を出す) ======
review_wkt_all = myp_other.AllSpot_Review(review_list)
## ====== 単語に重み付け(TFIDF) ======
review_wkt_all.insert(0,review_wkt_group_by[0])
words = myp_other.Tfidf(review_wkt_all)
## ====== エリア内で各スポットの特徴を出す〆 ======

print("<br><h1>マップエリア</h1>")
print("<iframe width='700' height='550' frameborder='1' scrolling='no' marginheight='0' marginwidth='0' src='http://maps.google.co.jp/maps?ll=36.578268,136.648035&q=金沢駅&output=embed&t=m&z=13'></iframe>")

finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
sql_update = "UPDATE map_test SET finish_datetime='{finish}' where id = {record_id};".format(finish = finish_datetime,record_id = record_id)
cur.execute(sql_update)
conn.commit()

print("<br></body></html>")
