#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
from tqdm import tqdm
import datetime
import re, json, random, string
import numpy as np
import mypackage.other as myp_other
import mypackage.doc2vec_recommend as myp_doc_rec
import mypackage.tfidf as myp_tfidf
import mypackage.harmonic_mean as myp_hmean
import mypackage.normal_distribution_map_position as myp_norm_p
import mypackage.normal_distribution_map_line as myp_norm_l
import mypackage.normal_distribution_map_table as myp_norm_t

import MySQLdb
import os, sys ## 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

def Randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

## 承認コード，乱数生成
def Response_Random():
    json_random = {"randomname":""}
    random = Randomname(12)
    json_random["randomname"] = random
    return random,json_random

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
vis_name,vis_lat,vis_lng,vis_url,vis_description,vis_cate = [],[],[],[],[],[]
for i in range(len(visited_spot_list)):
    visited_spot_id_list.append(visited_spot_list[i][0])
    if visited_spot_list[i][2]!=0 and visited_spot_list[i][3]!=0:
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

############################################################
## DB挿入
############################################################
## ユーザ入力とDBヘ書き込む
sql_insert = "INSERT INTO analogy_master_feature(user_id, prefecture, area, start_datetime, history, orders) VALUES(%s,%s,%s,%s,%s,%s);"
cur.execute(sql_insert,(user_id, prefecture, area, start_datetime, history,orders))
conn.commit()

## ユーザの最新情報を得る
cur.execute("SELECT max(id) FROM analogy_master_feature WHERE user_id='{user}';".format(user = user_id))
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
unvisited_spot_list = []
for i in range(len(vis_cate)):
    select_unvisited_spot = "SELECT DISTINCT id,name,lat,lng,area_id,review,url,description,category1 FROM spot_mst2 WHERE area_id IN {area} AND review!=0 AND (lat!=0 or lng!=0) AND id NOT IN {vis} AND name NOT LIKE '%レンタ%' AND category1 LIKE '%{vis_cate}%' ORDER BY review DESC limit 12;".format(area=tuple(unvisited_area_id_list),vis=tuple(visited_spot_id_list),vis_cate=vis_cate[i])
    tmp = myp_other.spot_or_reviewlist(select_unvisited_spot)
    unvisited_spot_list.append(tmp)

# print(len(unvisited_spot_list), file=sys.stderr)
unvisited_spot_list_map_l,unvisited_spot_list_map_t,unvisited_spot_list_map_p = [],[],[]
for i in range(len(unvisited_spot_list)):
    n = 0
    unvisited_spot_list_map_p.extend(unvisited_spot_list[i][n:n+3])
    n = 3
    unvisited_spot_list_map_l.extend(unvisited_spot_list[i][n:n+3])
    n = 6
    unvisited_spot_list_map_t.extend(unvisited_spot_list[i][n:n+3])
if len(unvisited_spot_list_map_l) != len(unvisited_spot_list_map_t) or len(unvisited_spot_list_map_t) != len(unvisited_spot_list_map_p) or len(unvisited_spot_list_map_l) != len(unvisited_spot_list_map_p):
    a = min([len(unvisited_spot_list_map_l),len(unvisited_spot_list_map_t),len(unvisited_spot_list_map_p)])
    unvisited_spot_list_map_p = unvisited_spot_list_map_p[:a]
    unvisited_spot_list_map_l = unvisited_spot_list_map_l[:a]
    unvisited_spot_list_map_t = unvisited_spot_list_map_t[:a]


