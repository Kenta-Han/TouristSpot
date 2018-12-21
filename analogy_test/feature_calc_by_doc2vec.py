#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
from tqdm import tqdm
import numpy as np
from pprint import pprint
from sklearn.decomposition import PCA ## scikit-learnのPCAクラス
import pandas as pd ## 便利なDataFrameを使うためのライブラリ
import matplotlib.pyplot as plt
import mypackage.package_01 as myp_pk01
import random,re

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

##########################
##########################
# ## [建長寺,高徳院（鎌倉大仏）,長谷寺（長谷観音）,鶴岡八幡宮,龍口寺]
# visited_spot_id_list = ['spt_14204ag2130011936','spt_14204ag2130009759','spt_14204ag2130009778','spt_14204ag2130012949','spt_14205ag2130015243']

## spt_14205ag2130015243 江島神社

## [伏見稲荷大社,鹿苑寺（金閣寺）,龍安寺,清水寺,八坂神社]
# visited_spot_id_list = ['spt_26109ag2130015470','spt_26101ag2130014551','spt_26108ag2130015438','spt_26105ag2130012063','spt_26105ag2130010617']

## 浅草寺，小田原城址公園，伏見稲荷大社，奈良公園，三島スカイウォーク
# visited_spot_id_list = ['spt_13106ag2130012302','spt_14206ah3330042448','spt_26109ag2130015470','spt_29201ah3330042300','spt_guide000000183988']
# visited_spot_id_list = ['spt_01214ca3280039313','spt_01214cc3310040156','spt_01396ca3372034772']

#['東京ディズニーランド(R)','東京タワー大展望台','新宿御苑','東京スカイツリー','明治神宮']
visited_spot_id_list = ['spt_12227cc3540060301','spt_13103ad3350046722','spt_13104ah2140016473','spt_13107ad3352086481','spt_13113ag2130014473']
# unvisited_spot_id_list = []


# ## [海遊館,天保山大観覧車,大阪城公園,USJ,天王寺動物園]
unvisited_spot_id_list = ['spt_27107cc3320040646','spt_27107ad3352003168','spt_27128ah3330042284','spt_guide000000184294','spt_27109ae3312015930']

# # ## [東京都庁舎展望室,浅草寺,明治神宮,新宿御苑,皇居東御苑]
# unvisited_spot_id_list = ['spt_13104aj2200025349','spt_13106ag2130012302','spt_13113ag2130014473','spt_13104ah2140016473','spt_13101ah2140016178']
#
# x = ['spt_45441ab2040005841','spt_45441ag2130011686','spt_45441ag2130015984','spt_45441cc3292007062','spt_45441ab2040005810','spt_43428ah3330044381','spt_guide000000167560','spt_43201af2120008919','spt_27111ad3352015941','spt_27107cc3320040646','spt_27128ad2250133278','spt_27128ah3330042284','spt_27127aj2200023829','spt_29201ag2130010937','spt_29201ah3330042300','spt_29201ae2180021457','spt_29201ag2130012119','spt_26204ag2130010639','spt_26109ag2130015470','spt_26107ag2130010579','spt_26105ag2130013629','spt_26105ag2130012063','spt_guide000000150273','spt_26105ag2130010617','spt_26102ag2130014838','spt_26101ag2130014551','spt_26108ag2130015438','spt_26108ag2130010605','spt_26108ag2130015316','spt_26108ah3330042504','spt_18361ab2050006586','spt_guide000000119003','spt_17201ag2130012974','spt_17201aj2200024669','spt_17201ag2130013930','spt_17201af2122018403','spt_17201ah2140016713','spt_17201aj2200023579','spt_22208ab2010003059','spt_22328ab2040005653','spt_guide000000179905','spt_22306ab2070007831','spt_guide000000183988','spt_14206af2120008936','spt_14206ah3330042448','spt_14206ah3330041190','spt_14382ee4610068856','spt_14382ab2020141656','spt_14382ag2130013396','spt_14382cb3410089132','spt_14382cc3300033858','spt_14382ac2100134144','spt_14205ad3352011278','spt_14205ab2050006540','spt_14205ab2050129880','spt_14205ag2130009779','spt_14204ag2130012949','spt_13104ah3330041099','spt_13104ah2140016473','spt_13106ag2130012302','spt_13103ad3350046722','spt_13107ad3352086481','spt_13106cc3310040182','spt_13101ah2140016178','spt_13105cc3540060470','spt_13102ah2140016179','spt_13106ah3330041103','spt_12227cc3540155509','spt_12227cc3540060301']
# #
# visited_spot_id_list = random.sample(x,5)

