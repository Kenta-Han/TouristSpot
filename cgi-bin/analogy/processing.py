#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
from tqdm import tqdm
import datetime
import re
import json
import mypackage.other as myp_other
import mypackage.category as myp_cate
import mypackage.doc2vec_recommend as myp_doc_rec
import mypackage.tfidf as myp_tfidf
import mypackage.mean as myp_mean
import mypackage.harmonic_mean as myp_hmean
import mypackage.response as myp_res

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
    user_spot.append(cur.fetchone())
visited_spot_id_list = []
visited_spot_url_list = []
for i in range(len(user_spot)):
    visited_spot_id_list.append(user_spot[i][0])
    visited_spot_url_list.append(user_spot[i][5])


############################################################
## DB挿入
############################################################
## ユーザ入力とDBヘ書き込む
sql_insert = "INSERT INTO analogy(user_id, prefecture, area, start_datetime, history) VALUES(%s,%s,%s,%s,%s);"
cur.execute(sql_insert,(user_id, prefecture, area, start_datetime, history))
conn.commit()

## ユーザの最新情報を得る
cur.execute("SELECT max(id) FROM analogy WHERE user_id='{user}';".format(user = user_id))
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
# print("<h4>エリアIDの数：\t{}</h4>".format(len(unvisited_area_id_list)))

## 未訪問エリア内(レビュー and [lat or lng])ありスポット
# select_unvisited_spot = "SELECT DISTINCT id,name,lat,lng,area_id,review FROM spot_mst WHERE area_id IN {area} AND review!=0 AND (lat!=0 or lng!=0) AND id NOT IN {vis} ORDER BY RAND() LIMIT 20;".format(area=tuple(unvisited_area_id_list),vis=tuple(visited_spot_id_list))
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

# [東京都庁舎展望室,浅草寺,明治神宮,新宿御苑,皇居東御苑]
# unvisited_spot_id_list = ['spt_13104aj2200025349','spt_13106ag2130012302','spt_13113ag2130014473','spt_13104ah2140016473','spt_13101ah2140016178']


############################################################
## 絶対的な特徴（カテゴリ）
############################################################
category_top10 = myp_cate.Category_Main(visited_spot_id_list,unvisited_spot_id_list,record_id)

## レスポンス作成，mysqlに入れるためのカラム内容作成
sql_unvis_c,sql_vis_c,sql_word_c,json_category = myp_res.Response_Category(category_top10[:5])

sql_update = "UPDATE analogy SET unvis_name_c='{unv_c}', vis_name_c='{vis_c}', word_c='{word_c}' WHERE id = {record_id};".format(unv_c='，'.join(sql_unvis_c), vis_c='，'.join(sql_vis_c), word_c=sql_word_c, record_id=record_id)
cur.execute(sql_update)
conn.commit()


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
## 絶対的な特徴（特徴ベクトル）
############################################################
visited_spot_name_all,unvisited_spot_name_all = [],[]
visited_spot_review_all,unvisited_spot_review_all = [],[]
for i in range(len(visited_spot_vectors)):
    visited_spot_name_all.append(visited_spot_vectors[i][1])
    visited_spot_review_all.append(list(visited_spot_vectors[i][2:-1]))
for i in range(len(unvisited_spot_vectors)):
    unvisited_spot_name_all.append(unvisited_spot_vectors[i][1])
    unvisited_spot_review_all.append(list(unvisited_spot_vectors[i][2:-1]))
# result_VtoU_top,result_UtoV_top = myp_doc_rec.Recommend_All(visited_spot_name_all,unvisited_spot_name_all,visited_spot_review_all,unvisited_spot_review_all)
result_UtoV_top = myp_doc_rec.Recommend_All(visited_spot_name_all,unvisited_spot_name_all,visited_spot_review_all,unvisited_spot_review_all)

## 類似度高い順でソート
# result_VtoU_top.sort(key=lambda x:x[1][1],reverse=True)
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
# VtoU_top10_Feature = myp_hmean.Sort_TFIDF_VtoU_Harmonic(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,result_VtoU_top)
UtoV_top10_Feature = myp_hmean.Sort_TFIDF_UtoV_Harmonic(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,result_UtoV_top)

## レスポンス作成，mysqlに入れるためのカラム内容作成
sql_unvis_f,sql_vis_f,sql_cossim_f,sql_lat_f,sql_lng_f,sql_word_f,json_feature = myp_res.Response_Feature(UtoV_top10_Feature[:5],name,lat,lng,url)

