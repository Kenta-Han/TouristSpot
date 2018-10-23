#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import numpy as np
from pprint import pprint
import copy

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

def Spot_List(select_spot):
    spot_list = []
    cur.execute(select_spot)
    for i in cur:
        spot_list.append(i)
    return spot_list

def Spot_Review(history_review_id):
    history_review_id_groupby = []
    history_review_id_groupby_spot = []
    for i in range(len(history_review_id)):
        try:
            if history_review_id[i][1] == history_review_id[i+1][1]:
                history_review_id_groupby.append(history_review_id[i][0])
            else:
                history_review_id_groupby.append(history_review_id[i][0])
                history_review_id_groupby_spot.append([history_review_id[i][1],history_review_id_groupby])
                history_review_id_groupby = []
        except IndexError:
            history_review_id_groupby.append(history_review_id[i][0])
            history_review_id_groupby_spot.append([history_review_id[i][1],history_review_id_groupby])
            history_review_id_groupby = []
    return history_review_id_groupby_spot

def Doc2Cec_Feature(spot_vectors):
    result_list = []
    for i in range(len(spot_vectors)):
        x = copy.deepcopy(spot_vectors)
        target = list(x[i][1:301])
        name = x[i][0]
        x.pop(i)
        temp = []
        for j in range(len(x)):
            temp.append(list(x[j][1:301]))
        temp = np.array(temp)
        result = target-sum(temp)/len(temp)
        # print(name)
        result_list.append([name, list(result)])
        target = []
        result = []
    return result_list


history_prefecture = "神奈川"
history_area = "鎌倉"

select_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND (area2 LIKE '%{area}%' OR area3 LIKE '%{area}%') AND id < 30435;".format(pre = history_prefecture, area = history_area)
area_id_list = []
cur.execute(select_area_id)
for i in cur:
    area_id_list.append(i[0])
# print(area_id_list)

select_history_spot = "SELECT DISTINCT id,name,area_id FROM spot_mst WHERE area_id IN {} AND review != 0;".format(tuple(area_id_list))
history_spot_list = Spot_List(select_history_spot)
# pprint(history_spot_list)

print("\n指定エリアid(東京都)")
select_spot = "SELECT id,name,area_id FROM spot_mst WHERE area_id BETWEEN 17698 AND 18516 AND review != 0;"
spot_list = Spot_List(select_spot)
# pprint(spot_list)

##########################
history_spot_id_list = ['spt_14204ag2130011936','spt_14204ag2130009759','spt_14204ag2130009778','spt_14204ag2130012949','spt_14205ag2130009779']

spot_id_list = ['spt_13104aj2200025349','spt_13106ag2130012302','spt_13113ag2130014473','spt_13104ah2140016473','spt_13101ah2140016178']

##########################
print("\n既訪問カテゴリ")
select_history_category = "SELECT * FROM spot_category WHERE id IN {};".format(tuple(history_spot_id_list))
history_category = Spot_List(select_history_category)
pprint(history_category)

print("\n未訪問カテゴリ")
select_category = "SELECT * FROM spot_category WHERE id IN {};".format(tuple(spot_id_list))
category = Spot_List(select_category)
pprint(category)

##########################
print("\n既訪問：レビュー数，Spot_id，春，夏，秋，冬，1時間未満，1〜2時間，2〜3時間，3時間以上")
select_season_duration = "SELECT COUNT(*),spot_id,COUNT(season4='spring' or null),COUNT(season4='summer' or null),COUNT(season4 = 'autumn' or null),COUNT(season4='winter' or null),COUNT(duration='1時間未満' or null),COUNT(duration='1〜2時間' or null),COUNT(duration='2〜3時間' or null),COUNT(duration='3時間以上' or null) FROM review WHERE spot_id IN {} GROUP BY spot_id;".format(tuple(history_spot_id_list))
history_season_duration = Spot_List(select_season_duration)
pprint(history_season_duration)

print("\n未訪問：レビュー数，Spot_id，春，夏，秋，冬，1時間未満，1〜2時間，2〜3時間，3時間以上")
select_season_duration = "SELECT COUNT(*),spot_id,COUNT(season4='spring' or null),COUNT(season4='summer' or null),COUNT(season4 = 'autumn' or null),COUNT(season4='winter' or null),COUNT(duration='1時間未満' or null),COUNT(duration='1〜2時間' or null),COUNT(duration='2〜3時間' or null),COUNT(duration='3時間以上' or null) FROM review WHERE spot_id IN {} GROUP BY spot_id;".format(tuple(spot_id_list))
season_duration = Spot_List(select_season_duration)
pprint(season_duration)

##########################
print("\n既訪問スポットベクトル")
select_history_spot_vectors = "SELECT * FROM spot_vectors WHERE id IN {};".format(tuple(history_spot_id_list))
history_spot_vectors = Spot_List(select_history_spot_vectors)
# print(history_spot_vectors)
history_spot_vectors_doc = Doc2Cec_Feature(history_spot_vectors)
print(history_spot_vectors_doc[2])


print("\n未訪問スポットベクトル")
select_spot_vectors = "SELECT * FROM spot_vectors WHERE id IN {};".format(tuple(spot_id_list))
spot_vectors = Spot_List(select_spot_vectors)
# print(spot_vectors)
spot_vectors_doc = Doc2Cec_Feature(spot_vectors)
# print(spot_vectors_doc)


##########################
# print("\n既訪問スポット毎レビューベクトル")
# select_history_review_id = "SELECT id,spot_id FROM review_all WHERE spot_id IN {};".format(tuple(history_spot_id_list))
# history_review_id = Spot_List(select_history_review_id)
# history_review_id_groupby_spot = Spot_Review(history_review_id)
# # print(history_review_id_groupby_spot)
#
# history_review_vectors = []
# for i in range(len(history_review_id_groupby_spot)):
#     select_history_review_vectors = "SELECT * FROM review_vectors WHERE id IN {};".format(tuple(history_review_id_groupby_spot[i][1]))
#     history_review_vectors.append(Spot_List(select_history_review_vectors))
# # print(history_review_vectors[0][0])
# # print(history_review_vectors[1][0])
#
# spot_review = []
# for i in range(len(history_review_vectors)):
#     temp = []
#     for j in range(len(history_review_vectors[i])):
#         temp.append(sum(history_review_vectors[i][j][1:301]))
#     spot_review.append(temp)
# # print(spot_review)
#
# every_spot_vector = []
# for i in range(len(spot_review)):
#     print(spot_review[i])
#     print(len(spot_review[i]))
#     every_spot_vector.append((sum(spot_review[i]))/len(spot_review[i]))
# print(every_spot_vector)
