#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import datetime
import sys
import mypackage.other_def as myp_other

# DBに接続しカーソルを取得する
connect = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan', charset='utf8')
c = connect.cursor()

print("<!DOCTYPE html>")
print("<head>")
print("Content-type:text/html; charset=UTF-8\r\n")
print("<link href='../../data/stylesheet.css' rel='stylesheet' type='text/css' />")
print("<title>レビュー選択</title>")
print("</head>")
print("<body>")
print("<div class='box1'>")
print("<header>")
print("<h1>観光スポット推薦</h1>")
print("</header>")
## ====== 季節 ======
now = datetime.datetime.today() ## 現在の日付を取得
if now.month >= 3 and now.month <= 5 :
    sql_season = ["select * from tfidf_season_spring","select * from kld_season_spring3"]
    season_word = ["tfidf_spring","kld_spring"]
    season ="spring"
elif now.month >= 6 and now.month <= 8 :
    sql_season= ["select * from tfidf_season_summer","select * from kld_season_summer3"]
    season_word = ["tfidf_summer","kld_summer"]
    season ="summer"
elif now.month >= 9 and now.month <= 11 :
    sql_season = ["select * from tfidf_season_autumn","select * from kld_season_autumn3"]
    season_word = ["tfidf_autumn","kld_autumn"]
    season ="autumn"
elif now.month == 12 or (now.month >= 1 and now.month <= 2) :
    sql_season = ["select * from tfidf_season_winter","select * from kld_season_winter3"]
    season_word = ["tfidf_winter","kld_winter"]
    season ="winter"
## ====== 季節〆 ======

## ====== タイプ ======
form = cgi.FieldStorage()
type1 = form.getvalue('type1')

type_all = ["一人","カップル・夫婦","家族","友達同士","その他"]
cnt_type_all = 1
type_id = int(type1)

if type_id  == 1 :
    type_word = ["tfidf_alone","kld_alone","一人"]
    sql_type = ["select * from tfidf_type_alone","select * from kld_type_alone3"]
elif type_id == 2 :
    type_word = ["tfidf_couple","kld_couple","カップル・夫婦"]
    sql_type = ["select * from tfidf_type_couple","select * from kld_type_couple"]
elif type_id == 3 :
    type_word = ["tfidf_family","kld_family","家族"]
    sql_type = ["select * from tfidf_type_family","select * from kld_type_family"]
elif type_id == 4 :
    type_word = ["tfidf_friend","kld_friend","友達同士"]
    sql_type = ["select * from tfidf_type_friend","select * from kld_type_friend"]
elif type_id == 5 :
    type_word = ["tfidf_other","kld_other","その他"]
    sql_type = ["select * from tfidf_type_other","select * from kld_type_other"]
## ====== タイプ〆 ======

## ====== 関東スポットリスト ======
name = "select distinct name from spot_area_kantou where name != '';"
spot_kantou_list = myp_other.Spot_Kantou_List(name)
area1 = "select distinct area1 from spot_area_kantou where area1 != '';"
spot_kantou_list1 = myp_other.Spot_Kantou_List(area1)
area2 = "select distinct area2 from spot_area_kantou where area2 != '';"
spot_kantou_list2 = myp_other.Spot_Kantou_List(area2)
area3 = "select distinct area3 from spot_area_kantou where area3 != '';"
spot_kantou_list3 = myp_other.Spot_Kantou_List(area3)
spot_kantou_list = spot_kantou_list + spot_kantou_list1 + spot_kantou_list2 + spot_kantou_list3
## ====== 関東スポットリスト〆 ======

## ====== レビュー(ランダム表示) ======
c.execute("select cast(num as char),review_text from unity_kantou where companion='" + type_word[2] +"' and season4='"+ season +"' order by rand() limit 20")


cnt_review = 1
review_all = []
for row in c: ## 1行ずつ読み込
    review_all.append(list(row))
    cnt_review += 1
## ====== レビュー(ランダム表示)〆 ======

## ====== レビュー(選択) ======
for i in range(len(review_all)):
    for j in range(len(spot_kantou_list)):
        if (spot_kantou_list[j] in review_all[i][1]) == True:
            review_all[i][1] = review_all[i][1].replace(spot_kantou_list[j],'〇〇')
cnt = 1

