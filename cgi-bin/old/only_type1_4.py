#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import datetime

connect = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan', charset='utf8')
c = connect.cursor()

print("<!DOCTYPE html>")
print("<head>")
print("Content-type:text/html; charset=UTF-8\r\n")
print("<meta http-equiv='content-type' content='text/html; />")
print("<script src='https://code.jquery.com/jquery-3.0.0.min.js'></script>")
print("<link href='/data/stylesheet_onlytype.css' rel='stylesheet' type='text/css' />")
print("<title>観光スポット</title>")
print("</head>")

print("<body>")

## ====== 季節 ======
now = datetime.datetime.today() ## 現在の日付を取得
if now.month >= 3 and now.month <= 5 :
    season = "spring"
elif now.month >= 6 and now.month <= 8 :
    season = "summer"
elif now.month >= 9 and now.month <= 11 :
    season = "autumn"
elif now.month == 12 or (now.month > 1 and now.month <= 2) :
    season = "winter"
## ====== 季節〆 ======
type_all = ["一人","カップル・夫婦","家族","友達同士","その他"]

print("<header><h1 style='text-align:center;'>観光スポット検索</h1></header>")

form = cgi.FieldStorage()
category_alone = form.getvalue('genre2')
type1 = int(form.getvalue('type1'))

print("<table class='imagetable'>")
print("<tr><th>ジャンル：</th><td>"+category_alone+"</tr></td>")
print("<tr><th>タイプ：</th><td>"+type_all[type1-1]+"</tr></td>")
print("<tr><th>季節：</th><td>"+season+"</tr></td>")
print("</table>")

sql_select = "select distinct name,spot_id,review from unity_kantou_add_category where category2 = '" + category_alone + "' and season4 = '" + season + "'and companion = '" + type_all[type1-1] + "' order by review desc limit 10;"
c.execute(sql_select)

print("<table class='imagetable'>")
for spot in c:
    print("<tr><th><a href='http://www.jalan.net/kankou/")
    print(str(spot[1]))
    print("/'>")
    print(spot[0])
    print("</a></th><td>レビュー数："+str(spot[2])+"</td></tr>")
print("</table>")

print("<form action='only_type1_1.py' method='post'>")
print("<input type='submit' value='ジャンル選択へ' class='button1'/>")
print("</form>")

print("</body></html>")

c.close
connect.close
