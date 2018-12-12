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
import random,re

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

## index_analogy.html 解析用

def Spot_List(select_spot):
    spot_list = []
    cur.execute(select_spot)
    for i in cur:
        spot_list.append(i)
    return spot_list

select_data = "SELECT * FROM analogy WHERE finish_datetime is not NULL;"
all_data = Spot_List(select_data)

# print(len(all_data))

c_data,f_data,h_data,m_data = [],[],[],[]
for i in range(len(all_data)):
    c_temp = []
    word_c = re.split("--",all_data[i][8])
    unv = re.split("，",all_data[i][6])
    vis = re.split("，",all_data[i][7])
    for j in range(len(unv)):
        c_temp.append([unv[j], vis[j], word_c[j]])
    c_data.append(c_temp)

    f_temp = []
    word_f = re.split("--",all_data[i][12])
    unv = re.split("，",all_data[i][9])
    vis = re.split("，",all_data[i][10])
    for j in range(len(unv)):
        f_temp.append([unv[j],vis[j],word_f[j]])
    f_data.append(f_temp)

    # word_h = re.split("--",all_data[i][18])
    # word_m = re.split("--",all_data[i][21])
    # h_data,m_data = [],[]
    # if len(all_data[15]) != 0:
    #     for j in range(len(all_data[15])):
    #         h_data.append([all_data[15][j],all_data[16][j],word_h[j]])
    #         m_data.append([all_data[15][j],all_data[16][j],word_m[j]])


vector = []
for i in range(len(all_data)):
    spot = []
    temp = []
    user_id = all_data[i][1]
    hyouka = re.split("，",all_data[i][22])
    hyouka_text = re.split("，",all_data[i][23])
    # print(hyouka)
    category,feature,harmonic,mean = [],[],[],[]
    category_t,feature_t,harmonic_t,mean_t = [],[],[],[]
    category_word,feature_word,harmonic_word,mean_word = [],[],[],[]
    for j in range(len(hyouka)):
        temp = re.split("：",hyouka[j])
        tempt = re.split("：",hyouka_text[j])
        if temp[0][-1] == "c":
            category.append(hyouka[j])
            category_t.append(tempt[1])
        elif temp[0][-1] == "f":
            feature.append(hyouka[j])
            feature_t.append(tempt[1])
        elif temp[0][-1] == "h":
            harmonic.append(hyouka[j])
            harmonic_t.append(tempt[1])
        elif temp[0][-1] == "m":
            mean.append(hyouka[j])
            mean_t.append(tempt[1])
    spot.extend([user_id,category,category_t,feature,feature_t,harmonic,harmonic_t,mean,mean_t])
    vector.append(spot)

file_path = "kaiseki.txt"
with open(file_path, "w") as f:
    for i in range(len(vector)):
        f.write("user_id：" + str(vector[i][0]) + "\n")
        f.write("=====絶対的な特徴(カテゴリー) ===== \n" )
        for j in range(len(vector[i][1])):
            f.write(str(vector[i][1][j]) + "，")
            f.write(str(vector[i][2][j]) + "\n")
        f.write("===== 絶対的な特徴(特徴) ===== \n")
        for j in range(len(vector[i][3])):
            f.write(str(vector[i][3][j]) + "，")
            f.write(str(vector[i][4][j]) + "\n")
        f.write("===== 相対的な特徴(調和) ===== \n")
        for j in range(len(vector[i][5])):
            f.write(str(vector[i][5][j]) + "，")
            f.write(str(vector[i][6][j]) + "\n")
        f.write("===== 相対的な特徴(相加) ===== \n")
        for j in range(len(vector[i][7])):
            f.write(str(vector[i][7][j]) + "，")
            f.write(str(vector[i][8][j]) + "\n")
        f.write("\n\n")
