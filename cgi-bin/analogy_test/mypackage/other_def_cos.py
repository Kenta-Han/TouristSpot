import MySQLdb
import math
from tqdm import tqdm
from gensim import corpora
from gensim import models
import mypackage.cos_sim_class as myp_cos
sc = myp_cos.SimCalculator()

import os, sys # 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

import numpy as np
import pandas as pd
from sklearn.datasets import make_blobs
from scipy.spatial.distance import pdist, squareform


## 履歴スポットリスト作成(DBでLIKE検索するため)
def Make_History_List(history):
	history_list = []
	for i in range(len(history)):
		temp = " like %"+ history[i] + "%  or"
		history_list.append(temp)
		temp = 0
	history = ",".join(history_list)[:-2]
	return history

## スポット，レビューリスト作成
def SpotORReview_List(spot):
	spot_list = []
	cur.execute(spot)
	for i in cur:
		spot_list.append(i)
	return spot_list

## エリアIDリスト作成
def Area_id_List(area):
	area_id_list = []
	cur.execute(area)
	for i in cur:
		area_id_list.append(i[0])
	return area_id_list

## スポット毎のレビュー
def EverySpot_Review(review_list):
	review_wkt_group_by = []
	review_wkt_group_by_spot = []
	for i in range(len(review_list)):
		try:
			if review_list[i][0] == review_list[i+1][0]:
				temp = review_list[i][1].split()
				review_wkt_group_by_spot.extend(temp)
				temp = []
			else:
				temp = review_list[i][1].split()
				# temp.append(review_list[i][0]) #スポットIDを追加
				review_wkt_group_by_spot.extend(temp)
				review_wkt_group_by.append(review_wkt_group_by_spot)
				review_wkt_group_by_spot = []
		except IndexError:
			temp = review_list[i][1].split()
			# temp.append(review_list[i][0]) #スポットIDを追加
			review_wkt_group_by_spot.extend(temp)
			review_wkt_group_by.append(review_wkt_group_by_spot)
			review_wkt_group_by_spot = []
	return review_wkt_group_by

## 履歴のスポットのカテゴリ別の全レビュー
def AllSpot_Review(review_list):
	review_wkt_all = []
	for i in range(len(review_list)):
		temp = review_list[i][1].split()
		review_wkt_all.append(temp)
		temp = []
	return review_wkt_all

## エリア内or履歴のスポットの全レビュー
def AllSpot_Review(review_list):
	review_wkt_all = []
	for i in range(len(review_list)):
		temp = review_list[i][1].split()
		review_wkt_all.append(temp)
		temp = []
	return review_wkt_all

## TFIDFを求める(単語に重み付け)
def Tfidf(review_all):
	dictionary = corpora.Dictionary(review_all) ## 単語にidを振る
	dictionary_inv = {}
	for dic in dictionary.token2id.items():
		dictionary_inv[dic[1]]=dic[0]
		# print(dictionary_inv)
	corpus = list(map(dictionary.doc2bow,review_all)) ## テキストのコーパス化
	# print(corpus)
	test_model = models.TfidfModel(corpus) ## コーパスからtfidfモデルを生成(正規化済み)
	corpus_tfidf = list(test_model[corpus])
	## 対応する数値を文字に変える
	j = 0
	doc2 = [] ## id表示ではないもの
	for wod in corpus_tfidf:
		i = 0
		doc2.append('') ## 空要素
		doc3 = []
		for ch in wod:
			doc3.append('')
			doc3[i] = [dictionary_inv[ch[0]],ch[1]]
			i += 1
		doc2[j] = doc3
		j += 1
	# print(doc2)
	return doc2

## 履歴レビューを辞書でリストにまとめる
def Change_To_Dic(words):
	spot = []
	all_spot = []
	search_dic = {}
	for i in range(len(words)):
		for j in words[i]:
			search_dic[j[0]] = j[1]
		spot.append(search_dic)
		search_dic = {}
	all_spot.append(spot)
	return all_spot

## 全ての観光地の類似度を出す
def Recommend_All(spot_all,spot_list):
	i = 1
	value = []
	while (i <= len(spot_all) - 1):
		cos = sc.sim_cos(spot_all[0],spot_all[i])
		value.append(cos)
		i += 1
	dic = dict(zip(spot_list,value)) ## 辞書作成 (スポット名,類似度)
	# print(dic)
	result = sorted(dic.items(),key=lambda x:x[1],reverse=True) ##降順にソート
	# print(result)
	# recommend_spot_list = []
	# for i in range(len(result)):
	# 	a = []
	# 	if i >= len(result):
	# 		continue
	# 	cur.execute("select spot_id from unity_kantou where name ='" + result[i][0] + "';")
	# 	spot_id = cur.fetchone()
	# 	recommend_spot_list.append([spot_id[0],result[i][0],result[i][1]])
	# return recommend_spot_list
	return result
