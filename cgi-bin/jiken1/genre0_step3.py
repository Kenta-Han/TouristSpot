#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import datetime

connect = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan', charset='utf8')
c = connect.cursor()

form = cgi.FieldStorage()
category = form.getvalue('category')
type_id = int(form.getvalue('type_id'))
user_id = form.getvalue('user_id')
keyword = [form.getvalue('keyword1'),form.getvalue('keyword2'),form.getvalue('keyword3')]

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
elif now.month == 12 or (now.month >= 1 and now.month <= 2) :
    season = "winter"
## ====== 季節〆 ======
type_all = ["一人","カップル・夫婦","家族","友達同士","その他"]

print("<header><h1 style='text-align:center;'>観光スポット検索(B)</h1></header>")

print("<table class='imagetable'>")
print("<tr><th>ジャンル：</th><td>" + category + "</tr></td>")
print("<tr><th>タイプ：</th><td>" + type_all[type_id-1] + "</tr></td>")
print("<tr><th>季節：</th><td>" + season + "</tr></td>")
print("</table>")

sql_insert = "insert into exp_data_category_test(category, type, season, user_id,keyword01,keyword02,keyword03) values(%s,%s,%s,%s,%s,%s,%s);"
c.execute(sql_insert, (category,type_all[type_id-1],season,user_id,keyword[0],keyword[1],keyword[2]))
connect.commit()

c.execute("select max(id) from exp_data_category_test where user_id='" + str(user_id) + "';")
user_max_id = c.fetchone()[0]

sql_select = "select distinct name,spot_id,review from unity_kantou_add_category where category1 = '" + category + "' and season4 = '" + season + "'and companion = '" + type_all[type_id-1] + "' order by review desc limit 10;"
c.execute(sql_select)

print("<form action='genre0_step4.py' method='post'>")

print("<table class='imagetable'>")
print("<p>以下の観光スポットを押すとじゃらんの紹介ページが開きます．</br>内容を確認した上でいくつか選択してください．</br></br> 「キーワード」:キーワードに満たしているならチェックしてください．</br>「既知」:既知の観光スポットならチェックしてください </p>")
print("<p>キーワード1：" + str(keyword[0]) + "</br>キーワード2：" + str(keyword[1]) + "</br>キーワード3：" + str(keyword[2]) + "</p>")

column_list = ["spot01","spot02","spot03","spot04","spot05","spot06","spot07","spot08","spot09","spot10"]


print("<tr><th>観光スポット</th><th>キーワード1</th><th>キーワード2</th><th>キーワード3</th><th>既知</th></tr>")
for spot,column in zip(c,column_list):
    print("<tr><th><a href='http://www.jalan.net/kankou/" + str(spot[1]) + "/'  target='_blank'>")
    print(spot[0] + "</a></th>")
    # print("<td style='text-align:center;'>" + str(spot[2]) + "</td>")
    print("<td style='text-align:center;'><input type='checkbox' name='check_1' value='" + spot[0] + "'></td>")
    print("<td style='text-align:center;'><input type='checkbox' name='check_2' value='" + spot[0] + "'></td>")
    print("<td style='text-align:center;'><input type='checkbox' name='check_3' value='" + spot[0] + "'></td>")
    print("<td style='text-align:center;'><input type='checkbox' name='count' value='" + spot[0] + "'></td></tr>")

    c.execute("update exp_data_category_test set " + column + "='" + spot[0] + "' where id=" + str(user_max_id) + ";")
    connect.commit()
print("</table>")

print("<h3>意見<span style='font-size: 14px;'>(※ご自由にどうぞ)：</span></h3>")
print("<textarea name='msg' cols=70 rows=7 />")
print("</textarea>")
print("<p>「結果送信」を押した後次のページ表示するまでお待ちしてください</p>")
print("<input type='hidden' name='user_max_id' value='" + str(user_max_id) + "'>")
print("</br><input type='submit' value='結果送信' class='button1'/>")
print("</form>")

print("</body></html>")

c.close
connect.close
