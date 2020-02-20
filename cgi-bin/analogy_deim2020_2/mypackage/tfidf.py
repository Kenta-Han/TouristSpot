from gensim import corpora
from gensim import models
import math,copy
from tqdm import tqdm

import os, sys # 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

def spot_list_tfidf(select_spot):
    all_spot_list = []
    cur.execute(select_spot)
    for i in cur:
        all_spot_list.append(list(i))
    all_spot_list = sorted(all_spot_list,key=lambda x:x[0],reverse=True)
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

## TFIDFを求める(単語に重み付け)，特徴ベクトル用
def tfidf(review_all):
    dictionary = corpora.Dictionary(review_all)
    # print(sorted([[dictionary[key],math.log2(len(review_all)/value)] for key,value in dictionary.dfs.items()],key=lambda x:x[1],reverse=True)[:200], file=sys.stderr)
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
    return doc2

## TFIDFを求める（IDF範囲は既訪問スポット全クラスタ）
def tfidf_new(dictionary,review_all,idf_length):
    spot = []
    for i in range(len(review_all)):
        tfidf_data = []
        vec = dictionary.doc2bow(review_all[i]) ## 辞書
        for word_id,word_num in vec:
            tf = word_num / len(review_all[i]) ## 既訪問 or 検索結果
            idf = math.log(idf_length / (dictionary.dfs[word_id] + 1)) ## 既訪問
            tfidf_data.append([dictionary[word_id], tf * idf])
        tfidf_sort = sorted(tfidf_data,key=lambda x:x[1],reverse=True)
        spot.append(tfidf_sort) ## スポット毎のTFIDF
    return spot


## 既訪問スポットの特徴語は，RCfからTFを，クラスタ関係なく既訪問スポットをdとしたIDF．検索結果は，RCfをRCu，IDFも同様に変更したもの．(既訪問：IDFの分子の全文書数=全既訪問スポットの数．検索結果：IDFの分子の全文書数=全検索結果スポットの数．)
def tfidf_res1(dictionary,data_length,review_all):
    spot = []
    for i in range(len(review_all)):
        tfidf_data = []
        vec = dictionary.doc2bow(review_all[i])
        for word_id,word_num in vec:
            tf = word_num / len(review_all[i])
            # idf = math.log(data_length / (dictionary.dfs[word_id] + 1))
            idf = math.log((data_length + 1) / (dictionary.dfs[word_id] + 1))
            tfidf_data.append([dictionary[word_id], tf * idf, tf, idf])
        tfidf_sort = sorted(tfidf_data,key=lambda x:x[1],reverse=True)
        spot.append(tfidf_sort) ## スポット毎のTFIDF
    return spot

## 既訪問スポットの特徴語は，RCfからTFを，各クラスタをdとしたIDF．検索結果に関しては以下略．(既訪問，検索結果：IDFの分子の全文書数 = 全！！クラスタ数)
def tfidf_res2(dictionary,data_length,review_all):
    spot = []
    for i in range(len(review_all)):
        tfidf_data = []
        vec = dictionary.doc2bow(review_all[i])
        for word_id,word_num in vec:
            tf = word_num / len(review_all[i])
            # idf = math.log(data_length / (dictionary.dfs[word_id] + 1))
            idf = math.log((data_length + 1) / (dictionary.dfs[word_id] + 1))
            tfidf_data.append([dictionary[word_id], tf * idf, tf, idf])
        tfidf_sort = sorted(tfidf_data,key=lambda x:x[1],reverse=True)
        spot.append(tfidf_sort) ## スポット毎のTFIDF
    return spot

def tfidf_res(dictionary,corpus_tfidf):
    spot = []
    for vec in corpus_tfidf:
        tfidf_data = []
        for word_id,value in vec:
            tfidf_data.append([dictionary[word_id], value])
        tfidf_sort = sorted(tfidf_data,key=lambda x:x[1],reverse=True)
        spot.append(tfidf_sort) ## スポット毎のTFIDF
    return spot
