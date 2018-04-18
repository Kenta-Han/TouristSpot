#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import datetime
import mypackage.other_def as myp_other

connect = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan', charset='utf8')
c = connect.cursor()

form = cgi.FieldStorage()
record_id = form.getvalue('record_id')
review_check1 = form.getvalue('review_check1')
review_check2 = form.getvalue('review_check2')
review_check3 = form.getvalue('review_check3')
review_count = form.getvalue('review_count')
review_msg = form.getvalue('review_msg')

finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

list_by_check = myp_other.Check(review_check1,review_check2,review_check3,review_count)

c.execute("update soc2018 set review_selected_spot1='" + str(list_by_check[0]) + "', review_selected_spot2='" + str(list_by_check[1]) + "', review_selected_spot3='" + str(list_by_check[2]) + "', review_msg ='" + str(review_msg) + "',review_count = '" + str(list_by_check[3]) + "',review_count_list = '" + str(list_by_check[4]) + "',finish_datetime = '" + finish_datetime + "' where id=" + str(record_id) + ";")
connect.commit()

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='/data/new_stylesheet.css' rel='stylesheet' type='text/css' />
<title>観光スポット(RS)</title>
</head>
<body>
<header><h1 class='title' style='margin:250px auto;'>実験のご協力を頂きありがとうございました．</h1></header>
</body></html>
"""
print(html_body)

c.close
connect.close