# unvisited_spot_id_list = random.sample(x,5)

#############################################################
## 絶対的な特徴（カテゴリ）
#############################################################
def Make_History_List(history):
    all = []
    spot = []
    area = []
    for i in range(len(history)):
        temp = "%"+ history[i] +"%"
        all.append(temp)
        temp = 0
    spot.append(all[0::2])
    area.append(all[1::2])
    return spot,area

history = ["新東京ゴルフクラブ---茨城","東京ディズニーランド(R)---千葉","東京ディズニーシー(R)---千葉","千代田区観光協会---東京"]
history_list = []
user_spot = [] ## 履歴スポット
history = "---".join(history)
history_list = re.split("---", history)
like_spot_list,like_area_list = Make_History_List(history_list)
for i in range(len(like_spot_list[0])):
    select_user_history = "SELECT id,name,lat,lng,area_id,url from spot_mst where name like '{spot}' AND address like '{area}' AND review=(SELECT max(review) FROM spot_mst WHERE name like '{spot}' AND address like '{area}' AND review != 0);".format(spot=like_spot_list[0][i],area=like_area_list[0][i])
    cur.execute(select_user_history)
    spot_data = cur.fetchone()
    if spot_data is None:
        continue
    else:
        user_spot.append(spot_data)
print(user_spot)
visited_spot_id_list = []
visited_spot_url_list = []
for i in range(len(user_spot)):
    visited_spot_id_list.append(user_spot[i][0])
    visited_spot_url_list.append(user_spot[i][5])
print(visited_spot_id_list)

