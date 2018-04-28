#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import sys
import math
from tqdm import tqdm
import mypackage.spot_def as myp_spot
import mypackage.other_def as myp_other

# DBに接続しカーソルを取得する
connect = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan', charset='utf8')
c = connect.cursor()

form = cgi.FieldStorage()
record_id = form.getvalue('record_id')
type_id = int(form.getvalue('type_id')) ##タイプ
keyword = [form.getvalue('keyword1'),form.getvalue('keyword2'),form.getvalue('keyword3')] ##要求3つ

input_data = [form.getvalue('input1'),form.getvalue('input2'),form.getvalue('input3')]
sql_season = [form.getvalue('sql_season0'),form.getvalue('sql_season1')]
season_word = [form.getvalue('season_word0'),form.getvalue('season_word1'),form.getvalue('season_word2')]
sql_type = [form.getvalue('sql_type0'),form.getvalue('sql_type1')]
type_word = [form.getvalue('type_word0'),form.getvalue('type_word1'),form.getvalue('type_word2')]
review_num = form.getvalue('review_num')
review_num = review_num.split(",")

id_data = [int(input_data[0])-1,int(input_data[1])-1,int(input_data[2])-1]

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='../../data/new_stylesheet.css' rel='stylesheet' type='text/css' />
<title>観光スポット</title>
</head>
<body>
<div id='wrap'>
<header><h1 class='title'>観光スポット検索(A)</h1></header>
"""
print(html_body)

# ====== レビュー　ユーザの選択 ======
selected_column_list=["review_selected1","review_selected2","review_selected3"]
review_user = []
for i in id_data:
    c.execute("select spot_id,name,review_text,wakachi2_text from unity_kantou where num='" + review_num[i]+ "';")
    for row,column in zip(c,selected_column_list):
        review_user.append(list(row))

# ====== 選択レビュー(insert) ======
sql_update = "update jiken2 set {column1} ='{r_user1}',{column2}='{r_user2}',{column3}='{r_user3}' where id = {record_id};"
c.execute(sql_update.format(column1=selected_column_list[0],r_user1=review_user[0][2],column2=selected_column_list[1],r_user2=review_user[1][2],column3=selected_column_list[2],r_user3=review_user[2][2],record_id=str(record_id)))

# ====== 選択レビュー(insert) 〆 ======

# ====== レビュー(分かち書き) ======
review1_wkt = review_user[0][3].split()
review2_wkt = review_user[1][3].split()
review3_wkt = review_user[2][3].split()
review_wakati = [review1_wkt,review2_wkt,review3_wkt]
review_wkt_user = []
review_wkt_user.extend(review1_wkt)
review_wkt_user.extend(review2_wkt)
review_wkt_user.extend(review3_wkt)
# ====== レビュー(分かち書き) 〆 ======
# ====== レビュー　ユーザの選択 〆 ======

# ====== レビュー　ユーザの選択以外 ======
figure = []
for num in review_num:
    if num == review_num[id_data[0]] or num == review_num[id_data[1]] or num == review_num[id_data[2]]:
        continue
    figure.append(num)

review_nouser = []
for i in range(len(figure)):
    c.execute("select spot_id,name,review_text,wakachi2_text from unity_kantou where num='" + figure[i]+ "';")
    for row in c.fetchall():
        review_nouser.append(list(row))

review_column = ["review01","review02","review03","review04","review05","review06","review07","review08","review09","review10","review11","review12","review13","review14","review15","review16","review17"]

for i,column in zip(range(len(review_nouser)),review_column):
    c.execute("update jiken2 set " + column + "='" + review_nouser[i][2] + "' where id=" + str(record_id) + ";")
    connect.commit()

review_wkt_nouser = []
for i in range(len(review_nouser)):
    a = review_nouser[i][3].split()
    review_wkt_nouser.append(a)
    a = []
# ====== レビュー　ユーザの選択以外 〆 ======

review_wkt_nouser.insert(0,review_wkt_user)
words_kantou = myp_other.Tfidf(review_wkt_nouser)

## ====== レビュー 全部 (分かち書きの単語をリストに入れる) 季節・タイプ ======
word = []
for i in range(len(review_wakati)) :
    for j in review_wakati[i] :
        word.append(j)
words = "'"+"','".join(word)+"'"
## ====== レビュー 全部 (分かち書きの単語をリストに入れる) 〆 ======

## ====== レビュー 各スポット (分かち書きの単語をリストに入れる) スポット ======
words_review1 = "'"+"','".join(review1_wkt)+"'"
words_review2 = "'"+"','".join(review2_wkt)+"'"
words_review3 = "'"+"','".join(review3_wkt)+"'"
words_review = [words_review1,words_review2,words_review3]
# print(words_review)
## ====== レビュー 各スポット (分かち書きの単語をリストに入れる) ======

## ====== レビュー(単語を季節のテーブルに問い合わせる) ======
######################### TFIDF #########################
c.execute(sql_season[0] + " where word in (" + str(words) +");")
words_season_all_tfidf = []
for i in c:
    words_season_all_tfidf.append(i)
user_season_tfidf = myp_other.Change_To_Dic(words_season_all_tfidf)
######################### KLD #########################
c.execute(sql_season[1] + " where word in (" + str(words) +");")
words_season_all_kld = []
for i in c:
    words_season_all_kld.append(i)
user_season_kld = myp_other.Change_To_Dic(words_season_all_kld)
## ====== レビュー(単語を季節のテーブルに問い合わせる)〆 ======

## ====== レビュー(単語をタイプのテーブルに問い合わせる) ======
######################### TFIDF #########################
c.execute(sql_type[0] + " where word in (" + str(words) +");")
words_type_all_tfidf = []
for i in c:
    words_type_all_tfidf.append(i)
user_type_tfidf = myp_other.Change_To_Dic(words_type_all_tfidf)
######################### KLD #########################
c.execute(sql_type[1] + " where word in (" + str(words) +");")
words_type_all_kld = []
for i in c:
    words_type_all_kld.append(i)
user_type_kld = myp_other. Change_To_Dic(words_type_all_kld)
## ====== レビュー(単語をタイプのテーブルに問い合わせる)〆 ======

## ====== レビュー(単語をスポットのテーブルに問い合わせる) ======
user_words_kantou = myp_other.Change_To_Dic(words_kantou[0])
## ====== レビュー(単語をスポットのテーブルに問い合わせる)〆 ======

## ====== スポット検索(wordfとtfidf_kantouを使ってフィルタ) ======
search_spot = []
for i in tqdm(range(len(words_kantou[0]))) :
    sql_search_spot = "select spot from tt_unity_kantou where word = '" + str(words_kantou[0][i][0]) +"' and tfidf_kantou > " + str(words_kantou[0][i][1] - 0.001) + " and tfidf_kantou < "  + str(words_kantou[0][i][1] + 0.001)
    c.execute(sql_search_spot)
    for j in c:
        search_spot.append(j[0])
search_spot.sort()
spot_list = []
for i in range(len(search_spot) - 1) :
    if search_spot[i] == search_spot[i+1] :
        continue
    spot_list.append(search_spot[i])
## ====== スポット検索(wordfとtfidf_kantouを使ってフィルタ)〆 ======

## ====== MySQLに問い合わせ ======
######################### TFIDF #########################
spot_tfidf = []
for i in tqdm(range(len(spot_list))) :
    c.execute("select spot,word,tfidf_kantou," + str(season_word[0]) + "," + str(type_word[0]) + " from tt_unity_kantou where spot in ('" + str(spot_list[i]) + "')")
    for j in c:
        spot_tfidf.append(list(j))
spot_kantou_tfidf = myp_spot.Kantou(spot_tfidf)
######################### KLD #########################
spot_kld = []
for i in tqdm(range(len(spot_list))) :
    c.execute("select spot,word,tfidf_kantou," + str(season_word[1]) + "," + str(type_word[1]) + " from tk_unity_kantou3 where spot in ('" + str(spot_list[i]) + "')")
    for j in c:
        spot_kld.append(list(j))
spot_season_kld = myp_spot.Season(spot_kld)
spot_type_kld = myp_spot.Type(spot_kld)
## ====== MySQLに問い合わせ〆 ======

## ====== コサイン類似度を使ってスポットを推薦 ======
######################### TFIDF #########################
spot_all_kantou_tfidf = user_words_kantou + spot_kantou_tfidf
kantou_tfidf_all = myp_other.Recommend_All(spot_all_kantou_tfidf,spot_list)
######################### KLD #########################
spot_all_season_kld = user_season_kld + spot_season_kld
season_kld_all = myp_other.Recommend_All(spot_all_season_kld,spot_list)
spot_all_type_kld = user_type_kld + spot_type_kld
type_kld_all = myp_other.Recommend_All(spot_all_type_kld,spot_list)
## ====== コサイン類似度を使ってスポットを推薦〆 ======

######################### KLD #########################
print("<div class='top10' style='text-align: center;'>")
print("<p>以下の観光スポットを押すとじゃらんの紹介ページが開きます．</br>内容を確認した上でいくつか選択してください．</br>「要求」:要求に満たしているならチェックしてください．</br>「既知」:既知の観光スポットならチェックしてください </p>")
print("<p>要求1：" + str(keyword[0]) + "，要求2：" + str(keyword[1]) + "，要求3：" + str(keyword[2]) + "</p>")

print("<div style='text-align:center;'>")
print("<form action='review0_step3.py' method='post'>")
myp_other.Average122_jiken2(kantou_tfidf_all,season_kld_all,type_kld_all,record_id)

print("<h2>意見：</h2>")
print("<textarea name='review_msg' cols=70 rows=7 /></textarea>")
print("<input type='hidden' name='record_id' value='" + str(record_id) + "'>")
print("</br><input type='submit' value='次へ' class='button1'/>")
print("</form>")

print("</div>")
print("</div>")

print("</div>")
print("</body></html>")

c.close
connect.close