for i in range(len(review_all)):
    print("<p>")
    print("<strong>ID：")
    print(str(cnt))
    print("</strong><br/><strong>Review：</strong>")
    print(str(review_all[i][1]))
    print("</p>")
    cnt += 1

print("<h3>==== レビューを３つを選択してください ====</h3>")
pulldown = """
<table class='imagetable'>
<tr>
<td>レビュー1：<select name='input1' form='example'>
<option value='1'>1</option>
<option value='2'>2</option>
<option value='3'>3</option>
<option value='4'>4</option>
<option value='5'>5</option>
<option value='6'>6</option>
<option value='7'>7</option>
<option value='8'>8</option>
<option value='9'>9</option>
<option value='10'>10</option>
<option value='11'>11</option>
<option value='12'>12</option>
<option value='13'>13</option>
<option value='14'>14</option>
<option value='15'>15</option>
<option value='16'>16</option>
<option value='17'>17</option>
<option value='18'>18</option>
<option value='19'>19</option>
<option value='20'>20</option>
</select>
</td><td>レビュー2：<select name='input2' form='example'>
<option value='1'>1</option>
<option value='2'>2</option>
<option value='3'>3</option>
<option value='4'>4</option>
<option value='5'>5</option>
<option value='6'>6</option>
<option value='7'>7</option>
<option value='8'>8</option>
<option value='9'>9</option>
<option value='10'>10</option>
<option value='11'>11</option>
<option value='12'>12</option>
<option value='13'>13</option>
<option value='14'>14</option>
<option value='15'>15</option>
<option value='16'>16</option>
<option value='17'>17</option>
<option value='18'>18</option>
<option value='19'>19</option>
<option value='20'>20</option>
</select>
</td><td>レビュー3：<select name='input3' form='example'>
<option value='1'>1</option>
<option value='2'>2</option>
<option value='3'>3</option>
<option value='4'>4</option>
<option value='5'>5</option>
<option value='6'>6</option>
<option value='7'>7</option>
<option value='8'>8</option>
<option value='9'>9</option>
<option value='10'>10</option>
<option value='11'>11</option>
<option value='12'>12</option>
<option value='13'>13</option>
<option value='14'>14</option>
<option value='15'>15</option>
<option value='16'>16</option>
<option value='17'>17</option>
<option value='18'>18</option>
<option value='19'>19</option>
<option value='20'>20</option>
</select>
</td></tr></table>
"""

print("<div class='review'>")
print(pulldown)

print("<form method='post' action='step2.py' id='example'>")
print("<h4><input type='hidden' name='type1' value='"+type1+"'></h4>")
print("<input type='hidden' name='sql_season0' value='"+sql_season[0]+"'>")
print("<input type='hidden' name='sql_season1' value='"+sql_season[1]+"'>")
print("<input type='hidden' name='season_word0' value='"+season_word[0]+"'>")
print("<input type='hidden' name='season_word1' value='"+season_word[1]+"'>")
print("<input type='hidden' name='season' value='"+season+"'>")
print("<input type='hidden' name='sql_type0' value='"+sql_type[0]+"'>")
print("<input type='hidden' name='sql_type1' value='"+sql_type[1]+"'>")
print("<input type='hidden' name='type_word0' value='"+type_word[0]+"'>")
print("<input type='hidden' name='type_word1' value='"+type_word[1]+"'>")
print("<input type='hidden' name='type_word2' value='"+type_word[2]+"'>")
print("<input type='hidden' name='review_num[]' value='"+review_all[0][0]+","+review_all[1][0]+","+review_all[2][0]+","+review_all[3][0]+","+review_all[4][0]+","+review_all[5][0]+","+review_all[6][0]+","+review_all[7][0]+","+review_all[8][0]+","+review_all[9][0]+","+review_all[10][0]+","+review_all[11][0]+","+review_all[12][0]+","+review_all[13][0]+","+review_all[14][0]+","+review_all[15][0]+","+review_all[16][0]+","+review_all[17][0]+","+review_all[18][0]+","+review_all[19][0]+"'>")
print("<div style='text-align:center;'>")
print("<br/><input type='button' value='リセット' onclick='this.form.reset();' class='button1'/>&nbsp&nbsp")
print("<input type='submit' value='送信' class='button1'/>")
print("<div>")

print("</form>")
print("</div></div>")
print("</body></html>")

c.close
connect.close
