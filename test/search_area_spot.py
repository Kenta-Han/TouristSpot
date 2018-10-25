#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import numpy as np
from pprint import pprint
import mypackage.package_01 as myp_pk01

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

history_prefecture = "神奈川"
history_area = "鎌倉"

# history_prefecture = "京都"
# history_area = "京都"

select_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND (area2 LIKE '%{area}%' OR area3 LIKE '%{area}%') AND id < 30435;".format(pre = history_prefecture, area = history_area)
area_id_list = []
cur.execute(select_area_id)
for i in cur:
    area_id_list.append(i[0])
print(area_id_list)

select_history_spot = "SELECT DISTINCT id,name,area_id FROM spot_mst WHERE area_id IN {} AND review != 0;".format(tuple(area_id_list))
history_spot_list = myp_pk01.Spot_List(select_history_spot)
pprint(history_spot_list)

print("\n指定エリアid(東京都)")
select_spot = "SELECT id,name,area_id FROM spot_mst WHERE area_id BETWEEN 17698 AND 18516 AND review != 0;"
spot_list = myp_pk01.Spot_List(select_spot)
pprint(spot_list)
