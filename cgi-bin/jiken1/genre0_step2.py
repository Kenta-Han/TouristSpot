#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='/data/stylesheet_onlytype.css' rel='stylesheet' type='text/css' />
<title>ジャンル選択2</title>

<script>
$(function() {
    inputCheck();
    $(':radio').change(function(){
        inputCheck();
    });
});

function inputCheck() {
    if($('#input-check').is(':checked')) {
        $('.button1').prop('disabled', false);
    } else {
        $('.button1').prop('disabled', true);
    }
}
</script>
</head>
<body>

"""

category = ["アウトドア","ウォータースポーツ・マリンスポーツ","雪・スノースポーツ","その他スポーツ・フィットネス","エンタメ・アミューズメント","レジャー・体験","クラフト・工芸","果物・野菜狩り","ミュージアム・ギャラリー","神社・神宮・寺院","伝統文化・日本文化","自然景観・絶景","乗り物","動・植物","風呂・スパ・サロン","ショッピング","観光施設・名所巡り","祭り・イベント"]

form = cgi.FieldStorage()
category_id = int(form.getvalue('genre')) ## only_type1_0.pyのgenreを受け取る

print(html_body)

print("<form action='genre0_step3.py' method='post' onsubmit='check(this);return false;'>")
print("<input type='hidden' name='category' value='" + category[category_id-1] + "'>")

print("<br/><h2 style='text-align:center;'>==== タイプを選んでください ====</h2>")

print("<table class='imagetable'>")
print("<tr><td colspan=1><input type='radio' name='type_id' value='1'>一人</td>")
print("<td colspan=2><input type='radio' name='type_id' value='2'>カップル・夫婦</td></tr>")
print("<tr><td colspan=1><input type='radio' name='type_id' value='3'>家族</td>")
print("<td colspan=1><input type='radio' name='type_id' value='4'>友達同士</td>")
print("<td colspan=1><input type='radio' name='type_id' value='5'>その他</td></tr>")
print("</table>")

print("<h3 style='text-align:center;'>CrowdWorks ID：<input type='text' name='user_id' id='user_id' maxlength='40' style='width: 200px;height: 24px;font-size:16px;'/></h3><p>(匿名は判別できません)</p>")

print("<p style='text-align:center;'>要求を3つ入力してください．<br><span style='font-size:12px;'>例：広い,のんびり,自然豊か...</span></p>")

print("<h4 style='text-align:center;'>要求1：<input type='text' name='keyword1' style='width: 250px;height: 24px;font-size:16px;'></h4>")
print("<h4 style='text-align:center;'>要求2：<input type='text' name='keyword2' style='width: 250px;height: 24px;font-size:16px;'></h4>")
print("<h4 style='text-align:center;'>要求3：<input type='text' name='keyword3' style='width: 250px;height: 24px;font-size:16px;'></h4>")

print("<p style='text-align:center;color:#ff0000'><input type='radio' name='user' id='input-check' />項目の入力し終えたら，チェックしてください．</p>")

print("<input type='submit' class='button1' value='送信'/>")
print("</form>")

print("</body></html>")
