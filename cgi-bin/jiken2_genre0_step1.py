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

form = cgi.FieldStorage()
user_id = form.getvalue('user_id') ##CrowdWorksID
type_id = int(form.getvalue('type1')) ##タイプ
keyword = [form.getvalue('keyword1'),form.getvalue('keyword2'),form.getvalue('keyword3')] ##要求3つ

## ====== 季節 ======
now = datetime.datetime.today() ## 現在の日付を取得
if now.month >= 3 and now.month <= 5 :
    season = "spring"
elif now.month >= 6 and now.month <= 8 :
    season = "summer"
elif now.month >= 9 and now.month <= 11 :
    season = "autumn"
elif now.month == 12 or (now.month >= 1 and now.month <= 2) :
    season = "winter"
## ====== 季節〆 ======
type_all = ["一人","カップル・夫婦","家族","友達同士","その他"]

start_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

sql_insert = "insert into jiken2(user_id, type, season, keyword1, keyword2, keyword3, access_order, start_datetime) values(%s,%s,%s,%s,%s,%s,%s,%s);"
c.execute(sql_insert,(user_id,type_all[type_id-1],season,keyword[0],keyword[1],keyword[2],"0",start_datetime))
connect.commit()

c.execute("select max(id) from jiken2 where user_id='" + str(user_id) + "';")
record_id = c.fetchone()[0]

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv='content-type' content='text/html; charset=utf-8' />
<script src='https://code.jquery.com/jquery-3.0.0.min.js'></script>
<link href='../data/new_stylesheet.css' rel='stylesheet' type='text/css' />
<title>ジャンル選択</title>
</head>

<body>
<header><h1 class='title'>観光スポット検索(B)</h1></header>

<form action='jiken2_genre0_step2.py' method='post'>
<table class='genre_table'>
<tr>
<th colspan=4><h2>　ジャンルを選んでください　</h2></th>
</tr>
<tr>
<td><input type='radio' name='genre' value='1'>&nbspアウトドア</td>
<td><input type='radio' name='genre' value='2'>&nbspウォータースポーツ・マリンスポーツ</td>
<td><input type='radio' name='genre' value='3'>&nbsp雪・スノースポーツ</td>
</tr>
<tr>
<td><input type='radio' name='genre' value='4'>&nbspその他スポーツ・フィットネス</td>
<td><input type='radio' name='genre' value='5'>&nbspエンタメ・アミューズメント</td>
<td><input type='radio' name='genre' value='6'>&nbspレジャー・体験</td>
</tr>
<tr>
<td><input type='radio' name='genre' value='7'>&nbspクラフト・工芸</td>
<td><input type='radio' name='genre' value='8'>&nbsp果物・野菜狩り</td>
<td><input type='radio' name='genre' value='9'>&nbspミュージアム・ギャラリー</td>
</tr>
<tr>
<td><input type='radio' name='genre' value='10'>&nbsp神社・神宮・寺院</td>
<td><input type='radio' name='genre' value='11'>&nbsp伝統文化・日本文化</td>
<td><input type='radio' name='genre' value='12'>&nbsp自然景観・絶景</td>
</tr>
<tr>
<td><input type='radio' name='genre' value='13'>&nbsp乗り物</td>
<td><input type='radio' name='genre' value='14'>&nbsp動・植物</td>
<td><input type='radio' name='genre' value='15'>&nbsp風呂・スパ・サロン</td>
</tr>
<tr>
<td><input type='radio' name='genre' value='16'>&nbspショッピング</td>
<td><input type='radio' name='genre' value='17'>&nbsp観光施設・名所巡り</td>
<td><input type='radio' name='genre' value='18'>&nbsp祭り・イベント</td>
</tr>
</table>
"""

print(html_body)
print("<input type='hidden' name='type_id' value='" + str(type_id) + "'>")
print("<input type='hidden' name='keyword1' value='" + str(keyword[0]) + "'>")
print("<input type='hidden' name='keyword2' value='" + str(keyword[1]) + "'>")
print("<input type='hidden' name='keyword3' value='" + str(keyword[2]) + "'>")
print("<input type='hidden' name='record_id' value='" + str(record_id) + "'>")
print("<input type='submit' class='button1' value='次へ'/>")
print("</form>")
print("</body></html>")

c.close
connect.close
