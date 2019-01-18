import numpy as np
import copy
import MySQLdb
from gensim import corpora
from gensim import models
import mypackage.cossim as myp_cos
from pprint import pprint
from tqdm import tqdm
import re
sc = myp_cos.SimCalculator()

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

bytesymbols = re.compile("[!-/:-@*[-`{-~\d]") ## 半角記号，数字\d

def CosSim(x, y):
    return np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))

########################################################
########################################################
def Spot_List(select_spot):
    spot_list = []
    cur.execute(select_spot)
    for i in cur:
        spot_list.append(i)
    return spot_list

def Doc2Cec_Feature(spot_vectors): ## doc2vecを使ってスポットベクトルの差を求める
    result_list = []
    for i in range(len(spot_vectors)):
        x = copy.deepcopy(spot_vectors)
        target = list(x[i][2:302])
        name = x[i][1]
        x.pop(i)
        temp = []
        for j in range(len(x)):
            temp.append(list(x[j][2:302]))
        temp = np.array(temp)
        result = np.round((target-sum(temp)/len(temp)),3)
        result_list.append([name, list(result)])
        target = []
        result = []
    return result_list

def Recommend_All(visited_name,unvisited_name,visited_review,unvisited_review):
    value_UtoV = []
    for i in range(len(unvisited_name)):
        temp_UtoV = []
        for j in range(len(visited_name)):
            # unvisited_to_visited = sc.sim_cos(unvisited_review[i],visited_review[j])
            unvisited_to_visited = CosSim(unvisited_review[i],visited_review[j])
            temp_UtoV.append([visited_name[j],unvisited_to_visited])
        value_UtoV.append(temp_UtoV)
    list_UtoV = list(zip(unvisited_name,value_UtoV))
    list_UtoV_top = []
    for i in range(len(list_UtoV)):
        list_UtoV[i][1].sort(key=lambda x:x[1],reverse=True)
        if list_UtoV[i][1][0][1] > 0.125:
            list_UtoV_top.append([list_UtoV[i][0],list_UtoV[i][1][0]])
        else:
            continue
    return list_UtoV_top

########################################################
########################################################
def Spot_List_TFIDF(select_spot):
    all_spot_list = []
    cur.execute(select_spot)
    for i in cur:
        all_spot_list.append(i)
    print(len(all_spot_list))
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
    # print(dictionary)
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

def Sort_TFIDF_UtoV(vis_tfidf,unvis_tfidf,vis_spot_name,unvis_spot_name,vis_mean,unvis_mean,result):
    ## TFIDFの結果にスポット名を追加
    vis_spot,unvis_spot = [],[]
    for i in range(len(vis_spot_name)):
        vis_spot.append([vis_spot_name[i],vis_tfidf[i],vis_mean[i]])
    for i in range(len(unvis_spot_name)):
        unvis_spot.append([unvis_spot_name[i],unvis_tfidf[i],unvis_mean[i]])
    ## 一番類似するスポットを関連付ける
    visited,unvisited,all_spot = [],[],[]
    visited_mean,unvisited_mean = [],[]
    for i in range(len(result)):
        for j in range(len(unvis_spot)):
            if result[i][0] == unvis_spot[j][0]:
                unvisited.append(unvis_spot[j][1])
                unvisited_mean.append(unvis_spot[j][2])
    for i in range(len(result)):
        for j in range(len(vis_spot)):
            if result[i][1][0] == vis_spot[j][0]:
                visited.append(vis_spot[j][1])
                visited_mean.append(unvis_spot[j][2])
    all_spot.extend([unvisited,visited])
    ## 一番類似するスポットの特徴語top10を求める
    all,top10 = [],[]
    for i in tqdm(range(len(all_spot[0]))):
        temp = []
        for j in tqdm(range(len(all_spot[0][i]))):
            for k in range(len(all_spot[1][i])):
                ## 同じ単語，値は共に平均以上
                # if all_spot[0][i][j][0]==all_spot[1][i][k][0] and all_spot[0][i][j][1]>=unvisited_mean[i] and all_spot[1][i][k][1]>=visited_mean[i]:
                # if all_spot[0][i][j][0]==all_spot[1][i][k][0] and all_spot[0][i][j][1]>=0.01 and all_spot[1][i][k][1]>=0.01:
                if all_spot[0][i][j][0]==all_spot[1][i][k][0] and len(all_spot[0][i][j][0])>1 and re.search(bytesymbols,all_spot[0][i][j][0])==None and all_spot[0][i][j][1]>=unvisited_mean[i] and all_spot[1][i][k][1]>=visited_mean[i]:
                    temp.append([all_spot[0][i][j][0],abs(all_spot[0][i][j][1]-all_spot[1][i][k][1]),all_spot[0][i][j][1],all_spot[1][i][k][1]]) ## 元の値をみる
                    # temp.append([all_spot[0][i][j][0],abs(all_spot[0][i][j][1]-all_spot[1][i][k][1]),all_spot[0][i][j][1],all_spot[1][i][k][1]]) ## 元の値をみる
        all.append(temp)
        all[i].sort(key=lambda x:x[1]) ## 昇順ソート(0に近い程が良い)
        # all[i].sort(key=lambda x:x[1],reverse=True)
        top10.append([result[i][0],result[i][1][0],all[i][:10]])
    return top10

## 調和平均 差が小値が大，差が大値が小 → 値が大の方が良い(昇順後ろから10個)
def Sort_TFIDF_UtoV_Harmonic(vis_tfidf,unvis_tfidf,vis_spot_name,unvis_spot_name,result):
    ## TFIDFの結果にスポット名を追加
    vis_spot,unvis_spot = [],[]
    for i in range(len(vis_spot_name)):
        vis_spot.append([vis_spot_name[i],vis_tfidf[i]])
    for i in range(len(unvis_spot_name)):
        unvis_spot.append([unvis_spot_name[i],unvis_tfidf[i]])
    # print(vis_spot)
    # print(unvis_spot)
    ## 一番類似するスポットを関連付ける
    visited,unvisited,all_spot = [],[],[]
    for i in range(len(result)):
        for j in range(len(unvis_spot)):
            if result[i][0] == unvis_spot[j][0]:
                unvisited.append(unvis_spot[j][1])
    for i in range(len(result)):
        for j in range(len(vis_spot)):
            if result[i][1][0] == vis_spot[j][0]:
                visited.append(vis_spot[j][1])
    all_spot.extend([unvisited,visited])
    ## 一番類似するスポットの特徴語top10を求める
    all,top10 = [],[]
    for i in tqdm(range(len(all_spot[0]))):
        temp = []
        same_word = list(set([all_spot[0][i][j][0] for j in range(len(all_spot[0][i]))]) & set([all_spot[1][i][j][0] for j in range(len(all_spot[1][i]))]))
        for sw in same_word:
            un = [j for j in range(len(all_spot[0][i])) if all_spot[0][i][j][0] == sw][0]
            vi = [j for j in range(len(all_spot[1][i])) if all_spot[1][i][j][0] == sw][0]
            if len(all_spot[0][i][un][0])>1 and re.search(bytesymbols,all_spot[0][i][un][0])==None:
                 temp.append([all_spot[0][i][un][0],abs(2/(1/all_spot[0][i][un][1]+1/all_spot[1][i][vi][1])),all_spot[0][i][un][1],all_spot[1][i][vi][1]])
        all.append(temp)
        all[i].sort(key=lambda x:x[1],reverse=True)## 降順ソート
        # ## 未訪問，既訪問，類似度，単語(最初の10個まで)
        top10.append([result[i][0],result[i][1][0],result[i][1][1],all[i][:5]])
    return top10
