#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb

# DBに接続しカーソルを取得する
connect = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan', charset='utf8')
c = connect.cursor()

html_body = u"""
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<link href='../../data/stylesheet.css' rel='stylesheet' type='text/css' />
<title>タイプ選択</title>
</head>
<body>
<div class='box1'>
<header>
<h1>観光スポット推薦</h1>
</header>
<form action='select_review1.py' method='post' onsubmit='check(this);return false;'>

<h3>==== タイプを選択してください ====</h3>
<div class='review'>
<ol>
<li><input type='radio' name='type1' value='1'>&nbsp一人</li>
<li><input type='radio' name='type1' value='2'>&nbspカップル・夫婦</li>
<li><input type='radio' name='type1' value='3'>&nbsp家族</li>
<li><input type='radio' name='type1' value='4'>&nbsp友達同士</li>
<li><input type='radio' name='type1' value='5'>&nbspその他</li>
<input type='submit' value='送信' class='submit1'/>
</ol>
</form>
<script>
function check(elem){
var radios = elem.type1;
var radiosFlag = new Boolean(false);
for(var i=0; i<radios.length; i++){
if(radios[i].checked == true){radiosFlag = true;}
}
if(radiosFlag == false){
alert('タイプを選択しくてください');
return false;
}
FormType1.submit();
}
</script>
</div>
</div>
</body>
</html>
"""

print(html_body)


c.close
connect.close
