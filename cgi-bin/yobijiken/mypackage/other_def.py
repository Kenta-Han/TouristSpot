import MySQLdb
import math
from tqdm import tqdm
import mypackage.cos_sim_class as myp_cos
from gensim import corpora
from gensim import models

# DBに接続しカーソルを取得する
connect = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan', charset='utf8')
c = connect.cursor()

sc = myp_cos.SimCalculator()

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


## スポットリスト作成
def Spot_Kantou_List(spot):
	spot_kantou_list = []
	c.execute(spot)
	for i in c:
		spot_kantou_list.append(i[0])
	# print(spot_kantou_list)
	return spot_kantou_list


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
		c.execute("select spot_id from unity_kantou where name ='" + result[i][0] + "';")
		spot_id = c.fetchone()
		recommend_spot_list.append([spot_id[0],result[i][0],result[i][1]])
	return recommend_spot_list


#############################################
##### yobijiken用
#############################################
## Top10を表示
def Top10_yobi(average):
	result = sorted(average,key=lambda x:x[2],reverse=True)
	# print("<h4>==== トップ10 ====</h4>")
	spot_list = []
	column_list = ["spot01","spot02","spot03","spot04","spot05","spot06","spot07","spot08","spot09","spot10"]

	print("<table class='imagetable'>")
	print("<tr><th>観光スポット</th><th>要求1</th><th>要求2</th><th>要求3</th><th>季節</th><th>タイプ</th></tr>")
	for i,column in zip(range(len(result)),column_list): ## トップ10を表示
		if i >= 10:
			continue
		print("<tr><th><a href='http://www.jalan.net/kankou/")
		print(str(result[i][0]))
		print("/' target='_blank'>")
		print(result[i][1])
		# print(str(result[i][2])) ## 類似度
		print("</a></th><td><input type='checkbox' name='check_1' value='"+result[i][1]+"'></td><td><input type='checkbox' name='check_2' value='"+result[i][1]+"'></td><td><input type='checkbox' name='check_3' value='"+result[i][1]+"'></td><td><input type='checkbox' name='count' value='"+result[i][1]+"'></td><td><input type='checkbox' name='count' value='"+result[i][1]+"'></td></tr>")

		# c.execute("update exp_data_proposal_test set " + column + "='" + result[i][1] + "' where id=" + str(user_max_id) + ";")
		# connect.commit()
	print("</table>")

## 関東1 : 季節2.5 : タイプ2.5(予備実験用)
def Average122_yobi(kantou,season,type_all):
	result = []
	for i in range(len(kantou)):
		for j in range(len(season)):
			for k in range(len(type_all)):
				if (kantou[i][1] == season[j][1]) and (season[j][1] == type_all[k][1]):
					math = (kantou[i][2]/6 + season[j][2]*2.5/6 + type_all[k][2]*2.5/6) / 3
					result.append([kantou[i][0],kantou[i][1],math])
	result = Top10_yobi(result)
	# return result
