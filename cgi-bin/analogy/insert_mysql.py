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

####################################
## index_analogy_moto.html 用
####################################
# cgitb.enable()
# form = cgi.FieldStorage()
# record_id = form.getfirst('record_id')
# print(record_id)
# hyouka_category = form.getlist('hyouka_category[]')
# hyouka_category_text = form.getlist('hyouka_category_text[]')
# hyouka_feature = form.getlist('hyouka_feature[]')
# hyouka_feature_text = form.getlist('hyouka_feature_text[]')
# hyouka_harmonic = form.getlist('hyouka_harmonic[]')
# hyouka_harmonic_text = form.getlist('hyouka_harmonic_text[]')
# hyouka_mean = form.getlist('hyouka_mean[]')
# hyouka_mean_text = form.getlist('hyouka_mean_text[]')
# print('Content-type: text/html\nAccess-Control-Allow-Origin: *\n')
#
# finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
#
# sql_update = "UPDATE map_test SET hyouka_c='{c}', hyouka_c_text='{ct}', hyouka_f='{f}', hyouka_f_text='{ft}', hyouka_h='{h}', hyouka_h_text='{ht}', hyouka_m='{m}', hyouka_m_text='{mt}', finish_datetime='{finish}' WHERE id = {record_id};".format(c='，'.join(hyouka_category), ct='，'.join(hyouka_category_text), f='，'.join(hyouka_feature), ft='，'.join(hyouka_feature_text), h='，'.join(hyouka_harmonic), ht='，'.join(hyouka_harmonic_text), m='，'.join(hyouka_mean), mt='，'.join(hyouka_mean_text), finish=finish_datetime, record_id=record_id)
# print(json.dumps({"sql":sql_update}))
#
# cur.execute(sql_update)
# conn.commit()


####################################
## index_analogy.html 用
####################################
cgitb.enable()
form = cgi.FieldStorage()
record_id = form.getfirst('record_id')
print(record_id)
hyouka = form.getlist('hyouka[]')
hyouka_text = form.getlist('hyouka_text[]')
print('Content-type: text/html\nAccess-Control-Allow-Origin: *\n')

finish_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

sql_update = "UPDATE analogy SET hyouka='{h}', hyouka_text='{ht}', finish_datetime='{finish}' WHERE id = {record_id};".format(h='，'.join(hyouka), ht='，'.join(hyouka_text), finish=finish_datetime, record_id=record_id)
print(json.dumps({"sql":sql_update}))

cur.execute(sql_update)
conn.commit()
