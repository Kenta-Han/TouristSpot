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
record_id = form.getvalue('record_id')
type_id = int(form.getvalue('type_id')) ##タイプ
keyword = [form.getvalue('keyword1'),form.getvalue('keyword2'),form.getvalue('keyword3')] ##要求3つ

review_check1 = form.getvalue('review_check1')
review_check2 = form.getvalue('review_check2')
review_check3 = form.getvalue('review_check3')
review_count = form.getvalue('review_count')
review_msg = form.getvalue('review_msg')

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

<form action='jiken2_genre1_step2.py' method='post'>
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

list_by_check = myp_other.Check(review_check1,review_check2,review_check3,review_count)

c.execute("update jiken2 set review_selected_spot1='" + str(list_by_check[0]) + "', review_selected_spot2='" + str(list_by_check[1]) + "', review_selected_spot3='" + str(list_by_check[2]) + "', review_msg ='" + str(review_msg) + "',review_count = '" + str(list_by_check[3]) +  "',review_count_list ='" + str(list_by_check[4]) + "' where id=" + str(record_id) + ";")
connect.commit()

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
