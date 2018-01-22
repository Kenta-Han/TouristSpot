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

print("<html>")
print("<head>")
print ("Content-type:text/html; charset=UTF-8\r\n")
print("<link href='/data/stylesheet.css' rel='stylesheet' type='text/css' />")
print("<title>観光スポット推薦</title>")
print("</head>")
print("<body>")
print("<div class='box1'>")
print("<header>")
print("<h1>観光スポット推薦</h1>")
print("</header>")

form = cgi.FieldStorage()
type1 = form.getvalue('type1')
input1 = form.getvalue('input1')
input2 = form.getvalue('input2')
input3 = form.getvalue('input3')
sql_season0 = form.getvalue('sql_season0')
sql_season1 = form.getvalue('sql_season1')
season_word0 = form.getvalue('season_word0')
season_word1 = form.getvalue('season_word1')
sql_type0 = form.getvalue('sql_type0')
sql_type1 = form.getvalue('sql_type1')
type_word0 = form.getvalue('type_word0')
type_word1 = form.getvalue('type_word1')
type_word2 = form.getvalue('type_word2')
review_num = form.getvalue('review_num[]')
review_num = review_num.split(",")

# print("<h3>=== 選択レビュー表示 ===</h3>")
id1 = int(input1)-1
id2 = int(input2)-1
id3 = int(input3)-1

c.execute("select spot_id,name,review_text,wakachi2_text from unity_kantou where num='" + review_num[id1]+ "';")
review_all1 = []
for row in c:
    review_all1.append(list(row))

c.execute("select spot_id,name,review_text,wakachi2_text from unity_kantou where num='" + review_num[id2]+ "';")
review_all2 = []
for row in c:
    review_all2.append(list(row))

c.execute("select spot_id,name,review_text,wakachi2_text from unity_kantou where num='" + review_num[id3]+ "';")
review_all3 = []
for row in c:
    review_all3.append(list(row))
reviews = review_all1+review_all2+review_all3
# print(reviews)

## ====== レビュー(分かち書き) ======
review1_wakati = reviews[0][3].split()
review2_wakati = reviews[1][3].split()
review3_wakati = reviews[2][3].split()
review_wakati = [review1_wakati,review2_wakati,review3_wakati]
# print(review_wakati)
## ====== レビュー(分かち書き) 〆 ======


## ====== レビュー 全部 (分かち書きの単語をリストに入れる) 季節・タイプ ======
word = []
for i in range(len(review_wakati)) :
    for j in review_wakati[i] :
        word.append(j)
words = "'"+"','".join(word)+"'"
## ====== レビュー 全部 (分かち書きの単語をリストに入れる) 〆 ======


## ====== レビュー 各スポット (分かち書きの単語をリストに入れる) スポット ======
words_review1 = "'"+"','".join(review1_wakati)+"'"
words_review2 = "'"+"','".join(review2_wakati)+"'"
words_review3 = "'"+"','".join(review3_wakati)+"'"
words_review = [words_review1,words_review2,words_review3]
## ====== レビュー 各スポット (分かち書きの単語をリストに入れる) ======


## ====== レビュー(単語を季節のテーブルに問い合わせる) ======
######################### TFIDF #########################
c.execute(sql_season0 + " where word in (" + str(words) +");")
words_season_all_tfidf = []
for i in c:
    words_season_all_tfidf.append(i)
user_season_tfidf = myp_other.Change_To_Dic(words_season_all_tfidf)
######################### KLD #########################
c.execute(sql_season1 + " where word in (" + str(words) +");")
words_season_all_kld = []
for i in c:
    words_season_all_kld.append(i)
user_season_kld = myp_other.Change_To_Dic(words_season_all_kld)
## ====== レビュー(単語を季節のテーブルに問い合わせる)〆 ======


## ====== レビュー(単語をタイプのテーブルに問い合わせる) ======
######################### TFIDF #########################
c.execute(sql_type0 + " where word in (" + str(words) +");")
words_type_all_tfidf = []
for i in c:
    words_type_all_tfidf.append(i)
