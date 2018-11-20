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
hyouka_name_category = form.getlist('hyouka_name_category[]')
hyouka_word_category = form.getlist('hyouka_word_category[]')
hyouka_name_feature = form.getlist('hyouka_name_feature[]')
hyouka_word_feature = form.getlist('hyouka_word_feature[]')
hyouka_name_vector = form.getlist('hyouka_name_vector[]')
hyouka_word_vector = form.getlist('hyouka_word_vector[]')
print('Content-type: text/html\nAccess-Control-Allow-Origin: *\n')

finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

sql_update = "UPDATE map_test SET hyouka_name_c='{hyouka_name_c}', hyouka_word_c='{hyouka_word_c}', hyouka_name_f='{hyouka_name_f}', hyouka_word_f='{hyouka_word_f}', hyouka_name_v='{hyouka_name_v}', hyouka_word_v='{hyouka_word_v}', finish_datetime='{finish}' WHERE id = {record_id};".format(hyouka_name_c='，'.join(hyouka_name_category), hyouka_word_c='，'.join(hyouka_word_category), hyouka_name_f='，'.join(hyouka_name_feature), hyouka_word_f='，'.join(hyouka_word_feature), hyouka_name_v='，'.join(hyouka_name_vector), hyouka_word_v='，'.join(hyouka_word_vector), finish=finish_datetime, record_id=record_id)
# print(json.dumps({"sql":sql_update}))
cur.execute(sql_update)
conn.commit()
