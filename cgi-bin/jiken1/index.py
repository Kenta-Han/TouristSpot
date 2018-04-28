#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='../../data/stylesheet.css' rel='stylesheet' type='text/css' />
<title>評価実験</title>
</head>

<script>
function open_win(url) {
  window.open(url,'status=yes,scrollbars=yes,directories=yes,width=400,height=400');
}
function RandomLink() {
  var a;
  a = 1 + Math.round(Math.random()*2);
  if (a==1) open_win('review1_step1.py');
  if (a==2) open_win('genre0_step1.py');
}
</script>

<body>

<div class='box1'style='text-align:center;'>
<form>
<header><h1 style='text-align:center;'>観光スポット検索</h1></header><br>
<input type='button' class='button1' value='実験開始' onClick='RandomLink()'/>
</form>
<br>
</div>

</body>
</html>

"""

print(html_body)
