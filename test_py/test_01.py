#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import numpy as np
from pprint import pprint
from sklearn.decomposition import PCA ## scikit-learnのPCAクラス
import pandas as pd ## 便利なDataFrameを使うためのライブラリ
import matplotlib.pyplot as plt
import mypackage.test_01_pk as myp_pk01

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

# history_prefecture = "神奈川"
# history_area = "鎌倉"
#
# history_prefecture = "京都"
# history_area = "京都"
#
# select_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND (area2 LIKE '%{area}%' OR area3 LIKE '%{area}%') AND id < 30435;".format(pre = history_prefecture, area = history_area)
# area_id_list = []
# cur.execute(select_area_id)
# for i in cur:
#     area_id_list.append(i[0])
# print(area_id_list)
#
# select_history_spot = "SELECT DISTINCT id,name,area_id FROM spot_mst WHERE area_id IN {} AND review != 0;".format(tuple(area_id_list))
# history_spot_list = myp_pk01.Spot_List(select_history_spot)
# pprint(history_spot_list)
#
# print("\n指定エリアid(東京都)")
# select_spot = "SELECT id,name,area_id FROM spot_mst WHERE area_id BETWEEN 17698 AND 18516 AND review != 0;"
# spot_list = myp_pk01.Spot_List(select_spot)
# pprint(spot_list)

##########################
# ## [建長寺,高徳院（鎌倉大仏）,長谷寺（長谷観音）,鶴岡八幡宮,龍口寺]
history_spot_id_list = ['spt_14204ag2130011936','spt_14204ag2130009759','spt_14204ag2130009778','spt_14204ag2130012949','spt_14205ag2130009779']

## [建長寺,高徳院（鎌倉大仏）,長谷寺（長谷観音）,鶴岡八幡宮,]
# history_spot_id_list = ['spt_26109ag2130015470','spt_26101ag2130014551','spt_26108ag2130015438','spt_26105ag2130012063','spt_26105ag2130010617']

## [東京都庁舎展望室,浅草寺,明治神宮,新宿御苑,皇居東御苑]
spot_id_list = ['spt_13104aj2200025349','spt_13106ag2130012302','spt_13113ag2130014473','spt_13104ah2140016473','spt_13101ah2140016178']

##########################
print("\n既訪問カテゴリ")
select_history_category = "SELECT * FROM spot_category WHERE id IN {};".format(tuple(history_spot_id_list))
history_category = myp_pk01.Spot_List(select_history_category)
pprint(history_category)

print("\n未訪問カテゴリ")
select_category = "SELECT * FROM spot_category WHERE id IN {};".format(tuple(spot_id_list))
category = myp_pk01.Spot_List(select_category)
pprint(category)

##########################
print("\n既訪問：レビュー数，Spot_id，春，夏，秋，冬，1時間未満，1〜2時間，2〜3時間，3時間以上")
select_season_duration = "SELECT COUNT(*),name,COUNT(season4='spring' or null),COUNT(season4='summer' or null),COUNT(season4 = 'autumn' or null),COUNT(season4='winter' or null),COUNT(duration='1時間未満' or null),COUNT(duration='1〜2時間' or null),COUNT(duration='2〜3時間' or null),COUNT(duration='3時間以上' or null) FROM review_all WHERE spot_id IN {} GROUP BY name;".format(tuple(history_spot_id_list))
history_season_duration = myp_pk01.Spot_List(select_season_duration)
pprint(history_season_duration)

print("\n未訪問：レビュー数，Spot_id，春，夏，秋，冬，1時間未満，1〜2時間，2〜3時間，3時間以上")
select_season_duration = "SELECT COUNT(*),name,COUNT(season4='spring' or null),COUNT(season4='summer' or null),COUNT(season4 = 'autumn' or null),COUNT(season4='winter' or null),COUNT(duration='1時間未満' or null),COUNT(duration='1〜2時間' or null),COUNT(duration='2〜3時間' or null),COUNT(duration='3時間以上' or null) FROM review_all WHERE spot_id IN {} GROUP BY name;".format(tuple(spot_id_list))
season_duration = myp_pk01.Spot_List(select_season_duration)
pprint(season_duration)

##########################
print("\n既訪問スポットベクトル")
select_history_spot_vectors = "SELECT * FROM spot_vectors WHERE id IN {};".format(tuple(history_spot_id_list))
history_spot_vectors = myp_pk01.Spot_List(select_history_spot_vectors)
# print(history_spot_vectors)
history_spot_vectors_doc = myp_pk01.Doc2Cec_Feature(history_spot_vectors)
# print(history_spot_vectors_doc)

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
select_spot_vectors = "SELECT * FROM spot_vectors WHERE id IN {};".format(tuple(spot_id_list))
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