# def SpotORReview_List(spot):
#     spot_list = []
#     cur.execute(spot)
#     for i in cur:
#         spot_list.append([i])
#     return spot_list
#
# def Area_id_List(area):
#     area_id_list = []
#     cur.execute(area)
#     for i in cur:
#         area_id_list.append(i[0])
#     return area_id_list
#
# prefecture = "石川"
# area = "金沢"
#
# if area == None:
#     select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND id < 30435;".format(pre = prefecture)
#     unvisited_area_id_list = Area_id_List(select_unvisited_area_id)
#     unvisited_area_id_list = Area_id_List(select_unvisited_area_id)
# else:
#     select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND (area2 LIKE '%{area}%' OR area3 LIKE '%{area}%') AND id < 30435;".format(pre = prefecture, area = area)
#     unvisited_area_id_list = Area_id_List(select_unvisited_area_id)
#
# ## 未訪問エリア内(レビュー and [lat or lng])ありスポット
# select_unvisited_spot = "SELECT DISTINCT id,name,lat,lng,area_id,review FROM spot_mst WHERE area_id IN {} AND review!=0 AND(lat!=0 or lng!=0);".format(tuple(unvisited_area_id_list))
# unvisited_spot_list = SpotORReview_List(select_unvisited_spot)
#
# ## 未訪問エリア内スポットIDリスト
# unvisited_spot_id_list = []
# ## GoogleMapの表示
# name,lat,lng = [],[],[]
# for i in range(len(unvisited_spot_list)):
#     for j in range(len(unvisited_spot_list[i])):
#         unvisited_spot_id_list.append(unvisited_spot_list[i][j][0])
#         if unvisited_spot_list[i][j][2]!=0 and unvisited_spot_list[i][j][3]!=0:
#             name.append(unvisited_spot_list[i][j][1])
#             lat.append(str(unvisited_spot_list[i][j][2]))
#             lng.append(str(unvisited_spot_list[i][j][3]))
#         else:
#             continue
#
# bytesymbols = re.compile("[!-/:-@[-`{-~\d]") ## 半角記号，数字\d
#
#
# def Category_Data(data):
#     spot = []
#     for i in range(len(data)):
#         temp = []
#
#         select_category = "SELECT category_id FROM spot_category WHERE id='{}';".format(data[i])
#         cur.execute(select_category)
#         try:
#             category = cur.fetchone()[0]
#         except TypeError:
#             category = None
#
#         select_season = "SELECT temp.season4 FROM (SELECT season4, count(*) cnt2 FROM review_all WHERE spot_id='{id}' GROUP BY season4) temp WHERE temp.cnt2 = (SELECT max(cnt) FROM (SELECT season4, count(*) AS cnt,season4 is not null AS nu FROM review_all WHERE spot_id='{id}' GROUP BY season4) num WHERE nu='1');".format(id=data[i])
#         cur.execute(select_season)
#         try:
#             season = cur.fetchone()[0]
#         except TypeError:
#             season = None
#
#         select_duration = "SELECT temp.duration FROM (SELECT duration, count(*) cnt2 FROM review_all WHERE spot_id='{id}' GROUP BY duration) temp WHERE temp.cnt2 = (SELECT max(cnt) FROM (SELECT duration, count(*) AS cnt,duration is not null AS nu FROM review_all WHERE spot_id='{id}' GROUP BY duration) num WHERE nu='1');".format(id=data[i])
#         cur.execute(select_duration)
#         try:
#             duration = cur.fetchone()[0]
#         except TypeError:
#             duration = None
#
#         temp.append([data[i],category,season,duration])
#         spot.extend(temp)
#     return spot
#
# ## レベルに応じて類似スポットセットを作成
# def Spot_set_by_level(cate_vispot,cate_unspot):
#     # level1,level2,level3 = [],[],[]
#     level1,level2,level3 = [],[],[]
#     for i in range(len(cate_unspot)):
#         for j in range(len(cate_vispot)):
#             if cate_unspot[i][1] == cate_vispot[j][1]:
#                 if cate_unspot[i][2] == cate_vispot[j][2]:
#                     if cate_unspot[i][3] == cate_vispot[j][3]:
#                         level3.append([cate_unspot[i][0],cate_vispot[j][0]])
#                     else:
#                         level2.append([cate_unspot[i][0],cate_vispot[j][0]])
#                 else:
#                     level1.append([cate_unspot[i][0],cate_vispot[j][0]])
#             else:
#                 continue
#     return level1,level2,level3
#
# ## 分かち書きのデータを抽出
# def Select_Review(data):
#     review_by_spot = []
#     set = []
#     for i in range(len(data)):
#         temp = []
#         select = "SELECT name,wakachi_neologd4 FROM review_all WHERE spot_id IN {};".format(tuple(data[i]))
#         cur.execute(select)
#         for j in cur:
#             temp.append(list(j))
#         set.append(temp)
#     review_by_spot.extend(set)
#     return review_by_spot
#
# # どのレベルまでのスポットセットを選択
# def Level(level1,level2,level3):
#     if level3 != []:
#         review_by_spot = Select_Review(level3)
#         level = level3
#     else:
#         if level2 != []:
#             review_by_spot = Select_Review(level2)
#             level = level2
#         else:
#             if level1 != []:
#                 review_by_spot = Select_Review(level1)
#                 level = level1
#             else:
#                 review_by_spot = []
#                 level = 0
#     return level,review_by_spot
#
# ## (類似スポット)単語の出現回数をカウント
# def Count_word(data):
#     result = []
#     for i in range(len(data)):
#         temp = []
#         for j in range(2):
#             moji =",".join(data[i][j])
#             ## counting
#             words = {}
#             for word in moji.split():
#                 words[word] = words.get(word, 0) + 1
#
#             # sort by count
#             cnt_word = [[v,k] for k,v in words.items()]
#             cnt_word.sort()
#             cnt_word.reverse() ## 降順
#             temp.append(cnt_word)
#             cnt_word = []
#         result.append(temp)
#     return result
#
# ## 絶対的な特徴(カテゴリー)
# def Category_Main(visited_spot_id_list,unvisited_spot_id_list):
#     cate_vispot = Category_Data(visited_spot_id_list)
#     cate_unspot = Category_Data(unvisited_spot_id_list)
#     ## レベルに応じて類似スポットセットを作成
#     level1,level2,level3 = Spot_set_by_level(cate_vispot,cate_unspot)
#     ## どのレベルまでのスポットセットを選択
#     level,review_by_spot = Level(level1,level2,level3)
#     all_reviews = []
#     for i in range(len(review_by_spot)):
#         temp = []
#         for j in range(len(review_by_spot[i])):
#             try:
#                 if review_by_spot[i][j][0] == review_by_spot[i][j+1][0]:
#                     temp.append(review_by_spot[i][j][1])
#                 else:
#                     temp.append(review_by_spot[i][j][1])
#                     all_reviews.append(temp)
#                     temp = []
#             except IndexError:
#                 temp.append(review_by_spot[i][j][1])
#                 all_reviews.append(temp)
#
#     ## 2つのリストを1つのセット(リスト)に入れす
#     set_2_list = list(zip(*[iter(all_reviews)]*2))
#     ## (類似スポット)単語の出現回数をカウント
#     cntw = Count_word(set_2_list)
#     print(cntw)
#     all,top10 = [],[]
#     for i in tqdm(range(len(cntw))):
#         temp = []
#         # for j in range(len(cntw[i][0])):
#         #     for k in range(len(cntw[i][1])):
#         #         ## 調和平均
#         #         if cntw[i][0][j][1]==cntw[i][1][k][1] and len(cntw[i][0][j][1])>1 and re.search(bytesymbols,cntw[i][0][j][1])==None:
#         #             temp.append([cntw[i][0][j][1],abs(2/(1/int(cntw[i][0][j][0])+1/int(cntw[i][1][k][0])))])
#         # all.append(temp)
#         # all[i].sort(key=lambda x:x[1],reverse=True)
#         # select_un = "SELECT name FROM spot_mst where id='{}'".format(level[i][0])
#         # cur.execute(select_un)
#         # unvisited_name = cur.fetchone()[0]
#         # select_vi = "SELECT name FROM spot_mst where id='{}'".format(level[i][1])
#         # cur.execute(select_vi)
#         # visited_name = cur.fetchone()[0]
#         # ## level は unvisited,visited
#         # top10.append([unvisited_name,visited_name,all[i][:10]])
#     # return top10
#         temp = []
#         same_word = list(set([cntw[i][0][j][1] for j in range(len(cntw[i][0]))]) & set([cntw[i][1][j][1] for j in range(len(cntw[i][1]))]))
#
#         for sw in same_word:
#             un = [j for j in range(len(cntw[i][0])) if cntw[i][0][j][1] == sw][0]
#             vi  = [j for j in range(len(cntw[i][1])) if cntw[i][1][j][1] == sw][0]
#             ## 調和平均
#             if len(cntw[i][0][un][1])>1 and re.search(bytesymbols,cntw[i][0][un][1])==None:
#                 temp.append([cntw[i][0][un][1],abs(2/(1/int(cntw[i][0][un][0])+1/int(cntw[i][1][vi][0])))])
#         all.append(temp)
#         all[i].sort(key=lambda x:x[1],reverse=True)
#         select_un = "SELECT name FROM spot_mst where id='{}'".format(level[i][0])
#         cur.execute(select_un)
#         unvisited_name = cur.fetchone()[0]
#         select_vi = "SELECT name FROM spot_mst where id='{}'".format(level[i][1])
#         cur.execute(select_vi)
#         visited_name = cur.fetchone()[0]
#         ## level は unvisited,visited
#         top10.append([unvisited_name,visited_name,all[i][:10]])
#     return top10
#
# top10 = Category_Main(visited_spot_id_list,unvisited_spot_id_list)

