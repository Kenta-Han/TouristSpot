#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
from tqdm import tqdm
import datetime
import re
import json
import mypackage.other as myp_other
import mypackage.doc2vec_recommend as myp_doc_rec
import mypackage.tfidf as myp_tfidf
import mypackage.harmonic_mean as myp_hmean
import mypackage.response as myp_res

import MySQLdb
import os, sys ## 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

cgitb.enable()

html_body = u"""
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <link href="../../data/stylesheet_analogy_deim_map.css" rel="stylesheet" type="text/css" />
     <script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
    <link type="text/css" rel="stylesheet" href="http://code.jquery.com/ui/1.10.3/themes/cupertino/jquery-ui.min.css" />
    <script type="text/javascript" src="http://code.jquery.com/ui/1.12.1/jquery-ui.min.js"></script>
    <title>観光スポット間の関係を想起する情報の提示に関する実験</title>
</head>
<body>
    <header><h1>システムBの説明</h1></header>
    <h2>入力したスポットに基づいて訪問したいエリアのスポットが検索されました．</h2>
"""
print(html_body)

form = cgi.FieldStorage()
user_id = form.getvalue('user_id') ## CrowdWorksID
prefecture2 = form.getvalue('prefecture2') ## 都道府県
area2 = form.getvalue('area2') ## エリア
history = form.getvalue('visited')
start_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

############################################################
## 既訪問スポット情報
############################################################
## 既訪問を利用
history_list = []
user_spot = [] ## 履歴スポット
history2 = "---".join(history)
history_list = re.split("---", history2)
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
sql_insert = "INSERT INTO analogy_deim_map(user_id, prefecture, area, start_datetime, history) VALUES(%s,%s,%s,%s,%s);"
cur.execute(sql_insert,(user_id, prefecture2, area2, start_datetime, history2))
conn.commit()
## ユーザの最新情報を得る
cur.execute("SELECT max(id) FROM analogy_deim_map WHERE user_id='{user}' and prefecture='{pre}';".format(user = user_id, pre = prefecture2))
record_id = cur.fetchone()[0]


############################################################
## 未訪問エリア情報
############################################################
## 未訪問エリアIDリスト
if area2 == "None":
    select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND id < 30435;".format(pre = prefecture2)
    unvisited_area_id_list = myp_other.Area_id_List(select_unvisited_area_id)
else:
    select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND (area2 LIKE '%{area}%' OR area3 LIKE '%{area}%') AND id < 30435;".format(pre = prefecture2, area = area2)
    unvisited_area_id_list = myp_other.Area_id_List(select_unvisited_area_id)

## 未訪問エリア内(レビュー and [lat or lng])ありスポット
select_unvisited_spot = "SELECT DISTINCT id,name,lat,lng,area_id,review,url FROM spot_mst WHERE area_id IN {area} AND review>=10 AND (lat!=0 or lng!=0) AND id NOT IN {vis} ORDER BY review DESC limit 20;".format(area=tuple(unvisited_area_id_list),vis=tuple(visited_spot_id_list))
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
visited_tfidf = myp_tfidf.Tfidf(visited_spot_reviews)

## 未訪問スポットの単語に重みつけ
select_unvisited_spot_reviews = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(unvisited_spot_id_list))
unvisited_spot_reviews = myp_tfidf.Spot_List_TFIDF(select_unvisited_spot_reviews)
unvisited_tfidf = myp_tfidf.Tfidf(unvisited_spot_reviews)

## 既訪問と未訪問スポット特徴語TOP10(調和平均)
UtoV_top10_harmonic = myp_hmean.Sort_TFIDF_UtoV_Harmonic(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,result_UtoV_top)

## 承認コード作成
random = myp_res.Response_Random()

## レスポンス作成，mysqlに入れるためのカラム内容作成
all_json,sql_unvis,sql_vis,sql_cossim,sql_lat,sql_lng,sql_word = myp_res.Response_Harmonic(UtoV_top10_harmonic[:15],name,lat,lng,url)

finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
sql_update = "UPDATE analogy_deim_map SET unvis_name='{unv}', vis_name='{vis}', cossim='{cos}', word='{word}', unvis_lat='{lat}', unvis_lng='{lng}', word='{word}',finish_datetime='{finish}',code='{code}',method='AtoB_B' WHERE id = {record_id};".format(unv='，'.join(sql_unvis), vis='，'.join(sql_vis), cos='，'.join(sql_cossim), word=sql_word, lat='，'.join(sql_lat), lng='，'.join(sql_lng), finish=finish_datetime, record_id=record_id, code=random)
cur.execute(sql_update)
conn.commit()

if area2 == "None":
    print("<h2>訪問したいスポットエリア："+str(prefecture2) + "</h2>")
else :
    print("<h2>訪問したいスポットエリア："+str(prefecture2) + "--" + str(area2) + "</h2>")
print("<h2>見つけたスポット数：" + str(len(all_json)) + "件<h2>")
if len(all_json) != 0 :
    html_body2 = u"""
        <h2>マップ上のアイコンをクリックすると各スポットの詳細情報（スポット名，関連する入力スポット名，関係を説明するキーワード）が表示されます．<br>検索結果が密集していたり，画面外にもあるかもしれません．<br>ズームイン/アウトしながら見てください．</h2>
        <div id='map'>
            <iframe src='https://www.google.com/maps/embed?pb=!1m16!1m12!1m3!1d13271.045898004142!2d139.69292184601608!3d35.690589482984!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!2m1!1z5bel5a2m6Zmi5aSn5a2m!5e0!3m2!1sja!2sjp!4v1541602248205' width='100%'' height='750' frameborder='0' style='border:0' allowfullscreen></iframe>
        </div>
        <script async defer src='https://maps.googleapis.com/maps/api/js?key=AIzaSyBzLtrdLAR0doAuGVk0HDIRkZJ1CkmDelo'></script>

        <script type='text/javascript'>
        var map;
        var marker = [];
        var infoWindow = [];
        function initMap(data) {
            var markerData = data;
            var cnt = 0, sum_lat = 0, sum_lng = 0;
            for (var i = 0; i < markerData.length; i++) {
                sum_lat = sum_lat + Number(markerData[i]['unvis_lat']);
                sum_lng = sum_lng + Number(markerData[i]['unvis_lng']);
                cnt += 1;
            }
            map = new google.maps.Map(document.getElementById('map'), {
                center: {lat: sum_lat / cnt, lng: sum_lng / cnt},
                zoom: 12
            });
            for (var i = 0; i < markerData.length; i++) {
                markerLatLng = new google.maps.LatLng({
                    lat: Number(markerData[i]["unvis_lat"]),
                    lng: Number(markerData[i]["unvis_lng"])
                });
                marker[i] = new google.maps.Marker({
                    position: markerLatLng,
                    map: map
                });
                infoWindow[i] = new google.maps.InfoWindow({
                    content: "<table border='1' id='window'><tr><th>スポット名</th><td><a href='" + markerData[i]["url"] + "'>" + markerData[i]["unvis_name"] + "</a></td></tr><tr><th>関連する入力スポット名</th><td>" + markerData[i]["vis_name"] + "</td</tr><tr><th>関係を説明するキーワード</th><td>" + markerData[i]["word"] + "</td></tr></table>"
                });
                markerEvent(i);
            }
        }
        var currentInfoWindow = null;
        function markerEvent(i) {
            marker[i].addListener('click', function() {
                if (currentInfoWindow) {
                    currentInfoWindow.close();
                }
                infoWindow[i].open(map, marker[i]);
                currentInfoWindow = infoWindow[i];
            });
        }
        </script>
    """
    print(html_body2)
    print("<script type='text/javascript'>window.onload = (function() {initMap("+str(all_json)+")});</script>")

print("<h1>承認コード(システムB)：<span id='code'>"+str(random)+"</span></h1>")
html_body3 = u"""
    <p style='text-align:center;color:#FF0000;'>「次へ」行く前に，承認コードと未訪問スポット名をコピーしてCrowdWorksの対応するタスクに貼り付けてください．<br>(見つけたスポット数が0件の時「なし」で回答してください)</p>
    <form action='../../index.html' style='text-align:center;'>
        <input type='submit' id='start' value='次へ' />
    </form>
    </body>
    </html>
"""
print(html_body3)
