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
print("\n既訪問カテゴリ")
select_history_category = "SELECT * FROM spot_category WHERE id IN {};".format(tuple(visited_spot_id_list))
history_category = myp_pk01.Spot_List(select_history_category)
pprint(history_category)

print("\n未訪問カテゴリ")
select_category = "SELECT * FROM spot_category WHERE id IN {};".format(tuple(unvisited_spot_id_list))
category = myp_pk01.Spot_List(select_category)
pprint(category)

##########################
print("\n既訪問：レビュー数，Spot_id，春，夏，秋，冬，1時間未満，1〜2時間，2〜3時間，3時間以上")
select_season_duration = "SELECT COUNT(*),name,COUNT(season4='spring' or null),COUNT(season4='summer' or null),COUNT(season4 = 'autumn' or null),COUNT(season4='winter' or null),COUNT(duration='1時間未満' or null),COUNT(duration='1〜2時間' or null),COUNT(duration='2〜3時間' or null),COUNT(duration='3時間以上' or null) FROM review_all WHERE spot_id IN {} GROUP BY name;".format(tuple(visited_spot_id_list))
history_season_duration = myp_pk01.Spot_List(select_season_duration)
pprint(history_season_duration)

print("\n未訪問：レビュー数，Spot_id，春，夏，秋，冬，1時間未満，1〜2時間，2〜3時間，3時間以上")
select_season_duration = "SELECT COUNT(*),name,COUNT(season4='spring' or null),COUNT(season4='summer' or null),COUNT(season4 = 'autumn' or null),COUNT(season4='winter' or null),COUNT(duration='1時間未満' or null),COUNT(duration='1〜2時間' or null),COUNT(duration='2〜3時間' or null),COUNT(duration='3時間以上' or null) FROM review_all WHERE spot_id IN {} GROUP BY name;".format(tuple(unvisited_spot_id_list))
season_duration = myp_pk01.Spot_List(select_season_duration)
pprint(season_duration)

##########################
print("\n既訪問スポットベクトル")
select_history_spot_vectors = "SELECT * FROM tfidf_by_wakachi2 WHERE spot_id IN {};".format(tuple(visited_spot_id_list))
history_spot_vectors = myp_pk01.Spot_List_TFIDF(select_history_spot_vectors)
print(history_spot_vectors)
history_spot_vectors_doc = myp_pk01.TFIDF_Feature(history_spot_vectors)
print(history_spot_vectors_doc)

# data = []
# for i in range(len(history_spot_vectors_doc)):
#     data.append(history_spot_vectors_doc[i][1])
# df = pd.DataFrame(data)
# print(df)
# ## n次元に圧縮するPCAインスタンスを作成，データをPCAで次元圧縮
# X = PCA(n_components=3).fit_transform(df.iloc[:,:].values)
# embed3 = pd.DataFrame(X) ## 可視化のためにデータフレームに変換
# print(embed3.head())

# print("\n未訪問スポットベクトル")
select_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(unvisited_spot_id_list))
spot_vectors = myp_pk01.Spot_List(select_spot_vectors)
# print(spot_vectors)
spot_vectors_doc = myp_pk01.Doc2Cec_Feature(spot_vectors)
# print(spot_vectors_doc)

print("\n既訪問と未訪問スポットベクトルの差の類似度")
his_spot_id_all,spot_id_all = [],[]
his_spot_review_all,spot_review_all = [],[]
for i in range(len(history_spot_vectors_doc)):
    his_spot_id_all.append(history_spot_vectors_doc[i][0])
    spot_id_all.append(spot_vectors_doc[i][0])
    his_spot_review_all.append(history_spot_vectors_doc[i][1])
    spot_review_all.append(spot_vectors_doc[i][1])
result_HtoA,result_AtoH = myp_pk01.Recommend_All(his_spot_id_all,spot_id_all,his_spot_review_all,spot_review_all)
print("\nHistory to Area")
pprint(result_HtoA)

print("\nArea to Histosy")
pprint(result_AtoH)
