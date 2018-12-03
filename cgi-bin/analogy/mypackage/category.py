#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from tqdm import tqdm
## カテゴリー参照(level1)→訪問季節参照(level2)→滞在時間参照(level3)
bytesymbols = re.compile("[!-/:-@[-`{-~\d]") ## 半角記号，数字\d

import MySQLdb
import os, sys ## 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()


def Category_Data(data):
    spot = []
    for i in range(len(data)):
        temp = []

        select_category = "SELECT category_id FROM spot_category WHERE id='{}';".format(data[i])
        cur.execute(select_category)
        try:
            category = cur.fetchone()[0]
        except TypeError:
            category = None

        select_season = "SELECT temp.season4 FROM (SELECT season4, count(*) cnt2 FROM review_all WHERE spot_id='{id}' GROUP BY season4) temp WHERE temp.cnt2 = (SELECT max(cnt) FROM (SELECT season4, count(*) AS cnt,season4 is not null AS nu FROM review_all WHERE spot_id='{id}' GROUP BY season4) num WHERE nu='1');".format(id=data[i])
        cur.execute(select_season)
        try:
            season = cur.fetchone()[0]
        except TypeError:
            season = None

        select_duration = "SELECT temp.duration FROM (SELECT duration, count(*) cnt2 FROM review_all WHERE spot_id='{id}' GROUP BY duration) temp WHERE temp.cnt2 = (SELECT max(cnt) FROM (SELECT duration, count(*) AS cnt,duration is not null AS nu FROM review_all WHERE spot_id='{id}' GROUP BY duration) num WHERE nu='1');".format(id=data[i])
        cur.execute(select_duration)
        try:
            duration = cur.fetchone()[0]
        except TypeError:
            duration = None

        temp.append([data[i],category,season,duration])
        spot.extend(temp)
    return spot

## レベルに応じて類似スポットセットを作成
def Spot_set_by_level(cate_vispot,cate_unspot):
    level1,level2,level3 = [],[],[]
    for i in range(len(cate_unspot)):
        for j in range(len(cate_vispot)):
            if cate_unspot[i][1] == cate_vispot[j][1]:
                if cate_unspot[i][2] == cate_vispot[j][2]:
                    if cate_unspot[i][3] == cate_vispot[j][3]:
                        level3.append([cate_unspot[i][0],cate_vispot[j][0]])
                    else:
                        level2.append([cate_unspot[i][0],cate_vispot[j][0]])
                else:
                    level1.append([cate_unspot[i][0],cate_vispot[j][0]])
            else:
                continue
    return level1,level2,level3

## 分かち書きのデータを抽出
def Select_Review(data):
    review_by_spot = []
    set = []
    for i in range(len(data)):
        temp = []
        select = "SELECT name,wakachi_neologd3 FROM review_all WHERE spot_id IN {};".format(tuple(data[i]))
        cur.execute(select)
        for j in cur:
            temp.append(list(j))
        set.append(temp)
    review_by_spot.extend(set)
    return review_by_spot

## どのレベルまでのスポットセットを選択
def Level(level1,level2,level3):
    if level3 != []:
        review_by_spot = Select_Review(level3)
        level = level3
    else:
        if level2 != []:
            review_by_spot = Select_Review(level2)
            level = level2
        else:
            if level1 != []:
                review_by_spot = Select_Review(level1)
                level = level1
            else:
                review_by_spot = 0
                level = 0
    return level,review_by_spot


## (類似スポット)単語の出現回数をカウント
def Count_word(data):
    result = []
    for i in range(len(data)):
        temp = []
        for j in range(2):
            moji =",".join(data[i][j])
            ## counting
            words = {}
            for word in moji.split():
                words[word] = words.get(word, 0) + 1

            # sort by count
            cnt_word = [[v,k] for k,v in words.items()]
            cnt_word.sort()
            cnt_word.reverse() ## 降順
            temp.append(cnt_word)
            cnt_word = []
        result.append(temp)
    return result

## 絶対的な特徴(カテゴリー)
def Category_Main(visited_spot_id_list,unvisited_spot_id_list):
    cate_vispot = Category_Data(visited_spot_id_list)
    cate_unspot = Category_Data(unvisited_spot_id_list)
    ## レベルに応じて類似スポットセットを作成
    level1,level2,level3 = Spot_set_by_level(cate_vispot,cate_unspot)
    ## どのレベルまでのスポットセットを選択
    level,review_by_spot = Level(level1,level2,level3)

    all_reviews = []
    for i in range(len(review_by_spot)):
        temp = []
        for j in range(len(review_by_spot[i])):
            try:
                if review_by_spot[i][j][0] == review_by_spot[i][j+1][0]:
                    temp.append(review_by_spot[i][j][1])
                else:
                    temp.append(review_by_spot[i][j][1])
                    all_reviews.append(temp)
                    temp = []
            except IndexError:
                temp.append(review_by_spot[i][j][1])
                all_reviews.append(temp)

    ## 2つのリストを1つのセット(リスト)に入れす
    set_2_list = list(zip(*[iter(all_reviews)]*2))
    ## (類似スポット)単語の出現回数をカウント
    cntw = Count_word(set_2_list)

    all,top10 = [],[]
    for i in tqdm(range(len(cntw))):
        temp = []
        for j in range(len(cntw[i][0])):
            for k in range(len(cntw[i][1])):
                ## 調和平均
                if cntw[i][0][j][1]==cntw[i][1][k][1] and len(cntw[i][0][j][1])>1 and re.search(bytesymbols,cntw[i][0][j][1])==None:
                    temp.append([cntw[i][0][j][1],abs(2/(1/int(cntw[i][0][j][0])+1/int(cntw[i][1][k][0])))])
        all.append(temp)
        all[i].sort(key=lambda x:x[1],reverse=True)
        select_un = "SELECT name FROM spot_mst where id='{}'".format(level[i][0])
        cur.execute(select_un)
        unvisited_name = cur.fetchone()[0]
        select_vi = "SELECT name FROM spot_mst where id='{}'".format(level[i][1])
        cur.execute(select_vi)
        visited_name = cur.fetchone()[0]
        ## level は unvisited,visited
        top10.append([unvisited_name,visited_name,all[i][:10]])
    return top10
