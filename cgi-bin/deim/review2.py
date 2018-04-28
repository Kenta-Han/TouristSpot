#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import sys
import math
from tqdm import tqdm
import spot_def as myp_spot
import other_def as myp_other

# DBに接続しカーソルを取得する
connect = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan', charset='utf8')
c = connect.cursor()

form = cgi.FieldStorage()
type_id = int(form.getvalue('type_id')) ##タイプ

input_data = [form.getvalue('input1')]
sql_season = [form.getvalue('sql_season0'),form.getvalue('sql_season1')]
season_word = [form.getvalue('season_word0'),form.getvalue('season_word1'),form.getvalue('season_word2')]
sql_type = [form.getvalue('sql_type0'),form.getvalue('sql_type1')]
type_word = [form.getvalue('type_word0'),form.getvalue('type_word1'),form.getvalue('type_word2')]
review_num = form.getvalue('review_num[]')
review_num = review_num.split(",")

id_data = [int(input_data[0])-1]

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='../../data/stylesheet_deim.css' rel='stylesheet' type='text/css' />
<title>観光スポット</title>
</head>
<body>
<div id='wrap'>
<header><h1 class='title'>観光スポット検索</h1></header>
"""
print(html_body)

# ====== レビュー　ユーザの選択 ======
selected_column_list=["review_selected1"]
review_user = []
for i in id_data:
    c.execute("select spot_id,name,review_text,wakachi2_text from unity_kantou where num='" + review_num[i]+ "';")
    for row,column in zip(c,selected_column_list):
        review_user.append(list(row))

# ====== レビュー(分かち書き) ======
review1_wkt = review_user[0][3].split()
review_wakati = [review1_wkt]
review_wkt_user = []
review_wkt_user.extend(review1_wkt)
# ====== レビュー(分かち書き) 〆 ======
# ====== レビュー　ユーザの選択 〆 ======

# ====== レビュー　ユーザの選択以外 ======
figure = []
for num in review_num:
    if num == review_num[id_data[0]]:
        continue
    figure.append(num)

review_nouser = []
for i in range(len(figure)):
    c.execute("select spot_id,name,review_text,wakachi2_text from unity_kantou where num='" + figure[i]+ "';")
    for row in c.fetchall():
        review_nouser.append(list(row))

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
words_review = [words_review1]
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
    sql_search_spot = "select spot from tt_unity_kantou where word = '" + str(words_kantou[0][i][0]) +"' and tfidf_kantou > " + str(words_kantou[0][i][1] - 0.01) + " and tfidf_kantou < "  + str(words_kantou[0][i][1] + 0.01)
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
print("<br><br><div class='top10' style='text-align: center; width:60%; margin:auto; font-size:20px;'>")
print("<form action='deim.py' method='post' style='text-align: center;'>")
myp_other.Average122_deim(kantou_tfidf_all,season_kld_all,type_kld_all)
print("<input type='submit' value='ホームへ' class='button1'/>")
print("</form>")
print("</div>")

print("</div>")
print("</body></html>")

c.close
connect.close
