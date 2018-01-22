#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import datetime
import sys
import mypackage.other_def as myp_other

connect = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan', charset='utf8')
c = connect.cursor()

form = cgi.FieldStorage()
record_id = form.getvalue('record_id')
type_id = int(form.getvalue('type_id')) ##タイプ
keyword = [form.getvalue('keyword1'),form.getvalue('keyword2'),form.getvalue('keyword3')] ##要求3つ

genre_check1 = form.getvalue('genre_check1')
genre_check2 = form.getvalue('genre_check2')
genre_check3 = form.getvalue('genre_check3')
genre_count = form.getvalue('genre_count')
genre_msg = form.getvalue('genre_msg')

list_by_check = myp_other.Check(genre_check1,genre_check2,genre_check3,genre_count)

c.execute("update jiken2 set genre_selected_spot1='" + str(list_by_check[0]) + "', genre_selected_spot2='" + str(list_by_check[1]) + "', genre_selected_spot3='" + str(list_by_check[2]) + "', genre_msg ='" + str(genre_msg) + "',genre_count = '" + str(list_by_check[3]) + "',genre_count_list = '" + str(list_by_check[4]) + "' where id=" + str(record_id) + ";")
connect.commit()

### レビュー ###
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
c.execute("select cast(num as char),review_text from unity_kantou where companion='" + type_word[2] +"' and season4='"+ season_word[2] +"' order by rand() limit 20")

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
<link href='../data/new_stylesheet.css' rel='stylesheet' type='text/css' />
<title>レビュー選択</title>
</head>

<script>
function send(){
    var user_id='';
    var keyword1='';
    var keyword2='';
    var keyword3='';
    var type1='';

    /* CrowdWorksID */
    if (document.form1.user_id.value!=''){
        user_id = escape(document.form1.user_id.value);
    }

    /* 要求 */
    if (document.form1.keyword1.value!=''){
        keyword1 = escape(document.form1.keyword1.value);
    }
    if (document.form1.keyword2.value!=''){
        keyword2 = escape(document.form1.keyword2.value);
    }
    if (document.form1.keyword3.value!=''){
        keyword3 = escape(document.form1.keyword3.value);
    }

    /* タイプ */
    if(document.form1.type_id[0].checked){
        type1 = escape(document.form1.type_id[0].value);
    }else if(document.form1.type_id[1].checked){
        type1 = escape(document.form1.type_id[1].value);
    }else if(document.form1.type_id[2].checked){
        type1 = escape(document.form1.type_id[2].value);
    }else if(document.form1.type_id[3].checked){
        type1 = escape(document.form1.type_id[3].value);
    }else if(document.form1.type_id[4].checked){
        type1 = escape(document.form1.type_id[4].value);
    }

    /* 季節 */
    var sql_season0='';
    var sql_season1='';
    var season_word0='';
    var season_word1='';
    var season_word2=‘';

    /* 季節のSQL文 */
    if (document.form1.sql_season0.value!=''){
        sql_season0 = escape(document.form1.sql_season0.value);
    }
    if (document.form1.sql_season1.value!=''){
        sql_season1 = escape(document.form1.sql_season1.value);
    }

    /* 季節のワード */
    if (document.form1.season_word0.value!=''){
        season_word0 = escape(document.form1.season_word0.value);
    }
    if (document.form1.season_word1.value!=''){
        season_word1 = escape(document.form1.season_word1.value);
    }
    if (document.form1.season_word2.value!=''){
        season_word2 = escape(document.form1.season_word2.value);
    }

    /* タイプ */
    var sql_type0='';
    var sql_type1='';
    var type_word0='';
    var type_word1='';
    var type_word2=‘’;

    /* タイプのSQL文 */
    if (document.form1.sql_type0.value!=''){
        sql_type0 = escape(document.form1.sql_type0.value);
    }
    if (document.form1.sql_type1.value!=''){
        sql_type1 = escape(document.form1.sql_type1.value);
    }

    /* タイプのワード */
    if (document.form1.type_word0.value!=''){
        type_word0 = escape(document.form1.type_word0.value);
    }
    if (document.form1.type_word1.value!=''){
        type_word1 = escape(document.form1.type_word1.value);
    }
    if (document.form1.type_word2.value!=''){
        type_word2 = escape(document.form1.type_word2.value);
    }

    /* レビュー */
    var review_num=‘';
    if (document.form1.review_num.value!=''){
        review_num = escape(document.form1.type_word0.value);
    }

    /* 取得した値をパラメータにセット(アンパサンド'&'で連結) */
    var pram = 'user_id=' + user_id + '&keyword1=' + keyword1 + '&keyword2=' + keyword2 + '&keyword3=' + keyword3 + '&type1=' + type1;

    /* アドレスにパラメータを付加 */
    location.href="/cgi-bin/jiken2_genre0_step1.py?"+pram;
    return false;
}

$(function() {
    var h = $(window).height();
    $('#wrap').css('display','none');
    $('#loader-bg ,#loader').height(h).css('display','block');
});

$(window).load(function () { //全ての読み込みが完了したら実行
    var min = 10000 ; //10秒
    var max = 20000 ; //20秒
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

<body>
<div id='wrap'>
<header><h1 class='title'>観光スポット検索(A)</h1></header>
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

print("<h2 style='text-align:center;'>==== レビューを３つを選択してください ====</h2>")
print("<p style='text-align:center;'>入力した要求に対する一番近いレビューを3つ選択してください．</p>")
pulldown = """
<table class='choice_table'>
<tr>
<td>レビュー1：<select name='input1' form='example' style='width: 44px;height: 24px;font-size:14px;'>
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
</td><td>レビュー2：<select name='input2' form='example' style='width: 44px;height: 24px;font-size:14px;'>
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
</td><td>レビュー3：<select name='input3' form='example' style='width: 44px;height: 24px;font-size:14px;'>
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

print("<form action='#' method='post' id='example' name='form1' onsubmit='return send();'>")
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

print("<input type='hidden' name='review_num' value='"+review_all[0][0]+","+review_all[1][0]+","+review_all[2][0]+","+review_all[3][0]+","+review_all[4][0]+","+review_all[5][0]+","+review_all[6][0]+","+review_all[7][0]+","+review_all[8][0]+","+review_all[9][0]+","+review_all[10][0]+","+review_all[11][0]+","+review_all[12][0]+","+review_all[13][0]+","+review_all[14][0]+","+review_all[15][0]+","+review_all[16][0]+","+review_all[17][0]+","+review_all[18][0]+","+review_all[19][0]+"'>")

print("<div style='text-align:center;'>")
print("<input type='hidden' name='type_id' value='" + str(type_id) + "'>")
print("<input type='hidden' name='keyword1' value='" + str(keyword[0]) + "'>")
print("<input type='hidden' name='keyword2' value='" + str(keyword[1]) + "'>")
print("<input type='hidden' name='keyword3' value='" + str(keyword[2]) + "'>")
print("<input type='hidden' name='record_id' value='" + str(record_id) + "'>")
print("<p>※ 次のページが開くまでしばらく時間(約30秒~2分)がかかります．</p>")
print("<input type='submit' class='button1' value='次へ'/>")
print("<div>")
print("</form>")
print("</div></div></br>")
print("</body></html>")

c.close
connect.close
