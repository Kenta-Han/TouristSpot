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

def Spot_List(select_spot):
    spot_list = []
    cur.execute(select_spot)
    for i in cur:
        spot_list.append(i)
    return spot_list

def Anket(tmp):
    if tmp == "0": return "イメージ語なし"
    elif tmp == "1": return "思わない"
    elif tmp == "2": return "やや思わない"
    elif tmp == "3": return "普通"
    elif tmp == "4": return "やや思う"
    elif tmp == "5": return "思う"


select_data = "SELECT * FROM map_test WHERE finish_datetime is not NULL;"

all_data = Spot_List(select_data)

print(len(all_data))

########################
## 絶対的な特徴（特徴）
########################

vector = []
for i in range(len(all_data)):
    temp = []



    unvisited_v = re.split("，",all_data[i][15])
    for vec in range(len(unvisited_v)):
        visited_v = re.split("，",all_data[i][16])
        cossim_v = re.split("，",all_data[i][17])

        word_v = re.split("--",all_data[i][18])
        Word = []
        for w in word_v:
            if w[0] == " ":
                w = w[1:]
            Word.append(w)

        word_v_m = re.split("--",all_data[i][21])
        Word_M = []
        for w in word_v_m:
            if w[0] == " ":
                w = w[1:]
            Word_M.append(w)

        hyouka_name_v = re.split("，",all_data[i][26])
        Res_Name = []
        for vec_name in hyouka_name_v:
            tmp = re.split("：",vec_name)[1]
            Res_Name.append(Anket(tmp))

        hyouka_word_v = re.split("，",all_data[i][27])
        Res_Word = []
        for vecw in hyouka_word_v:
            tmp = re.split("：",vecw)[1]
            Res_Word.append(Anket(tmp))

        hyouka_word_v_m = re.split("，",all_data[i][28])
        Res_Word_M = []
        for vecwm in hyouka_word_v_m:
            tmp = re.split("：",vecwm)[1]
            Res_Word_M.append(Anket(tmp))

        temp.append([unvisited_v[vec],visited_v[vec],cossim_v[vec],Res_Name[vec],Word[vec],Res_Word[vec],Word_M[vec],Res_Word_M[vec]])
    vector.append(temp)
pprint(vector)


########################
## 相対的特徴
########################

# vector = []
# for i in range(len(all_data)):
#     temp = []
#     unvisited_v = re.split("，",all_data[i][15])
#     for vec in range(len(unvisited_v)):
#         visited_v = re.split("，",all_data[i][16])
#         cossim_v = re.split("，",all_data[i][17])
#
#         word_v = re.split("--",all_data[i][18])
#         Word = []
#         for w in word_v:
#             if w[0] == " ":
#                 w = w[1:]
#             Word.append(w)
#
#         word_v_m = re.split("--",all_data[i][21])
#         Word_M = []
#         for w in word_v_m:
#             if w[0] == " ":
#                 w = w[1:]
#             Word_M.append(w)
#
#         hyouka_name_v = re.split("，",all_data[i][26])
#         Res_Name = []
#         for vec_name in hyouka_name_v:
#             tmp = re.split("：",vec_name)[1]
#             Res_Name.append(Anket(tmp))
#
#         hyouka_word_v = re.split("，",all_data[i][27])
#         Res_Word = []
#         for vecw in hyouka_word_v:
#             tmp = re.split("：",vecw)[1]
#             Res_Word.append(Anket(tmp))
#
#         hyouka_word_v_m = re.split("，",all_data[i][28])
#         Res_Word_M = []
#         for vecwm in hyouka_word_v_m:
#             tmp = re.split("：",vecwm)[1]
#             Res_Word_M.append(Anket(tmp))
#
#         temp.append([unvisited_v[vec],visited_v[vec],cossim_v[vec],Res_Name[vec],Word[vec],Res_Word[vec],Word_M[vec],Res_Word_M[vec]])
#     vector.append(temp)
# pprint(vector)
