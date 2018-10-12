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
print("<link href='../../data/stylesheet.css' rel='stylesheet' type='text/css' />")
print("<title>観光スポット</title>")
print("</head>")
print("<body>")
print("<div class='box1'>")
print("<header>")
print("<h1>観光スポット検索(A)</h1>")
print("</header>")

print("<h2 style='text-align:center;'>レビューによる観光スポット検索の実験のご協力ありがとうございます．</h2>")
print("<p style='text-align:center;'>「ジャンルによる観光スポット検索へ」をクリックして次の実験をお願いします．</p>")

print("<form action='genre1_step1.py' method='post'>")
print("<div style='text-align:center;'>")
print("<input type='submit' value='ジャンルによる観光スポット検索へ' class='button1'/>")
print("</div></form>")

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

cur.execute("update exp_data_proposal_test set selected_spot1='" + str(check1) + "', selected_spot2='" + str(check2) + "', selected_spot3='" + str(check3) + "', msg ='" + str(msg) + "',count = '" + str(count) +  "', access_order=1 where id=" + str(user_max_id) + ";")

print("</body></html>")

conn.commit()

cur.close
conn.close
