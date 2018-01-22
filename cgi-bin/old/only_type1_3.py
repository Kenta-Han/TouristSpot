#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb

print("<!DOCTYPE html>")
print("<head>")
print("Content-type:text/html; charset=UTF-8\r\n")
print("<meta http-equiv='content-type' content='text/html; />")
print("<script src='https://code.jquery.com/jquery-3.0.0.min.js'></script>")
print("<link href='/data/stylesheet_onlytype.css' rel='stylesheet' type='text/css' />")
print("<title>タイプ選択</title>")
print("</head>")

print("<body>")
print("<header><h1 style='text-align:center;'>観光スポット検索</h1></header>")

category = ["アウトドア","ウォータースポーツ・マリンスポーツ","雪・スノースポーツ","その他スポーツ・フィットネス","エンタメ・アミューズメント","レジャー・体験","クラフト・工芸","果物・野菜狩り","ミュージアム・ギャラリー","神社・神宮・寺院","伝統文化・日本文化","自然景観・絶景","乗り物","動・植物","風呂・スパ・サロン","ショッピング","観光施設・名所巡り","祭り・イベント"]

form = cgi.FieldStorage()
category_id = int(form.getvalue('genre1')) ## only_type02.pyのgenre1を受け取る
category_alone = form.getvalue('genre2') ## only_type02.pyのgenre2を受け取る

print("<br/><h2 style='text-align:center;'>==== ジャンル確認 ====</h2>")
print("<table class='imagetable'>")
print("<tr><th>ジャンル1：</th><td>"+category[category_id-1]+"</tr></td>")
print("<tr><th>ジャンル2：</th><td>"+category_alone+"</tr></td>")
print("</table>")
print("<form action='only_type1_1.py' method='post'>")
print("<input type='submit' value='ジャンル選択へ' class='button1'/>")
print("</form>")

print("<form action='only_type1_4.py' method='post' onsubmit='check(this);return false;'>")
print("<input type='hidden' name='genre2' value='"+category_alone+"'>")

print("<br/><h2 style='text-align:center;'>==== タイプを選んでください ====</h2>")
print("<table class='imagetable'>")
print("<tr><td colspan=1><input type='radio' name='type1' value='1'>一人</td>")
print("<td colspan=2><input type='radio' name='type1' value='2'>カップル・夫婦</td></tr>")
print("<tr><td colspan=1><input type='radio' name='type1' value='3'>家族</td>")
print("<td colspan=1><input type='radio' name='type1' value='4'>友達同士</td>")
print("<td colspan=1><input type='radio' name='type1' value='5'>その他</td></tr>")
print("</table>")
print("<input type='submit' class='button1' value='送信' />")
print("</form>")

print("</body></html>")
