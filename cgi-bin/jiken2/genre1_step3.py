#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import datetime

import os, sys # 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan
conn,cur = jalan.main()
import mypackage.other_def as myp_other

form = cgi.FieldStorage()
record_id = form.getvalue('record_id')
genre_check1 = form.getvalue('genre_check1')
genre_check2 = form.getvalue('genre_check2')
genre_check3 = form.getvalue('genre_check3')
genre_count = form.getvalue('genre_count')
genre_msg = form.getvalue('genre_msg')

finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

list_by_check = myp_other.Check(genre_check1,genre_check2,genre_check3,genre_count)

cur.execute("update jiken2 set genre_selected_spot1='" + str(list_by_check[0]) + "', genre_selected_spot2='" + str(list_by_check[1]) + "', genre_selected_spot3='" + str(list_by_check[2]) + "', genre_msg ='" + str(genre_msg) + "',genre_count = '" + str(list_by_check[3]) + "',genre_count_list = '" + str(list_by_check[4]) + "',finish_datetime = '" + finish_datetime + "' where id=" + str(record_id) + ";")
conn.commit()

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='../../data/stylesheet_jiken2.css' rel='stylesheet' type='text/css' />
<title>観光スポット</title>
</head>
<body>
<header><h1 class='title' style='margin:250px auto;'>実験のご協力を頂きありがとうございました．</h1></header>
</body>
</html>
"""
print(html_body)

cur.close
conn.close
