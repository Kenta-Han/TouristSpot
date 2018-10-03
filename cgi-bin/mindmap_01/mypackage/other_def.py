import MySQLdb
import math
from tqdm import tqdm
import mypackage.cos_sim_class as myp_cos
from gensim import corpora
from gensim import models

# DBに接続しカーソルを取得する
conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan', charset='utf8')
cur = conn.cursor()
sc = myp_cos.SimCalculator()

## エリアIDリスト作成
def Area_id_List(area):
	area_id_list = []
	cur.execute(area)
	for i in cur:
		area_id_list.append(i[0])
	return area_id_list

## スポット，レビューリスト作成
def SpotORReview_List(spot):
	spot_list = []
	cur.execute(spot)
	for i in cur:
		spot_list.append(i)
	return spot_list

## ====== スポット毎のレビュー ======
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
## ====== スポット毎のレビュー〆 ======

## ====== エリア内orユーザ履歴のスポットの全レビュー ======
def AllSpot_Review(review_list):
	review_wkt_all = []
	for i in range(len(review_list)):
	    temp = review_list[i][1].split()
	    review_wkt_all.append(temp)
	    temp = []
	return review_wkt_all
## ====== エリア内orユーザ履歴のスポットの全レビュー〆 ======


## TFIDFを求める
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
	for wod in tqdm(corpus_tfidf):
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


## ユーザ選んだレビューを辞書で一つのリストにまとめる
def Change_To_Dic(words):
	spot = []
	search_dic = {}
	for i in words:
		search_dic[i[0]] = i[1]
	spot.append(search_dic)
	return spot


## 全ての観光地を類似度を出す
def Recommend_All(spot_all,spot_list):
	i = 1
	value = []
	while (i < len(spot_all) - 1):
		cos = sc.sim_cos(spot_all[0],spot_all[i])
		value.append(cos)
		i += 1
	dic = dict(zip(spot_list,value)) ## 辞書作成 (スポット名,類似度)
	# print(dic)
	result = sorted(dic.items(),key=lambda x:x[1],reverse=True) ##降順にソート
	# print(result)
	recommend_spot_list = []
	for i in range(len(result)):
		a = []
		if i >= len(result):
			continue
		cur.execute("select spot_id from unity_kantou where name ='" + result[i][0] + "';")
		spot_id = cur.fetchone()
		recommend_spot_list.append([spot_id[0],result[i][0],result[i][1]])
	return recommend_spot_list

## チェックしているかどうかを判断
def Check(check1,check2,check3,count,go):
	if check1 == None:
		check1 = 0
	elif type(check1) == str:
		check1 = ','.join([check1])
	else:
		check1 = ','.join(check1)

	if check2 == None:
		check2 = 0
	elif type(check2) == str:
		check2 = ','.join([check2])
	else:
		check2 = ','.join(check2)

	if check3 == None:
		check3 = 0
	elif type(check3) == str:
		check3 = ','.join([check3])
	else:
		check3 = ','.join(check3)

	if count == None:
		count_list = []
		count = 0
	elif type(count) == str:
		count_list = ','.join([count])
		count = len([count])
	else:
		count_list = ','.join(count)
		count = len(count)

	if go == None:
		go_list = []
		go = 0
	elif type(go) == str:
		go_list = ','.join([go])
		go = len([go])
	else:
		go_list = ','.join(go)
		go = len(go)

	return check1,check2,check3,count_list,count,go_list,go
