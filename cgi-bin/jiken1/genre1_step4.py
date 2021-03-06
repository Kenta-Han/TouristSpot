#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb

import os, sys # 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan
conn,cur = jalan.main()


form = cgi.FieldStorage()
user_max_id = form.getvalue('user_max_id')
check1_list = form.getvalue('check_1')
check2_list = form.getvalue('check_2')
check3_list = form.getvalue('check_3')
count_list = form.getvalue('count')
msg = form.getvalue('msg')

print("<!DOCTYPE html>")
print("<head>")
print("Content-type:text/html; charset=UTF-8\r\n")
print("<meta http-equiv='content-type' content='text/html; />")
print("<script src='https://code.jquery.com/jquery-3.0.0.min.js'></script>")
print("<link href='../../data/stylesheet_onlytype.css' rel='stylesheet' type='text/css' />")
print("<title>観光スポット</title>")
print("</head>")

print("<body>")
print("<header><h1 style='text-align:center;'>観光スポット検索(B)</h1></header>")

print("<h2 style='text-align:center;'>実験のご協力ありがとうございます</h2>")

if check1_list == None:
    check1 = 0
elif type(check1_list)==str:
    check1 = ','.join([check1_list])
else:
    check1 = ','.join(check1_list)

if check2_list == None:
    check2 = 0
elif type(check2_list)==str:
    check2 = ','.join([check2_list])
else:
    check2 = ','.join(check2_list)

if check3_list == None:
    check3 = 0
elif type(check3_list)==str:
    check3 = ','.join([check3_list])
else:
    check3 = ','.join(check3_list)

if count_list == None:
    count = 0
elif type(count_list)==str:
    count = len([count_list])
else:
    count = len(count_list)

cur.execute("update exp_data_category_test set selected_spot1='" + str(check1) + "', selected_spot2='" + str(check2) + "', selected_spot3='" + str(check3) + "', msg ='" + str(msg) + "',count = '" + str(count) +  "', access_order=1  where id=" + str(user_max_id) + ";")

print("</body></html>")

conn.commit()

cur.close
conn.close