# all_catejson = []
# for i in range(len(top10)):
#     response_catejson = {"cate_unspot":"","cate_vispot":"","cate_word":""}
#     response_catejson["cate_unspot"] = top10[i][0]
#     response_catejson["cate_vispot"] = top10[i][1]
#     word_list = []
#     temp = []
#     for j in range(len(top10[i][2])):
#         try:
#             word_list.append(top10[i][2][j][0])
#         except TypeError:
#             continue
#     response_catejson["cate_word"] = word_list
#     all_catejson.append(response_catejson)
#
# print(all_catejson)
#
# import random, string
#
# def Randomname(n):
#    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
#    return ''.join(randlst)
#
# random_json = {"randomname":""}
# rand = Randomname(12)
# random_json["randomname"] = rand
#
# print([random_json]+[random_json]+[random_json])


#############################################################
## 絶対的な特徴（そのほか）
#############################################################
##########################
# print("\n既訪問カテゴリ")
# select_visited_category = "SELECT name,category_id FROM spot_category_name WHERE id IN {};".format(tuple(visited_spot_id_list))
# visited_category = myp_pk01.Spot_List(select_visited_category)
# pprint(visited_category)
#
# print("\n未訪問カテゴリ")
# select_unvisited_category = "SELECT name,category_id FROM spot_category_name WHERE id IN {};".format(tuple(unvisited_spot_id_list))
# unvisited_category = myp_pk01.Spot_List(select_unvisited_category)
# pprint(unvisited_category)
#
# ##########################
# print("\n既訪問：レビュー数，Spot_id，春，夏，秋，冬，1時間未満，1〜2時間，2〜3時間，3時間以上")
# select_season_duration = "SELECT COUNT(*),name,COUNT(season4='spring' or null),COUNT(season4='summer' or null),COUNT(season4 = 'autumn' or null),COUNT(season4='winter' or null),COUNT(duration='1時間未満' or null),COUNT(duration='1〜2時間' or null),COUNT(duration='2〜3時間' or null),COUNT(duration='3時間以上' or null) FROM review_all WHERE spot_id IN {} GROUP BY name;".format(tuple(visited_spot_id_list))
# visited_season_duration = myp_pk01.Spot_List(select_season_duration)
# pprint(visited_season_duration)
#
# print("\n未訪問：レビュー数，Spot_id，春，夏，秋，冬，1時間未満，1〜2時間，2〜3時間，3時間以上")
# select_season_duration = "SELECT COUNT(*),name,COUNT(season4='spring' or null),COUNT(season4='summer' or null),COUNT(season4 = 'autumn' or null),COUNT(season4='winter' or null),COUNT(duration='1時間未満' or null),COUNT(duration='1〜2時間' or null),COUNT(duration='2〜3時間' or null),COUNT(duration='3時間以上' or null) FROM review_all WHERE spot_id IN {} GROUP BY name;".format(tuple(unvisited_spot_id_list))
# unvisited_season_duration = myp_pk01.Spot_List(select_season_duration)
# pprint(unvisited_season_duration)

