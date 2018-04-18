#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import sys

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='/data/stylesheet_deim.css' rel='stylesheet' type='text/css' />
<title>観光スポット検索</title>
</head>
<body>
<header>
<h1 class='title'>観光スポット検索</h1>
</header>
<form method='post' action='review1.py'>
<br><br>
<h2 class='subtitle'>== タイプを選択してください ==</h2>
<ol class='type_choice'>
<li class='type_choice_li'><input type='radio' name='type1' value='1'>&nbsp一人</li>
<li class='type_choice_li'><input type='radio' name='type1' value='2'>&nbspカップル・夫婦</li>
<li class='type_choice_li'><input type='radio' name='type1' value='3'>&nbsp家族</li>
<li class='type_choice_li'><input type='radio' name='type1' value='4'>&nbsp友達同士</li>
<li class='type_choice_li'><input type='radio' name='type1' value='5'>&nbspその他</li>
</ol>
<input type='submit' class='button1' value='次へ'/>
</form>
</body>
</html>
"""
print(html_body)
