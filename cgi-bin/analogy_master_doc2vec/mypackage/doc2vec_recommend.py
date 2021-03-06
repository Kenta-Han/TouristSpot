import numpy as np
import copy
import MySQLdb
import re,sys

import os, sys # 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

def spot_list(select_spot):
    spot_list = []
    cur.execute(select_spot)
    for i in cur:
        spot_list.append(i)
    return spot_list

def cossim(x, y):
    return np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))

def recommend_all(visited_name,unvisited_name,visited_review,unvisited_review):
    value_UtoV = []
    for i in range(len(unvisited_name)):
        temp_UtoV = []
        for j in range(len(visited_name)):
            unvisited_to_visited = cossim(unvisited_review[i],visited_review[j])
            temp_UtoV.append([visited_name[j],unvisited_to_visited])
        value_UtoV.append(temp_UtoV)
    list_UtoV = list(zip(unvisited_name,value_UtoV))
    list_UtoV_top = []
    for i in range(len(list_UtoV)):
        list_UtoV[i][1].sort(key=lambda x:x[1],reverse=True)
        for j in range(len(list_UtoV[i][1])):
            # if list_UtoV[i][1][j][1] > 0.1: #0.125 / 0.1 /0.05
            list_UtoV_top.append([list_UtoV[i][0],list_UtoV[i][1][j]])
            # else:
            #     continue
    return list_UtoV_top
