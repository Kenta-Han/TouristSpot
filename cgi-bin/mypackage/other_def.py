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
##### jiken2用
#############################################
## Top10を表示
def Top10_jiken2(average,record_id):
	result = sorted(average,key=lambda x:x[2],reverse=True)
	# print("<h4>==== トップ10 ====</h4>")
	spot_list = []
	column_list = ["review_spot01","review_spot02","review_spot03","review_spot04","review_spot05","review_spot06","review_spot07","review_spot08","review_spot09","review_spot10"]

	print("<table class='review_table'>")
	print("<tr><th>観光スポット</th><th>要求1</th><th>要求2</th><th>要求3</th><th>既知</th></tr>")
	for i,column in zip(range(len(result)),column_list): ## トップ10を表示
		if i >= 10:
			continue
		print("<tr><th><a href='http://www.jalan.net/kankou/")
		print(str(result[i][0]))
		print("/' target='_blank'>")
		print(result[i][1])
		# print(str(result[i][2])) ## 類似度
		print("</a></th><td><input type='checkbox' name='review_check1' value='"+result[i][1]+"'></td><td><input type='checkbox' name='review_check2' value='"+result[i][1]+"'></td><td><input type='checkbox' name='review_check3' value='"+result[i][1]+"'></td><td><input type='checkbox' name='review_count' value='"+result[i][1]+"'></td></tr>")

		c.execute("update jiken2 set " + column + "='" + result[i][1] + "' where id=" + str(record_id) + ";")
		connect.commit()
	print("</table>")

## 関東1 : 季節2.5 : タイプ2.5
def Average122_jiken2(kantou,season,type_all,record_id):
	result = []
	for i in range(len(kantou)):
		for j in range(len(season)):
			for k in range(len(type_all)):
				if (kantou[i][1] == season[j][1]) and (season[j][1] == type_all[k][1]):
					math = (kantou[i][2]/6 + season[j][2]*2.5/6 + type_all[k][2]*2.5/6) / 3
					result.append([kantou[i][0],kantou[i][1],math])
	result = Top10_jiken2(result,record_id)
	# return result

## チェックしているかどうかを判断
def Check(check1,check2,check3,count):
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

	return check1,check2,check3,count,count_list


#############################################
##### jiken1用
#############################################
## Top10を表示
def Top10(average,user_max_id):
	result = sorted(average,key=lambda x:x[2],reverse=True)
	# print("<h4>==== トップ10 ====</h4>")
	spot_list = []
	column_list = ["spot01","spot02","spot03","spot04","spot05","spot06","spot07","spot08","spot09","spot10"]

	print("<table class='imagetable'>")
	print("<tr><th>観光スポット</th><th>キーワード1</th><th>キーワード2</th><th>キーワード3</th><th>既知</th></tr>")
	for i,column in zip(range(len(result)),column_list): ## トップ10を表示
		if i >= 10:
			continue
		print("<tr><th><a href='http://www.jalan.net/kankou/")
		print(str(result[i][0]))
		print("/' target='_blank'>")
		print(result[i][1])
		# print(str(result[i][2])) ## 類似度
		print("</a></th><td><input type='checkbox' name='check_1' value='"+result[i][1]+"'></td><td><input type='checkbox' name='check_2' value='"+result[i][1]+"'></td><td><input type='checkbox' name='check_3' value='"+result[i][1]+"'></td><td><input type='checkbox' name='count' value='"+result[i][1]+"'></td></tr>")

		c.execute("update exp_data_proposal_test set " + column + "='" + result[i][1] + "' where id=" + str(user_max_id) + ";")
		connect.commit()
	print("</table>")

## 関東1 : 季節1 : タイプ1
def Average111(kantou,season,type_all,user_max_id):
	result = []
	for i in range(len(kantou)):
		for j in range(len(season)):
			for k in range(len(type_all)):
				if (kantou[i][1] == season[j][1]) and (season[j][1] == type_all[k][1]):
					math = (kantou[i][2] + season[j][2] + type_all[k][2]) / 3
					result.append([kantou[i][0],kantou[i][1],math])
	result = Top10(result,user_max_id)
	# return result

## 関東2 : 季節1 : タイプ1
def Average211(kantou,season,type_all,user_max_id):
	result = []
	for i in range(len(kantou)):
		for j in range(len(season)):
			for k in range(len(type_all)):
				if (kantou[i][1] == season[j][1]) and (season[j][1] == type_all[k][1]):
					math = (kantou[i][2]*2/4 + season[j][2]/4 + type_all[k][2]/4) / 3
					result.append([kantou[i][0],kantou[i][1],math])
	result = Top10(result,user_max_id)
	# return result

## 関東1 : 季節2 : タイプ1
def Average121(kantou,season,type_all,user_max_id):
	result = []
	for i in range(len(kantou)):
		for j in range(len(season)):
			for k in range(len(type_all)):
				if (kantou[i][1] == season[j][1]) and (season[j][1] == type_all[k][1]):
					math = (kantou[i][2]/4 + season[j][2]*2/4 + type_all[k][2]/4) / 3
					result.append([kantou[i][0],kantou[i][1],math])
	result = Top10(result,user_max_id)
	# return result

## 関東1 : 季節1 : タイプ2
def Average112(kantou,season,type_all,user_max_id):
	result = []
	for i in range(len(kantou)):
		for j in range(len(season)):
			for k in range(len(type_all)):
				if (kantou[i][1] == season[j][1]) and (season[j][1] == type_all[k][1]):
					math = (kantou[i][2]/4 + season[j][2]/4 + type_all[k][2]*2/4) / 3
					result.append([kantou[i][0],kantou[i][1],math])
	result = Top10(result,user_max_id)
	# return result

## 関東1 : 季節2.5 : タイプ2.5
def Average122(kantou,season,type_all,user_max_id):
	result = []
	for i in range(len(kantou)):
		for j in range(len(season)):
			for k in range(len(type_all)):
				if (kantou[i][1] == season[j][1]) and (season[j][1] == type_all[k][1]):
					math = (kantou[i][2]/6 + season[j][2]*2.5/6 + type_all[k][2]*2.5/6) / 3
					result.append([kantou[i][0],kantou[i][1],math])
	result = Top10(result,user_max_id)
	# return result



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



#############################################
##### deim用
#############################################
## Top10を表示
def Top10_deim(average):
	result = sorted(average,key=lambda x:x[2],reverse=True)
	# print("<h4>==== トップ10 ====</h4>")
	spot_list = []
	column_list = ["spot01","spot02","spot03","spot04","spot05","spot06","spot07","spot08","spot09","spot10"]

	print("<ol>")
	for i,column in zip(range(len(result)),column_list): ## トップ10を表示
		if i >= 10:
			continue
		print("<li><a href='http://www.jalan.net/kankou/")
		print(str(result[i][0]))
		print("/' target='_blank'>")
		print(result[i][1])
		# print(str(result[i][2])) ## 類似度
		print("</a></li>")
	print("</ol>")

## 関東1 : 季節2.5 : タイプ2.5(予備実験用)
def Average122_deim(kantou,season,type_all):
	result = []
	for i in range(len(kantou)):
		for j in range(len(season)):
			for k in range(len(type_all)):
				if (kantou[i][1] == season[j][1]) and (season[j][1] == type_all[k][1]):
					math = (kantou[i][2]/6 + season[j][2]*2.5/6 + type_all[k][2]*2.5/6) / 3
					result.append([kantou[i][0],kantou[i][1],math])
	result = Top10_deim(result)
	# return result