########################## 未訪問エリア指定
# # print("\n未訪問エリアid(東京都)")
# select_unvisited_spot = "SELECT id,name,area_id FROM spot_mst WHERE area_id BETWEEN 17698 AND 18516 AND review != 0 ORDER BY RAND() LIMIT 100;"
# unvisited_spot_list = myp_pk01.Spot_List(select_unvisited_spot)
# # pprint(unvisited_spot_list)
# unvisited_spot_id_list = []
# for i in range(len(unvisited_spot_list)):
#     unvisited_spot_id_list.append(unvisited_spot_list[i][0])
# # print(unvisited_spot_id_list)


#
#########################
# print("\n既訪問スポットベクトル")
select_visited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(visited_spot_id_list))
## スポット特徴ベクトル
visited_spot_vectors = myp_pk01.Spot_List(select_visited_spot_vectors)
# print(visited_spot_vectors)
## doc2vecを使ってスポットベクトルの差分を求める
visited_spot_vectors_doc = myp_pk01.Doc2Cec_Feature(visited_spot_vectors)
# print(visited_spot_vectors_doc)

# print("\n未訪問スポットベクトル")
select_unvisited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(unvisited_spot_id_list))
## スポット特徴ベクトル
unvisited_spot_vectors = myp_pk01.Spot_List(select_unvisited_spot_vectors)
# print(unvisited_spot_vectors)
## doc2vecを使ってスポットベクトルの差分を求める
unvisited_spot_vectors_doc = myp_pk01.Doc2Cec_Feature(unvisited_spot_vectors)
# print(unvisited_spot_vectors_doc)


