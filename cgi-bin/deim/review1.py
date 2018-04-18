#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import datetime
import sys
import other_def as myp_other

# DBに接続しカーソルを取得する
connect = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan', charset='utf8')
c = connect.cursor()

form = cgi.FieldStorage()
type_id = int(form.getvalue('type1')) ##タイプ

start_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
## ====== 季節 ======
now = datetime.datetime.today() ## 現在の日付を取得
if now.month >= 3 and now.month <= 5 :
    sql_season = ["select * from tfidf_season_spring","select * from kld_season_spring3"]
    season_word = ["tfidf_spring","kld_spring","spring"]
elif now.month >= 6 and now.month <= 8 :
    sql_season= ["select * from tfidf_season_summer","select * from kld_season_summer3"]
    season_word = ["tfidf_summer","kld_summer","summer"]
elif now.month >= 9 and now.month <= 11 :
    sql_season = ["select * from tfidf_season_autumn","select * from kld_season_autumn3"]
    season_word = ["tfidf_autumn","kld_autumn","autumn"]
elif now.month == 12 or (now.month >= 1 and now.month <= 2) :
    sql_season = ["select * from tfidf_season_winter","select * from kld_season_winter3"]
    season_word = ["tfidf_winter","kld_winter","winter"]
## ====== 季節〆 ======
type_all = ["一人","カップル・夫婦","家族","友達同士","その他"]
## ====== タイプ ======
if type_id  == 1 :
    type_word = ["tfidf_alone","kld_alone","一人"]
    sql_type = ["select * from tfidf_type_alone","select * from kld_type_alone3"]
elif type_id == 2 :
    type_word = ["tfidf_couple","kld_couple","カップル・夫婦"]
    sql_type = ["select * from tfidf_type_couple","select * from kld_type_couple3"]
elif type_id == 3 :
    type_word = ["tfidf_family","kld_family","家族"]
    sql_type = ["select * from tfidf_type_family","select * from kld_type_family3"]
elif type_id == 4 :
    type_word = ["tfidf_friend","kld_friend","友達同士"]
    sql_type = ["select * from tfidf_type_friend","select * from kld_type_friend3"]
elif type_id == 5 :
    type_word = ["tfidf_other","kld_other","その他"]
    sql_type = ["select * from tfidf_type_other","select * from kld_type_other3"]
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
c.execute("select cast(num as char),review_text from unity_kantou where companion='" + type_word[2] +"' and season4='"+ season_word[2] +"' order by rand() limit 5")

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

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='/data/stylesheet_deim.css' rel='stylesheet' type='text/css' />
<title>レビュー選択</title>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
<script>
$(function () {
    $('.button1').click(function() {
        /* 画面を隠す */
        var h = $(window).height();
        $('#wrap').css('display','none');
        $('#loader-bg ,#loader').height(h).css('display','block');

        /* 画面n秒後を表示 */
        var min = 10000 ; //10秒
        var max = 30000 ; //30秒
        var a = Math.floor( Math.random() * (max + 1 - min) ) + min ;
        $('#loader-bg').delay(a).fadeOut(1000);
        //$('#loader').delay(30000).fadeOut(1000);
        $('#wrap').css('display', 'block');
    });
});
</script>
</head>

<body>
<div id="loader-bg">
  <div id="loader">
    <h2>Now Loading...</h2>
  </div>
</div>
<div id='wrap'>
<header><h1 class='title'>観光スポット検索</h1></header>
"""
print(html_body)

for i in range(len(review_all)):
    print("<p>")
    print("<strong>ID：")
    print(str(cnt))
    print("</strong><br/><strong>Review：</strong>")
    print(str(review_all[i][1]))
    print("</p>")
    cnt += 1

print("<h2 style='text-align:center;'>==== レビューを1つを選択してください ====</h2>")
pulldown = """
<table class='choice_table'>
<tr>
<td>レビュー：<select name='input1' form='example' style='width: 44px;height: 24px;font-size:14px;'>
<option value='1'>1</option>
<option value='2'>2</option>
<option value='3'>3</option>
<option value='4'>4</option>
<option value='5'>5</option>
</select>
</td></tr></table>
"""

print("<div class='review'>")
print(pulldown)

print("<form method='post' action='review2.py' id='example'>")
print("<input type='hidden' name='sql_season0' value='" + sql_season[0] + "'>")
print("<input type='hidden' name='sql_season1' value='" + sql_season[1] + "'>")
print("<input type='hidden' name='season_word0' value='" + season_word[0] + "'>")
print("<input type='hidden' name='season_word1' value='" + season_word[1] + "'>")
print("<input type='hidden' name='season_word2' value='" + season_word[2] + "'>")
print("<input type='hidden' name='sql_type0' value='" + sql_type[0] + "'>")
print("<input type='hidden' name='sql_type1' value='" + sql_type[1] + "'>")
print("<input type='hidden' name='type_word0' value='" + type_word[0] + "'>")
print("<input type='hidden' name='type_word1' value='" + type_word[1] + "'>")
print("<input type='hidden' name='type_word2' value='" + type_word[2] + "'>")

print("<input type='hidden' name='review_num[]' value='"+review_all[0][0]+","+review_all[1][0]+","+review_all[2][0]+","+review_all[3][0]+","+review_all[4][0]+"'>")

print("<div style='text-align:center;'>")
print("<input type='hidden' name='type_id' value='" + str(type_id) + "'>")
print("<input type='submit' class='button1' value='次へ'/>")
print("<div>")
print("</form>")
print("</div></div></br>")
print("</body></html>")

c.close
connect.close