#################  map_line  #######################
#################  map_line  #######################
#################  map_line  #######################
## 未訪問エリア内スポットIDリスト
unvisited_spot_id_list = []
## GoogleMapの表示
unvis_name,unvis_lat,unvis_lng,unvis_url,unvis_description = [],[],[],[],[]
for i in range(len(unvisited_spot_list_map_l)):
    for j in range(len(unvisited_spot_list_map_l[i])):
        unvisited_spot_id_list.append(unvisited_spot_list_map_l[i][j][0])
        if unvisited_spot_list_map_l[i][j][2]!=0 and unvisited_spot_list_map_l[i][j][3]!=0:
            unvis_name.append(unvisited_spot_list_map_l[i][j][1])
            unvis_lat.append(str(unvisited_spot_list_map_l[i][j][2]))
            unvis_lng.append(str(unvisited_spot_list_map_l[i][j][3]))
            unvis_url.append(str(unvisited_spot_list_map_l[i][j][6]))
            unvis_description.append(str(unvisited_spot_list_map_l[i][j][7]))
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

try:
    json_data_map_line = myp_norm_l.calculation(vis_name,vis_lat,vis_lng,unvis_name,unvis_lat,unvis_lng,UtoV_top10_harmonic,record_id,unvis_url)
except:
    import traceback
    traceback.print_exc()


#################  map_position  #######################
#################  map_position  #######################
#################  map_position  #######################
## 未訪問エリア内スポットIDリスト
unvisited_spot_id_list = []
## GoogleMapの表示
unvis_name,unvis_lat,unvis_lng,unvis_url,unvis_description = [],[],[],[],[]
for i in range(len(unvisited_spot_list_map_p)):
    for j in range(len(unvisited_spot_list_map_p[i])):
        unvisited_spot_id_list.append(unvisited_spot_list_map_p[i][j][0])
        if unvisited_spot_list_map_p[i][j][2]!=0 and unvisited_spot_list_map_p[i][j][3]!=0:
            unvis_name.append(unvisited_spot_list_map_p[i][j][1])
            unvis_lat.append(str(unvisited_spot_list_map_p[i][j][2]))
            unvis_lng.append(str(unvisited_spot_list_map_p[i][j][3]))
            unvis_url.append(str(unvisited_spot_list_map_p[i][j][6]))
            unvis_description.append(str(unvisited_spot_list_map_p[i][j][7]))
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

try:
    json_data_map_position = myp_norm_p.calculation(vis_name,vis_lat,vis_lng,unvis_name,unvis_lat,unvis_lng,UtoV_top10_harmonic,record_id,unvis_url)
except:
    import traceback
    traceback.print_exc()




#################  map_table  #######################
#################  map_table  #######################
#################  map_table  #######################
## 未訪問エリア内スポットIDリスト
unvisited_spot_id_list = []
## GoogleMapの表示
unvis_name,unvis_lat,unvis_lng,unvis_url,unvis_description = [],[],[],[],[]
for i in range(len(unvisited_spot_list_map_t)):
    for j in range(len(unvisited_spot_list_map_t[i])):
        unvisited_spot_id_list.append(unvisited_spot_list_map_t[i][j][0])
        if unvisited_spot_list_map_t[i][j][2]!=0 and unvisited_spot_list_map_t[i][j][3]!=0:
            unvis_name.append(unvisited_spot_list_map_t[i][j][1])
            unvis_lat.append(str(unvisited_spot_list_map_t[i][j][2]))
            unvis_lng.append(str(unvisited_spot_list_map_t[i][j][3]))
            unvis_url.append(str(unvisited_spot_list_map_t[i][j][6]))
            unvis_description.append(str(unvisited_spot_list_map_t[i][j][7]))
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

try:
    json_data_map_table = myp_norm_t.calculation(vis_name,vis_lat,vis_lng,unvis_name,unvis_lat,unvis_lng,UtoV_top10_harmonic,record_id,unvis_url)
except:
    import traceback
    traceback.print_exc()

random,json_random = Response_Random()
json_data = [json_data_map_position] + [json_data_map_line] + [json_data_map_table] + [json_random]

finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
sql_insert = "UPDATE analogy_master_feature SET category='{cate}', code='{rand}',finish_datetime='{finish}' WHERE id = {record_id};".format(cate='，'.join(vis_cate),rand=random,finish=finish_datetime,record_id=record_id)
cur.execute(sql_insert)
conn.commit()
# print(json_data, file=sys.stderr)
print(json.dumps(json_data))
