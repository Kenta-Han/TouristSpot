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

## ストップワード
file_path = "./wakachi/stopword.txt"
with open(file_path, "r") as f:
    data = f.read()
stopword = data.split("\n")

## 動詞，2文字，ひらがな　を削除するため
file_path = "./wakachi/deleteword.txt"
with open(file_path, "r") as f:
    data = f.read()
deleteword = data.split("\n")

## 色々 を削除するため
file_path = "./wakachi/otherword.txt"
with open(file_path, "r") as f:
    data = f.read()
otherword = data.split("\n")

select_all = "SELECT id,review_text FROM review_all;"
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
            ## 削除：記号，助詞，助動詞，連帯詞，ストップワード ，動詞かつ2文字かつひらがな
            other_check = (word_hinsi[0] in ["記号","助詞","助動詞","連体詞"])
            mathword_check = (word_hinsi[0]=="名詞" and word_hinsi[1]=="数")
            stopword_check1 = (word[0] in stopword)
            stopword_check2 = (word_hinsi[6] in stopword)
            deleteword_check1 = (word_hinsi[0]=="動詞" and len(word[0])==2 and (word[0] in deleteword))
            deleteword_check2 = (word_hinsi[0]=="動詞" and len(word_hinsi[6])==2 and (word_hinsi[6] in deleteword))
            otherword_check = (word_hinsi[6] in otherword)

            if other_check or mathword_check or stopword_check1 or stopword_check2 or deleteword_check1 or deleteword_check2 or otherword_check:
                continue
            else:
                # print(word_hinsi[6])
                if word_hinsi[6] == "*":
                    temp_w.append(word[0])
                else:
                    temp_w.append(word_hinsi[6])
        else:
            temp_w = " ".join(temp_w)
            result.append(temp_w)
            insert = "INSERT INTO review_wakachi_neologd5(id,wakachi_text) VALUES(%s,%s);"
            cur.execute(insert,(all[i][0],temp_w))
            conn.commit()
# print(result)