user_type_tfidf = myp_other.Change_To_Dic(words_type_all_tfidf)
######################### KLD #########################
c.execute(sql_type1 + " where word in (" + str(words) +");")
words_type_all_kld = []
for i in c:
    words_type_all_kld.append(i)
user_type_kld = myp_other. Change_To_Dic(words_type_all_kld)
## ====== レビュー(単語をタイプのテーブルに問い合わせる)〆 ======


## ====== レビュー(単語をスポットのテーブルに問い合わせる) ======
words_kantou = []
for i in range(len(reviews)):
    c.execute("select * from tfidf_unity_kantou where spot='" + reviews[i][1] + "' and word in (" + str(words_review[i]) + ");")
    for j in c:
        words_kantou.append(j)
user_words_kantou = myp_other.Change_To_Dic(words_kantou)
## ====== レビュー(単語をスポットのテーブルに問い合わせる)〆 ======


## ====== スポット検索(wordfとtfidf_kantouを使ってフィルタ) ======
search_spot = []
for i in tqdm(range(len(words_kantou))) :
    sql_search_spot = "select spot from tt_unity_kantou where word = '" + str(words_kantou[i][0]) +"' and tfidf_kantou > " + str(words_kantou[i][1] - 0.0001) + " and tfidf_kantou < "  + str(words_kantou[i][1] + 0.0001)
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
    c.execute("select spot,word,tfidf_kantou," + str(season_word0) + "," + str(type_word0) + " from tt_unity_kantou where spot in ('" + str(spot_list[i]) + "')")
    for j in c:
        spot_tfidf.append(list(j))
spot_kantou_tfidf = myp_spot.Kantou(spot_tfidf)
spot_season_tfidf = myp_spot.Season(spot_tfidf)
spot_type_tfidf = myp_spot.Type(spot_tfidf)
######################### KLD #########################
spot_kld = []
for i in tqdm(range(len(spot_list))) :
    c.execute("select spot,word,tfidf_kantou," + str(season_word1) + "," + str(type_word1) + " from tk_unity_kantou3 where spot in ('" + str(spot_list[i]) + "')")
    for j in c:
        spot_kld.append(list(j))
spot_season_kld = myp_spot.Season(spot_kld)
spot_type_kld = myp_spot.Type(spot_kld)
## ====== MySQLに問い合わせ〆 ======


## ====== コサイン類似度を使ってスポットを推薦 ======
spot_all_kantou_tfidf = user_words_kantou + spot_kantou_tfidf
kantou_tfidf_all = myp_other.Recommend_All(spot_all_kantou_tfidf,spot_list)
# ######################### TFIDF #########################
spot_all_season_tfidf = user_season_tfidf + spot_season_tfidf
season_tfidf_all = myp_other.Recommend_All(spot_all_season_tfidf,spot_list)
spot_all_type_tfidf = user_type_tfidf + spot_type_tfidf
type_tfidf_all = myp_other.Recommend_All(spot_all_type_tfidf,spot_list)
######################### KLD #########################
spot_all_season_kld = user_season_kld + spot_season_kld
season_kld_all = myp_other.Recommend_All(spot_all_season_kld,spot_list)
spot_all_type_kld = user_type_kld + spot_type_kld
type_kld_all = myp_other.Recommend_All(spot_all_type_kld,spot_list)
## ====== コサイン類似度を使ってスポットを推薦〆 ======


######################### TFIDf #########################
print("<h3>==== 推薦スポット(TOP10---TFIDF---) ====</h3>")
# myp_other.Average111(kantou_tfidf_all,season_tfidf_all,type_tfidf_all)
print("<div class='top10'>")
myp_other.Average112(kantou_tfidf_all,season_tfidf_all,type_tfidf_all)
print("</div>")
######################### KLD #########################
print("<h3>==== 推薦スポット(TOP10---単語出現確率---) ====</h3>")
print("<div class='top10'>")
myp_other.Average112(kantou_tfidf_all,season_kld_all,type_kld_all)
print("</div>")

print("<form action='select_type1.py' method='post'>")
print("<input type='submit' value='タイプ選択へ' class='submit1'/>")
print("</form>")

print("</div>")
print("</body>")
print("</html>")

c.close
connect.close
