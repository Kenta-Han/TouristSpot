#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import numpy as np
from pprint import pprint
from sklearn.decomposition import PCA ## scikit-learnのPCAクラス
import pandas as pd ## 便利なDataFrameを使うためのライブラリ
import matplotlib.pyplot as plt
import mypackage.package_01 as myp_pk01
import MeCab
from tqdm import tqdm

m = MeCab.Tagger('mecabrc')

def Spot_List(select_spot):
    spot_list = []
    cur.execute(select_spot)
    for i in cur:
        spot_list.append(i)
    return spot_list

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

select_all = "SELECT id,review_text FROM review_all where id BETWEEN 228684 AND 1481838;"
all = myp_pk01.Spot_List(select_all)
# print(all)
result = []
for i in tqdm(range(len(all))):
    chunks = m.parse(all[i][1]).splitlines()
    temp_w = []
    for w in chunks:
        word = list(w.split("\t"))
        if word[0] != "EOS":
            word_hinsi = list(word[1].split(","))
            if word_hinsi[0]=="記号" or word_hinsi[0]=="助詞" or word_hinsi[0]=="助動詞" or word_hinsi[0]=="連体詞":
                continue
            else:
                # print(word_hinsi[6])
                temp_w.append(word_hinsi[6])
        else:
            temp_w = " ".join(temp_w)
            # result.append(temp_w)
            insert = "INSERT INTO review_wakachi_neologd2(id,wakachi_text) VALUES(%s,%s);"
            cur.execute(insert,(all[i][0],temp_w))
            conn.commit()
# print(result)