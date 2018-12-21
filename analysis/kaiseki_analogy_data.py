#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import MySQLdb
import numpy as np
from pprint import pprint
import re

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

## index_analogy.html の実験デーダの分析用 (table:analysis_analogy)

def Select_Data(select_data):
    spot_list = []
    cur.execute(select_data)
    for i in cur:
        spot_list.append(i)
    return spot_list

select_category = "SELECT * FROM analysis_analogy WHERE way='category';"
pprint(Select_Data(select_category))

select_feature = "SELECT * FROM analysis_analogy WHERE way='feature';"
pprint(Select_Data(select_feature))

select_harmonic = "SELECT * FROM analysis_analogy WHERE way='harmonic';"
pprint(Select_Data(select_harmonic))

select_mean = "SELECT * FROM analysis_analogy WHERE way='mean';"
pprint(Select_Data(select_mean))
