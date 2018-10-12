#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import datetime
import random
from time import sleep

import os, sys # 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan
conn,cur = jalan.main()

# sleep_time = random.randint(30,120)
# sleep(sleep_time)

form = cgi.FieldStorage()
record_id = form.getvalue('record_id')
type_id = int(form.getvalue('type_id')) ##タイプ
keyword = [form.getvalue('keyword1'),form.getvalue('keyword2'),form.getvalue('keyword3')] ##要求3つ
category_id = int(form.getvalue('genre')) ## only_type1_0.pyのgenreを受け取る

category = ["アウトドア","ウォータースポーツ・マリンスポーツ","雪・スノースポーツ","その他スポーツ・フィットネス","エンタメ・アミューズメント","レジャー・体験","クラフト・工芸","果物・野菜狩り","ミュージアム・ギャラリー","神社・神宮・寺院","伝統文化・日本文化","自然景観・絶景","乗り物","動・植物","風呂・スパ・サロン","ショッピング","観光施設・名所巡り","祭り・イベント"]

sql_update = "update jiken2 set genre ='" + category[category_id-1] + "'where id = " + record_id + ";"
cur.execute(sql_update)
conn.commit()

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

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<link href="../../data/new_stylesheet.css' rel='stylesheet' type='text/css' />
<title>観光スポット</title>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
<script>
$(function() {
    var h = $(window).height();
    $('#wrap').css('display','none');
    $('#loader-bg ,#loader').height(h).css('display','block');
});

$(window).load(function () { //全ての読み込みが完了したら実行
    var min = 30000 ; //30秒
    var max = 90000 ; //1分30秒
    var a = Math.floor( Math.random() * (max + 1 - min) ) + min ;
    $('#loader-bg').delay(a).fadeOut(1000);
    //$('#loader').delay(30000).fadeOut(1000);
    $('#wrap').css('display', 'block');
});

//300秒たったら強制的にロード画面を非表示
$(function(){
    setTimeout('stopload()',300000);
});

function stopload(){
    $('#wrap').css('display','block');
    $('#loader-bg').delay(900).fadeOut(800);
    $('#loader').delay(600).fadeOut(300);
}
</script>
</head>

<body>
<div id="loader-bg">
  <div id="loader">
    <h2>Now Loading...</br>次のページが開くまでしばらく時間</br>(約30秒~90秒)がかかります．<br>更新せずにお待ちして下さい．</h2>
  </div>
</div>
<div id="wrap">
<header><h1 class='title'>観光スポット検索(B)</h1></header>

"""
print(html_body)

print("<table class='info_table'>")
print("<tr><th>ジャンル：</th><td>" + category[category_id-1] + "</tr></td>")
print("<tr><th>タイプ：</th><td>" + type_all[type_id-1] + "</tr></td>")
print("<tr><th>季節：</th><td>" + season + "</tr></td>")
print("</table>")


sql_select = "select distinct name,spot_id,review from unity_kantou_add_category where category1 = '" + category[category_id-1] + "' and season4 = '" + season + "'and companion = '" + type_all[type_id-1] + "' order by review desc limit 10;"
cur.execute(sql_select)

print("<form action='genre1_step3.py' method='post'>")
print("<p>以下の観光スポットを押すとじゃらんの紹介ページが開きます．</br>内容を確認した上でいくつか選択してください．</br>「要求」:要求に満たしているならチェックしてください．</br>「既知」:既知の観光スポットならチェックしてください </p>")
print("<p>要求1：" + str(keyword[0]) + "，要求2：" + str(keyword[1]) + "，要求3：" + str(keyword[2]) + "</p>")

column_list = ["genre_spot01","genre_spot02","genre_spot03","genre_spot04","genre_spot05","genre_spot06","genre_spot07","genre_spot08","genre_spot09","genre_spot10"]

print("<table class='genre_table'>")
print("<tr><th>観光スポット</th><th>要求1</th><th>要求2</th><th>要求3</th><th>既知</th></tr>")
for spot,column in zip(cur,column_list):
    print("<tr><th><a href='http://www.jalan.net/kankou/" + str(spot[1]) + "/'  target='_blank'>")
    print(spot[0] + "</a></th>")
    # print("<td style='text-align:center;'>" + str(spot[2]) + "</td>")
    print("<td style='text-align:center;'><input type='checkbox' name='genre_check1' value='" + spot[0] + "'></td>")
    print("<td style='text-align:center;'><input type='checkbox' name='genre_check2' value='" + spot[0] + "'></td>")
    print("<td style='text-align:center;'><input type='checkbox' name='genre_check3' value='" + spot[0] + "'></td>")
    print("<td style='text-align:center;'><input type='checkbox' name='genre_count' value='" + spot[0] + "'></td></tr>")
    cur.execute("update jiken2 set " + column + "='" + spot[0] + "' where id=" + str(record_id) + ";")
    conn.commit()
print("</table>")

print("<h2>意見：</h2>")
print("<textarea name='genre_msg' cols=70 rows=7 /></textarea>")
print("<input type='hidden' name='type_id' value='" + str(type_id) + "'>")
print("<input type='hidden' name='keyword1' value='" + str(keyword[0]) + "'>")
print("<input type='hidden' name='keyword2' value='" + str(keyword[1]) + "'>")
print("<input type='hidden' name='keyword3' value='" + str(keyword[2]) + "'>")
print("<input type='hidden' name='record_id' value='" + str(record_id) + "'>")
print("</br><input type='submit' value='次へ' class='button1'/>")
print("</form>")

print("</div></br></body></html>")

cur.close
conn.close