#############################################################
# 絶対的な特徴（特徴ベクトル）
#############################################################
print("\n絶対的な特徴（特徴ベクトル）")
visited_spot_name_all,unvisited_spot_name_all = [],[]
visited_spot_review_all,unvisited_spot_review_all = [],[]
for i in range(len(visited_spot_vectors)):
    visited_spot_name_all.append(visited_spot_vectors[i][1])
    visited_spot_review_all.append(list(visited_spot_vectors[i][2:-1]))
for i in range(len(unvisited_spot_vectors)):
    unvisited_spot_name_all.append(unvisited_spot_vectors[i][1])
    unvisited_spot_review_all.append(list(unvisited_spot_vectors[i][2:-1]))
result_VtoU_top,result_UtoV_top = myp_pk01.Recommend_All(visited_spot_name_all,unvisited_spot_name_all,visited_spot_review_all,unvisited_spot_review_all)
## print("Visited to Unvisited")
## result_VtoU_top.sort(key=lambda x:x[1][1],reverse=True)
## pprint(result_VtoU_top)
print("Unvisited to Visited")
result_UtoV_top.sort(key=lambda x:x[1][1],reverse=True)
pprint(result_UtoV_top)

##########################
select_visited_spot_reviews = "SELECT spot_id,wakachi_neologd4 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd4".format(tuple(visited_spot_id_list))
visited_spot_reviews = myp_pk01.Spot_List_TFIDF(select_visited_spot_reviews)
visited_tfidf,visited_mean = myp_pk01.Tfidf(visited_spot_reviews)
# print("既訪問毎平均：\n" + str(visited_spot_name_all) + "\n" + str(visited_mean))

select_unvisited_spot_reviews = "SELECT spot_id,wakachi_neologd4 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd4".format(tuple(unvisited_spot_id_list))
unvisited_spot_reviews = myp_pk01.Spot_List_TFIDF(select_unvisited_spot_reviews)
unvisited_tfidf,unvisited_mean = myp_pk01.Tfidf(unvisited_spot_reviews)
# print("未訪問毎平均：\n" + str(unvisited_spot_name_all) + "\n" + str(unvisited_mean))

# print("\n相加平均")
# VtoU_top10 = myp_pk01.Sort_TFIDF_VtoU(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_VtoU_top)
# print("\n既訪問，未訪問，特徴語，2つの値の差(絶対値)，既値，未値")
# pprint(VtoU_top10)

# UtoV_top10 = myp_pk01.Sort_TFIDF_UtoV(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_UtoV_top)
# print("\n未訪問，既訪問，特徴語，2つの値の差(絶対値)，未値，既値")
# pprint(UtoV_top10)

