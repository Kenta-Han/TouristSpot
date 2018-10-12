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
from mysql_connect import jalan_mindmap
conn,cur = jalan_mindmap.main()

import numpy as np
import pandas as pd
from sklearn.datasets import make_blobs
from scipy.spatial.distance import pdist, squareform


## 履歴スポットリスト作成(DBでLIKE検索するため)
def Make_History_List(history):
	history_list = []
	for i in range(len(history)):
		temp = "%"+ history[i] +"%"
		history_list.append(temp)
		temp = 0
	return history_list

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

## K-Medoid法
def spot_values_list(tfidf_list):
	spot_values_list = []
	temp = []
	for i in range(len(tfidf_list)):
	    for j in range(len(tfidf_list[i])):
	        temp.append(tfidf_list[i][j][1])
	    spot_values_list.append(temp)
	    temp = []
	return spot_values_list

class KMedoids(object):
	def __init__(self, n_cluster, max_iter=300):
		self.n_cluster = n_cluster
		self.max_iter = max_iter # 最大回数

	def fit_predict(self, D):
		m, n = D.shape
		initial_medoids = np.random.choice(range(m), self.n_cluster, replace=False)
		tmp_D = D[:, initial_medoids]

		# 初期セントロイドの中で距離が最も近いセントロイドにクラスタリング
		labels = np.argmin(tmp_D, axis=1)

		# 各点に一意のIDが振ってあった方が分類したときに取り扱いやすいため
		# IDをもつようにするデータフレームを作っておく
		# .T 行と列を入れ替える
		results = pd.DataFrame([range(m), labels]).T
		results.columns = ['id', 'label']

		col_names = ['x_' + str(i + 1) for i in range(m)]
		# 各点のIDと距離行列を結びつかせる
		# 距離行列の列に名前をつけて後々処理しやすいようにしている
		results = pd.concat([results, pd.DataFrame(D, columns=col_names)], axis=1)

		before_medoids = initial_medoids
		new_medoids = []

		loop = 0
		# medoidの群に変化があり，ループ回数がmax_iter未満なら続く
		# s.intersection(t) -> sとtで共通する要素からなる新しい集合
		while len(set(before_medoids).intersection(set(new_medoids))) != self.n_cluster and loop < self.max_iter:
			if loop > 0:
				before_medoids = new_medoids.copy()
				new_medoids = []
			# 各クラスタにおいて，クラスタ内の他の点との距離の合計が最小の点を新しいクラスタとしている
			for i in range(self.n_cluster):
				tmp = results.ix[results['label'] == i, :].copy()

				# 各点において他の点との距離の合計を求めている
				tmp['distance'] = np.sum(tmp.ix[:, ['x_' + str(id + 1) for id in tmp['id']]].values, axis=1)
				tmp = tmp.reset_index(drop=True)
				# 上記で求めた距離が最初の点を新たなmedoidとしている
				new_medoids.append(tmp.loc[tmp['distance'].idxmin(), 'id'])
			new_medoids = sorted(new_medoids)
			tmp_D = D[:, new_medoids]
			# 新しいmedoidのなかで距離が最も最小なクラスタを新たに選択
			clustaling_labels = np.argmin(tmp_D, axis=1)
			results['label'] = clustaling_labels
			loop += 1

		# resultsに必要情報を追加
		results = results.ix[:, ['id', 'label']]
		results['flag_medoid'] = 0
		for medoid in new_medoids:
			results.ix[results['id'] == medoid, 'flag_medoid'] = 1
		# 各medoidまでの距離
		tmp_D = pd.DataFrame(tmp_D, columns=['medoid_distance'+str(i) for i in range(self.n_cluster)])
		results = pd.concat([results, tmp_D], axis=1)

		self.results = results
		self.cluster_centers_ = new_medoids

		return results['label'].values

def KM(data,length):
	n_cluster = math.ceil(length/3.3)
	print("<h4>クラスタの数：\t{}</h4>".format(n_cluster))
	n_samples = len(data)
	labels = np.random.randint(0, n_cluster, n_samples)
	km = KMedoids(n_cluster = n_cluster)
	D = squareform(pdist(data, metric='euclidean'))
	predicted_labels = km.fit_predict(D) ## 予測ラベル
	centroids = km.cluster_centers_ ## 重心
	return predicted_labels,centroids
