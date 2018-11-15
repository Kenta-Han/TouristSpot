#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import numpy as np
from pprint import pprint
from gensim import corpora
from gensim import models

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()


def Spot_List_TFIDF(select_spot):
    all_spot_list = []
    cur.execute(select_spot)
    for i in cur:
        all_spot_list.append(i)
    spot_review_list = []
    temp = []
    for i in range(len(all_spot_list)):
        try:
            if all_spot_list[i][0] == all_spot_list[i+1][0]:
                temp.append(list(all_spot_list[i])[1])
            else:
                temp.append(list(all_spot_list[i])[1])
                spot_review_list.append(temp)
                temp = []
        except IndexError:
            temp.append(list(all_spot_list[i])[1])
            spot_review_list.append(temp)
    everyspot = []
    temp = []
    for i in range(len(spot_review_list)):
        for j in range(len(spot_review_list[i])):
            temp.extend(spot_review_list[i][j].split())
        everyspot.append(temp)
        temp = []
    return everyspot

## TFIDFを求める(単語に重み付け)
def Tfidf(review_all):
    dictionary = corpora.Dictionary(review_all)
    dictionary_inv = {}
    for dic in dictionary.token2id.items():
        dictionary_inv[dic[1]]=dic[0]
    corpus = list(map(dictionary.doc2bow,review_all))
    test_model = models.TfidfModel(corpus)
    corpus_tfidf = list(test_model[corpus])
    j = 0
    doc2 = [] ## id表示ではないもの
    for wod in corpus_tfidf:
        i = 0
        doc2.append('') ## 空要素
        doc3 = []
        for ch in wod:
            doc3.append('')
            doc3[i] = [dictionary_inv[ch[0]],ch[1]]
            i += 1
        doc2[j] = doc3
        j += 1
    for i in range(len(doc2)):
        doc2[i].sort(key=lambda x:x[1],reverse=True)
    return doc2

## 金閣寺，清水寺
visited_spot_id_list = ['spt_26101ag2130014551','spt_26105ag2130012063']

##　金閣寺，都庁
visited_spot_id_list = ['spt_26101ag2130014551','spt_13104aj2200025349']

##　金閣寺，新宿御苑
visited_spot_id_list = ['spt_26101ag2130014551','spt_13104ah2140016473']

select_visited_spot_reviews = "SELECT spot_id,wakachi_neologd2 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd2".format(tuple(visited_spot_id_list))

visited_spot_reviews = Spot_List_TFIDF(select_visited_spot_reviews)
visited_tfidf = Tfidf(visited_spot_reviews)

print(visited_tfidf)