sql_update = "UPDATE analogy SET unvis_name_f='{unv_f}', vis_name_f='{vis_f}', cossim_f='{cos_f}', word_f='{word_f}', unvis_lat_f='{lat_f}', unvis_lng_f='{lng_f}' WHERE id = {record_id};".format(unv_f='，'.join(sql_unvis_f), vis_f='，'.join(sql_vis_f), cos_f='，'.join(sql_cossim_f), word_f=sql_word_f, lat_f='，'.join(sql_lat_f), lng_f='，'.join(sql_lng_f), record_id=record_id)
cur.execute(sql_update)
conn.commit()

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
# result_VtoU_top,result_UtoV_top = myp_doc_rec.Recommend_All(visited_spot_name_all,unvisited_spot_name_all,visited_spot_review_all,unvisited_spot_review_all)
result_UtoV_top = myp_doc_rec.Recommend_All(visited_spot_name_all,unvisited_spot_name_all,visited_spot_review_all,unvisited_spot_review_all)

## 類似度高い順でソート
# result_VtoU_top.sort(key=lambda x:x[1][1],reverse=True)
result_UtoV_top.sort(key=lambda x:x[1][1],reverse=True)

## 既訪問スポットの単語に重みつけ
select_visited_spot_reviews = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(visited_spot_id_list))
visited_spot_reviews = myp_tfidf.Spot_List_TFIDF(select_visited_spot_reviews)
visited_tfidf,visited_mean = myp_tfidf.Tfidf_HM(visited_spot_reviews)

## 未訪問スポットの単語に重みつけ
select_unvisited_spot_reviews = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(unvisited_spot_id_list))
unvisited_spot_reviews = myp_tfidf.Spot_List_TFIDF(select_unvisited_spot_reviews)
unvisited_tfidf,unvisited_mean = myp_tfidf.Tfidf_HM(unvisited_spot_reviews)

## 既訪問と未訪問スポット特徴語TOP10(相加平均)
# VtoU_top10_mean = myp_mean.Sort_TFIDF_VtoU(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_VtoU_top)
UtoV_top10_mean = myp_mean.Sort_TFIDF_UtoV(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_UtoV_top)

## 既訪問と未訪問スポット特徴語TOP10(調和平均)
# VtoU_top10_harmonic = myp_hmean.Sort_TFIDF_VtoU_Harmonic(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,result_VtoU_top)
UtoV_top10_harmonic = myp_hmean.Sort_TFIDF_UtoV_Harmonic(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,result_UtoV_top)

## レスポンス作成，mysqlに入れるためのカラム内容作成
sql_unvis_h,sql_vis_h,sql_cossim_h,sql_lat_h,sql_lng_h,sql_word_h,json_harmonic = myp_res.Response_Harmonic(UtoV_top10_harmonic[:5],name,lat,lng,url)
sql_word_m,json_mean = myp_res.Response_Mean(UtoV_top10_mean[:5],name,url)
random,json_random = myp_res.Response_Random()

syori_finishtime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
sql_update = "UPDATE analogy SET code='{code}', unvis_name_h='{unv_h}', vis_name_h='{vis_h}', cossim_h='{cos_h}', word_h='{word_h}', unvis_lat_h='{lat_h}', unvis_lng_h='{lng_h}', word_m='{word_m}',syori_finishtime='{finish}' WHERE id = {record_id};".format(code=random, unv_h='，'.join(sql_unvis_h), vis_h='，'.join(sql_vis_h), cos_h='，'.join(sql_cossim_h), word_h=sql_word_h, lat_h='，'.join(sql_lat_h), lng_h='，'.join(sql_lng_h), word_m=sql_word_m,finish=syori_finishtime, record_id=record_id)
cur.execute(sql_update)
conn.commit()

## レスポンス作成（送信）
myp_res.Response(json_category,json_feature,json_harmonic,json_mean,json_random,record_id)


############################################################
## DBにデータ挿入
############################################################
# sql_update = "UPDATE analogy SET code='{code}', unvis_name_c='{unv_c}', vis_name_c='{vis_c}', word_c='{word_c}', unvis_name_f='{unv_f}', vis_name_f='{vis_f}', cossim_f='{cos_f}', word_f='{word_f}', unvis_lat_f='{lat_f}', unvis_lng_f='{lng_f}', unvis_name_h='{unv_h}', vis_name_h='{vis_h}', cossim_h='{cos_h}', word_h='{word_h}', unvis_lat_h='{lat_h}', unvis_lng_h='{lng_h}', word_m='{word_m}'  WHERE id = {record_id};".format(code=random, unv_c='，'.join(sql_unvis_c), vis_c='，'.join(sql_vis_c), word_c=sql_word_c, unv_f='，'.join(sql_unvis_f), vis_f='，'.join(sql_vis_f), cos_f='，'.join(sql_cossim_f), word_f=sql_word_f, lat_f='，'.join(sql_lat_f), lng_f='，'.join(sql_lng_f), unv_h='，'.join(sql_unvis_h), vis_h='，'.join(sql_vis_h), cos_h='，'.join(sql_cossim_h), word_h=sql_word_h, lat_h='，'.join(sql_lat_h), lng_h='，'.join(sql_lng_h), word_m=sql_word_m, record_id=record_id)
# cur.execute(sql_update)
# conn.commit()
