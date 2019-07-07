import MySQLdb
import os, sys # 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

## 履歴スポットリスト作成(DBでLIKE検索するため)
def Make_History_List(history):
    all = []
    spot = []
    area = []
    for i in range(len(history)):
        temp = "%"+ history[i] +"%"
        all.append(temp)
        temp = 0
    spot.append(all[0::2])
    area.append(all[1::2])
    return spot,area

## スポット，レビューリスト作成
def SpotORReview_List(spot):
    spot_list = []
    cur.execute(spot)
    for i in cur:
        spot_list.append([i])
    return spot_list

## エリアIDリスト作成
def Area_id_List(area):
    area_id_list = []
    cur.execute(area)
    for i in cur:
        area_id_list.append(i[0])
    return area_id_list