print("\n調和平均")
# VtoU_top10 = myp_pk01.Sort_TFIDF_VtoU_Harmonic(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_VtoU_top)
# print("\n既訪問，未訪問，特徴語，2つの値の差(絶対値)，既値，未値")
# pprint(VtoU_top10)

UtoV_top10 = myp_pk01.Sort_TFIDF_UtoV_Harmonic(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_UtoV_top)
print("\n未訪問，既訪問，特徴語，2つの値の差(絶対値)，未値，既値")
pprint(UtoV_top10)


############################################################
# 相対的な特徴（差分ベクトル）
############################################################
#########################
print("\n相対的な特徴（差分ベクトル）")
visited_spot_name_all,unvisited_spot_name_all = [],[]
visited_spot_review_all,unvisited_spot_review_all = [],[]
for i in range(len(visited_spot_vectors_doc)):
    visited_spot_name_all.append(visited_spot_vectors_doc[i][0])
    visited_spot_review_all.append(visited_spot_vectors_doc[i][1])
for i in range(len(unvisited_spot_vectors_doc)):
    unvisited_spot_name_all.append(unvisited_spot_vectors_doc[i][0])
    unvisited_spot_review_all.append(unvisited_spot_vectors_doc[i][1])
result_VtoU_top,result_UtoV_top = myp_pk01.Recommend_All(visited_spot_name_all,unvisited_spot_name_all,visited_spot_review_all,unvisited_spot_review_all)
# print("Visited Name：" + str(visited_spot_name_all))
# print("Unvisited Name：" + str(unvisited_spot_name_all))
# print("Visited to Unvisited")
# pprint(result_VtoU_top)
print("Unvisited to Visited")
result_UtoV_top.sort(key=lambda x:x[1][1],reverse=True)
pprint(result_UtoV_top)

##########################
select_visited_spot_reviews = "SELECT spot_id,wakachi_neologd4 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd4".format(tuple(visited_spot_id_list))
visited_spot_reviews = myp_pk01.Spot_List_TFIDF(select_visited_spot_reviews)
visited_tfidf,visited_mean = myp_pk01.Tfidf(visited_spot_reviews)
## print("既訪問毎平均：\n" + str(visited_spot_name_all) + "\n" + str(visited_mean))

select_unvisited_spot_reviews = "SELECT spot_id,wakachi_neologd4 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd4".format(tuple(unvisited_spot_id_list))
unvisited_spot_reviews = myp_pk01.Spot_List_TFIDF(select_unvisited_spot_reviews)
unvisited_tfidf,unvisited_mean = myp_pk01.Tfidf(unvisited_spot_reviews)
## print("未訪問毎平均：\n" + str(unvisited_spot_name_all) + "\n" + str(unvisited_mean))

# print("\n相加平均")
# # VtoU_top10 = myp_pk01.Sort_TFIDF_VtoU(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_VtoU_top)
# # print("\n既訪問，未訪問，特徴語，2つの値の差(絶対値)，既値，未値")
# # pprint(VtoU_top10)
#
# UtoV_top10 = myp_pk01.Sort_TFIDF_UtoV(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_UtoV_top)
# print("\n未訪問，既訪問，特徴語，2つの値の差(絶対値)，未値，既値")
# pprint(UtoV_top10)

print("\n調和平均")
# VtoU_top10 = myp_pk01.Sort_TFIDF_VtoU_Harmonic(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_VtoU_top)
# print("\n既訪問，未訪問，特徴語，2つの値の差(絶対値)，既値，未値")
# pprint(VtoU_top10)

UtoV_top10 = myp_pk01.Sort_TFIDF_UtoV_Harmonic(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_UtoV_top)
print("\n未訪問，既訪問，特徴語，2つの値の差(絶対値)，未値，既値")
pprint(UtoV_top10)
