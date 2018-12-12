#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import datetime
import json
import MySQLdb

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

## スポットリストTEXT書き出し
select_spot = "SELECT spot_mst.name,area_mst.area1 FROM spot_mst,area_mst WHERE spot_mst.area_id=area_mst.id AND spot_mst.review > 0;"
cur.execute(select_spot)
all = []
for i in cur:
    all.append(i)
seiri = []
for i in range(len(all)):
    s = "---".join(all[i])
    seiri.append(s)
    s = 0
s2 = "\n".join(seiri)
with open('spot.txt', mode='w') as f:
    f.write(str(s2))

## 都道府県リストTEXT書き出し
select_area1 = "SELECT area1 FROM area_mst GROUP BY area1;"
cur.execute(select_area1)
all = []
for i in cur.fetchall():
    all.append(i[0])
s = "\n".join(all)
with open('area1.txt', mode='w') as f:
    f.write(str(s))

## エリアリストTEXT書き出し
select_area2 = "SELECT area2 FROM area_mst GROUP BY area2;"
cur.execute(select_area2)
all = []
for i in cur.fetchall():
    all.append(i[0])
s = "\n".join(all)
with open('area2.txt', mode='w') as f:
    f.write(str(s))
