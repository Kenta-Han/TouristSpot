#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import numpy as np
from pprint import pprint
from sklearn.decomposition import PCA ## scikit-learnのPCAクラス
import pandas as pd ## 便利なDataFrameを使うためのライブラリ
import matplotlib.pyplot as plt
import mypackage.package_01 as myp_pk01

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

##########################
# ## [建長寺,高徳院（鎌倉大仏）,長谷寺（長谷観音）,鶴岡八幡宮,龍口寺]
# visited_spot_id_list = ['spt_14204ag2130011936','spt_14204ag2130009759','spt_14204ag2130009778','spt_14204ag2130012949','spt_14205ag2130015243']

## spt_14205ag2130015243 江島神社

# ## [伏見稲荷大社,鹿苑寺（金閣寺）,龍安寺,清水寺,八坂神社]
visited_spot_id_list = ['spt_26109ag2130015470','spt_26101ag2130014551','spt_26108ag2130015438','spt_26105ag2130012063','spt_26105ag2130010617']

## [海遊館,天保山大観覧車,大阪城公園,USJ,天王寺動物園]
# visited_spot_id_list = ['spt_27107cc3320040646','spt_27107ad3352003168','spt_27128ah3330042284','spt_guide000000184294','spt_27109ae3312015930']

## [東京都庁舎展望室,浅草寺,明治神宮,新宿御苑,皇居東御苑]
unvisited_spot_id_list = ['spt_13104aj2200025349','spt_13106ag2130012302','spt_13113ag2130014473','spt_13104ah2140016473','spt_13101ah2140016178']

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

##########################
# print("\n既訪問スポットベクトル")
select_visited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(visited_spot_id_list))
visited_spot_vectors = myp_pk01.Spot_List(select_visited_spot_vectors)
# print(visited_spot_vectors)
visited_spot_vectors_doc = myp_pk01.Doc2Cec_Feature(visited_spot_vectors)

# print("\n未訪問スポットベクトル")
select_unvisited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(unvisited_spot_id_list))
unvisited_spot_vectors = myp_pk01.Spot_List(select_unvisited_spot_vectors)
# print(unvisited_spot_vectors)
unvisited_spot_vectors_doc = myp_pk01.Doc2Cec_Feature(unvisited_spot_vectors)
# print(unvisited_spot_vectors_doc)

##########################
print("\n既訪問と未訪問スポットベクトルの差の類似度(1番高い)")
visited_spot_name_all,unvisited_spot_name_all = [],[]
visited_spot_review_all,unvisited_spot_review_all = [],[]
for i in range(len(visited_spot_vectors_doc)):
    visited_spot_name_all.append(visited_spot_vectors_doc[i][0])
    visited_spot_review_all.append(visited_spot_vectors_doc[i][1])
for i in range(len(unvisited_spot_vectors_doc)):
    unvisited_spot_name_all.append(unvisited_spot_vectors_doc[i][0])
    unvisited_spot_review_all.append(unvisited_spot_vectors_doc[i][1])
result_VtoU_top,result_UtoV_top = myp_pk01.Recommend_All(visited_spot_name_all,unvisited_spot_name_all,visited_spot_review_all,unvisited_spot_review_all)
print("Visited to Unvisited")
pprint(result_VtoU_top)
print("Unvisited to Visited")
pprint(result_UtoV_top)

##########################
print("\n既訪問と未訪問スポット特徴語TOP10(TFIDF)")
select_visited_spot_reviews = "SELECT spot_id,wakachi_neologd2 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd2".format(tuple(visited_spot_id_list))
visited_spot_reviews = myp_pk01.Spot_List_TFIDF(select_visited_spot_reviews)
visited_tfidf,visited_mean = myp_pk01.Tfidf(visited_spot_reviews)
print("既訪問毎平均：\n" + str(visited_spot_name_all) + "\n" + str(visited_mean))

select_unvisited_spot_reviews = "SELECT spot_id,wakachi_neologd2 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd2".format(tuple(unvisited_spot_id_list))
unvisited_spot_reviews = myp_pk01.Spot_List_TFIDF(select_unvisited_spot_reviews)
unvisited_tfidf,unvisited_mean = myp_pk01.Tfidf(unvisited_spot_reviews)
print("未訪問毎平均：\n" + str(unvisited_spot_name_all) + "\n" + str(unvisited_mean))

VtoU_top10 = myp_pk01.Sort_TFIDF_VtoU(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_VtoU_top)
print("\n既訪問，未訪問，特徴語，2つの値の差(絶対値)，既値，未値")
pprint(VtoU_top10)

UtoV_top10 = myp_pk01.Sort_TFIDF_UtoV(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,visited_mean,unvisited_mean,result_UtoV_top)
print("\n未訪問，既訪問，特徴語，2つの値の差(絶対値)，未値，既値")
pprint(UtoV_top10)


##########################
# print("\n既訪問と未訪問スポットベクトルの類似度")
# visited_spot_name_all,unvisited_spot_name_all = [],[]
# visited_spot_review_all,unvisited_spot_review_all = [],[]
# for i in range(len(visited_spot_vectors)):
#     visited_spot_name_all.append(visited_spot_vectors[i][1])
#     unvisited_spot_name_all.append(unvisited_spot_vectors[i][1])
#     visited_spot_review_all.append(list(visited_spot_vectors[i][2:-1]))
#     unvisited_spot_review_all.append(list(unvisited_spot_vectors[i][2:-1]))
# result_VtoU_top,result_UtoV_top = myp_pk01.Recommend_All(visited_spot_name_all,unvisited_spot_name_all,visited_spot_review_all,unvisited_spot_review_all)
# # print("Visited to Unvisited")
# # pprint(result_VtoU_top)
# print("Unvisited to Visited")
# pprint(result_UtoV_top)
