#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import datetime
import json

import MySQLdb
import os, sys ## 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

cgitb.enable()
form = cgi.FieldStorage()
record_id = form.getfirst('record_id')
print(record_id)
hyouka = form.getlist('hyouka[]')
hyouka_text = form.getlist('hyouka_text[]')
print('Content-type: text/html\nAccess-Control-Allow-Origin: *\n')

finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

sql_update = "UPDATE analogy_deim2019 SET hyouka='{h}', hyouka_text='{ht}', finish_datetime='{finish}' WHERE id = {record_id};".format(h='，'.join(hyouka), ht='，'.join(hyouka_text), finish=finish_datetime, record_id=record_id)
print(json.dumps({"sql":sql_update}))

cur.execute(sql_update)
conn.commit()
