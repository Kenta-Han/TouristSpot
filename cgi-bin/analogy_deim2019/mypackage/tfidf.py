from gensim import corpora
from gensim import models

import os, sys # 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

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

## TFIDFを求める(単語に重み付け)，特徴ベクトル用
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
    return doc2


# ## TFIDFを求める(単語に重み付け)，差分ベクトル用
# def Tfidf_HM(review_all):
#     dictionary = corpora.Dictionary(review_all)
#     dictionary_inv = {}
#     for dic in dictionary.token2id.items():
#         dictionary_inv[dic[1]]=dic[0]
#     corpus = list(map(dictionary.doc2bow,review_all))
#     test_model = models.TfidfModel(corpus)
#     corpus_tfidf = list(test_model[corpus])
#     j = 0
#     doc2 = [] ## id表示ではないもの
#     for wod in corpus_tfidf:
#         i = 0
#         doc2.append('') ## 空要素
#         doc3 = []
#         for ch in wod:
#             doc3.append('')
#             doc3[i] = [dictionary_inv[ch[0]],ch[1]]
#             i += 1
#         doc2[j] = doc3
#         j += 1
#     ## スポット毎の平均を計算
#     mean = []
#     sum = 0
#     for i in range(len(doc2)):
#         for j in range(len(doc2[i])):
#             sum += doc2[i][j][1]
#         mean.append(sum/len(doc2[i]))
#         sum = 0
#     return doc2,mean
