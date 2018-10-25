# -*- coding: utf-8 -*-
import MySQLdb
import time
import numpy as np
from gensim import corpora
from gensim import models
from pprint import pprint
from operator import itemgetter
from tqdm import tqdm
import re

# DBに接続しカーソルを取得する
conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

def Spot_List(select_spot):
    spot_list = []
    cur.execute(select_spot)
    for i in cur:
        spot_list.append(i)
    return spot_list

try:
	## レビュー全体：各スポットで1文書と見なす(1個目の空白の前は場所を示している)
	select_wakachi2 = "SELECT name,group_concat(wakachi2 separator '') FROM review_all GROUP BY name;"
	spot_list = Spot_List(select_wakachi2)
	docs = []
	for i in range(len(spot_list)):
		line = spot_list[i][1]
		docs.append(line.split())
	dictionary = corpora.Dictionary(docs) ## 単語にidを振る

	## itemの中は(単語,単語index)
	#print(dictionary.token2id.items())
	## 単語と単語indexの配置を逆転→(3896:'私')
	dictionary_inv = {}
	for dic in dictionary.token2id.items():
		dictionary_inv[dic[1]]=dic[0]
		#print(dictionary_inv)
	corpus = list(map(dictionary.doc2bow,docs)) ## テキストのコーパス化
	## コーパスからtfidfモデルを生成(正規化済み)
	test_model = models.TfidfModel(corpus)
	corpus_tfidf = list(test_model[corpus]) ## コーパスに適用

	## 対応する数値を文字に変える
	j = 0
	doc = [] ## id表示ではないもの
	for word in tqdm(corpus_tfidf):
		i = 0
		doc.append('') ## 空要素
		temp = []
		for ch in word:
			temp.append('')
			temp[i] = [dictionary_inv[ch[0]],ch[1]]
			i += 1
		doc[j] = temp
		j += 1
		# print(doc2)

	bytesymbols = re.compile("[!-/:-@[-`{-~]") ## 半角記号
	k = 0
	for word in tqdm(doc):
		i = 0
		copyw = word
		if word==[]:
			continue
		for w in word:
			w[1] = str(w[1])
			copyw[i] = '：'.join(w)
			copyw[i] = '：'.join([copyw[i],spot_list[k][0]])
			i+=1
		k+=1
		# print(copyw)
		for i in range(len(copyw)):
			count_kigo = copyw[i].count('：') ## 1行中の：の数
			if count_kigo >= 3:
				continue
			else:
				copyw[i] = copyw[i].split("：")
				d = re.search(bytesymbols,copyw[i][0])
				e = re.search('^\d', copyw[i][1])
				if (d != None) or (e == None) :
					continue
				insert_tfidf = "INSERT INTO tfidf_by_wakachi2 VALUES('{}',{},'{}')".format(copyw[i][0],copyw[i][1],copyw[i][2])
				cur.execute(insert_tfidf)
				conn.commit()

except MySQLdb.Error as error:
	print("===MySQLdb.Error===\n",error)

# cur.close
# conn.close
