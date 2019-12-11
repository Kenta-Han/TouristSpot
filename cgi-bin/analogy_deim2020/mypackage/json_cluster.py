import sys
import collections, copy, math
import numpy as np
import json, random, string
from scipy.stats import norm
import datetime

import MySQLdb
import os, sys ## 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

def resp(record_id,word,vis_score_dic):
    response_json = {"record_id":"","word":"","vis_score_dic":""}
    response_json["record_id"] = record_id
    response_json["word"] = word
    # response_json["tfidf_dataset"] = tfidf
    response_json["vis_score_dic"] = vis_score_dic
    # response_json["vis_center_use"] = vis_center_use
    return response_json

def response(data,record_id,vis_score_dic):
    # print(data, file=sys.stderr)
    tfidf = []
    for i in range(len(data)):
        tfidf.append([data[i][0],sorted(data[i][1],key=lambda x:x[1],reverse=True)])
    ## 各クラスタ提示キーワード：TFIDFの値の上位10件
    word = []
    for i in range(len(tfidf)):
        tmp = []
        for j in range(len(tfidf[i][1])):
            tmp.append(tfidf[i][1][j][0])
        word.append([tfidf[i][0],tmp[:10]])
    for i in range(len(vis_score_dic)):
        vis_score_dic[i][2] = [int(n) for n in vis_score_dic[i][2]]
    return resp(record_id,word,vis_score_dic)
