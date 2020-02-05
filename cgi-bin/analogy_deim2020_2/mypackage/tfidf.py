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

## ATFを求める(単語に重み付け)，特徴ベクトル用
def atf(conter_list):
    word_data = []
    for i in range(len(conter_list)):
        for j in range(len(conter_list[i][1])):
            word_data.append([conter_list[i][1][j][0],conter_list[i][1][j][1]])
    word_data_sort = sorted(word_data,key=lambda x:x[0])
    word_data_sort.append(["-finish-",1])
    res, tmp = [],[]
    for i in range(1,len(word_data_sort)):
        if word_data_sort[i-1][0] == word_data_sort[i][0]:
            tmp.append(word_data_sort[i-1][1])
        else:
            tmp.append(word_data_sort[i-1][1])
            res.append([word_data_sort[i-1][0],tmp])
            tmp = []
    word_val = []
    for i in range(len(res)):
        word_val.append([res[i][0],sum(res[i][1])/len(conter_list)])
    result = []
    for i in tqdm(range(len(conter_list))):
        tmp = []
        for j in range(len(conter_list[i][1])):
            for k in range(len(word_val)):
                if conter_list[i][1][j][0] == word_val[k][0]:
                    tmp.append([conter_list[i][1][j][0],conter_list[i][1][j][1]/(word_val[k][1]**0.3)])
        s = sorted(tmp,key=lambda x:x[1],reverse=True)
        result.append([conter_list[i][0],s[:10]])
    return result
