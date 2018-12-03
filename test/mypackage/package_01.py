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
    value_VtoU = []
    value_UtoV = []
    for i in range(len(visited_name)):
        temp_VtoU = []
        for j in range(len(unvisited_name)):
            # visited_to_unvisited = sc.sim_cos(visited_review[i],unvisited_review[j])
            visited_to_unvisited = CosSim(visited_review[i],unvisited_review[j])
            temp_VtoU.append([unvisited_name[j],visited_to_unvisited])
        value_VtoU.append(temp_VtoU)
    list_VtoU = list(zip(visited_name,value_VtoU)) ## リスト作成(スポット名,類似度)
    list_VtoU_top = [] ## スポットから類似度一番高いスポットを取り出す
    for i in range(len(list_VtoU)):
        list_VtoU[i][1].sort(key=lambda x:x[1],reverse=True) ## 降順ソート
        # list_VtoU_top.append([list_VtoU[i][0],list_VtoU[i][1][0]])
        ## 0.1以上
        if list_VtoU[i][1][0][1] > 0.125:
            list_VtoU_top.append([list_VtoU[i][0],list_VtoU[i][1][0]])
        else:
            continue

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
    # pprint(list_VtoU)
    # print("VtoU　↑\nUtoV　↓")
    # pprint(list_UtoV)
    return list_VtoU_top,list_UtoV_top


########################################################
########################################################
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
    ## スポット毎の平均を計算
    mean = []
    sum = 0
    for i in range(len(doc2)):
        for j in range(len(doc2[i])):
            sum += doc2[i][j][1]
        mean.append(sum/len(doc2[i]))
        sum = 0
    return doc2,mean

def Sort_TFIDF_VtoU(vis_tfidf,unvis_tfidf,vis_spot_name,unvis_spot_name,vis_mean,unvis_mean,result):
    ## TFIDFの結果にスポット名を追加
    vis_spot,unvis_spot = [],[]
    for i in range(len(vis_spot_name)):
        vis_spot.append([vis_spot_name[i],vis_tfidf[i],vis_mean[i]])
    for i in range(len(unvis_spot_name)):
        unvis_spot.append([unvis_spot_name[i],unvis_tfidf[i],unvis_mean[i]])
    ## 一番類似するスポットを関連付ける
    visited,unvisited,set = [],[],[]
    visited_mean,unvisited_mean = [],[]
    for i in range(len(result)):
        for j in range(len(vis_spot)):
            if result[i][0] == vis_spot[j][0]:
                visited.append(vis_spot[j][1])
                visited_mean.append(unvis_spot[j][2])
    for i in range(len(result)):
        for j in range(len(unvis_spot)):
            if result[i][1][0] == unvis_spot[j][0]:
                unvisited.append(unvis_spot[j][1])
                unvisited_mean.append(unvis_spot[j][2])
    set.extend([visited,unvisited])
    ## 一番類似するスポットの特徴語top10を求める
    all,top10 = [],[]
    for i in tqdm(range(len(set[0]))):
        temp = []
        for j in tqdm(range(len(set[0][i]))):
            for k in range(len(set[1][i])):
                ## 同じ単語，値は共に平均以上
                if set[0][i][j][0]==set[1][i][k][0] and set[0][i][j][1]>=visited_mean[i] and set[1][i][k][1]>=unvisited_mean[i]:
                # if set[0][i][j][0]==set[1][i][k][0] and set[0][i][j][1]>=0.01 and set[1][i][k][1]>=0.01:
                    temp.append([set[0][i][j][0],abs(set[0][i][j][1]-set[1][i][k][1]),set[0][i][j][1],set[1][i][k][1]]) ## 元の値をみる
        all.append(temp)
        all[i].sort(key=lambda x:x[1]) ## 昇順ソート(0に近い程が良い)
        top10.append([result[i][0],result[i][1][0],all[i][:10]])
    return top10

def Sort_TFIDF_UtoV(vis_tfidf,unvis_tfidf,vis_spot_name,unvis_spot_name,vis_mean,unvis_mean,result):
    ## TFIDFの結果にスポット名を追加
    vis_spot,unvis_spot = [],[]
    for i in range(len(vis_spot_name)):
        vis_spot.append([vis_spot_name[i],vis_tfidf[i],vis_mean[i]])
    for i in range(len(unvis_spot_name)):
        unvis_spot.append([unvis_spot_name[i],unvis_tfidf[i],unvis_mean[i]])
    ## 一番類似するスポットを関連付ける
    visited,unvisited,set = [],[],[]
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
    set.extend([unvisited,visited])
    ## 一番類似するスポットの特徴語top10を求める
    all,top10 = [],[]
    for i in tqdm(range(len(set[0]))):
        temp = []
        for j in tqdm(range(len(set[0][i]))):
            for k in range(len(set[1][i])):
                ## 同じ単語，値は共に平均以上
                # if set[0][i][j][0]==set[1][i][k][0] and set[0][i][j][1]>=unvisited_mean[i] and set[1][i][k][1]>=visited_mean[i]:
                # if set[0][i][j][0]==set[1][i][k][0] and set[0][i][j][1]>=0.01 and set[1][i][k][1]>=0.01:
                if set[0][i][j][0]==set[1][i][k][0] and len(set[0][i][j][0])>1 and re.search(bytesymbols,set[0][i][j][0])==None and set[0][i][j][1]>=unvisited_mean[i] and set[1][i][k][1]>=visited_mean[i]:
                    temp.append([set[0][i][j][0],abs(set[0][i][j][1]-set[1][i][k][1]),set[0][i][j][1],set[1][i][k][1]]) ## 元の値をみる
                    # temp.append([set[0][i][j][0],abs(set[0][i][j][1]-set[1][i][k][1]),set[0][i][j][1],set[1][i][k][1]]) ## 元の値をみる
        all.append(temp)
        all[i].sort(key=lambda x:x[1]) ## 昇順ソート(0に近い程が良い)
        # all[i].sort(key=lambda x:x[1],reverse=True)
        top10.append([result[i][0],result[i][1][0],all[i][:10]])
    return top10

## 調和平均 差が小値が大，差が大値が小 → 値が大の方が良い(昇順後ろから10個)
def Sort_TFIDF_VtoU_Harmonic(vis_tfidf,unvis_tfidf,vis_spot_name,unvis_spot_name,vis_mean,unvis_mean,result):
    ## TFIDFの結果にスポット名を追加
    vis_spot,unvis_spot = [],[]
    for i in range(len(vis_spot_name)):
        vis_spot.append([vis_spot_name[i],vis_tfidf[i]])
    for i in range(len(unvis_spot_name)):
        unvis_spot.append([unvis_spot_name[i],unvis_tfidf[i]])
    ## 一番類似するスポットを関連付ける
    visited,unvisited,set = [],[],[]
    for i in range(len(result)):
        for j in range(len(vis_spot)):
            if result[i][0] == vis_spot[j][0]:
                visited.append(vis_spot[j][1])
    for i in range(len(result)):
        for j in range(len(unvis_spot)):
            if result[i][1][0] == unvis_spot[j][0]:
                unvisited.append(unvis_spot[j][1])
    set.extend([visited,unvisited])
    ## 一番類似するスポットの特徴語top10を求める
    all,top10 = [],[]
    for i in tqdm(range(len(set[0]))):
        temp = []
        for j in tqdm(range(len(set[0][i]))):
            for k in range(len(set[1][i])):
                if set[0][i][j][0]==set[1][i][k][0] and len(set[0][i][j][0])>1 and re.search(bytesymbols,set[0][i][j][0])==None:
                    temp.append([set[0][i][j][0],abs(2/(1/set[0][i][j][1]+1/set[1][i][k][1])),set[0][i][j][1],set[1][i][k][1]])
        all.append(temp)
        all[i].sort(key=lambda x:x[1],reverse=True) ## 昇順ソート
        top10.append([result[i][0],result[i][1][0],all[i][:10]])
    return top10

def Sort_TFIDF_UtoV_Harmonic(vis_tfidf,unvis_tfidf,vis_spot_name,unvis_spot_name,vis_mean,unvis_mean,result):
    ## TFIDFの結果にスポット名を追加
    vis_spot,unvis_spot = [],[]
    for i in range(len(vis_spot_name)):
        vis_spot.append([vis_spot_name[i],vis_tfidf[i]])
    for i in range(len(unvis_spot_name)):
        unvis_spot.append([unvis_spot_name[i],unvis_tfidf[i]])
    ## 一番類似するスポットを関連付ける
    visited,unvisited,set = [],[],[]
    for i in range(len(result)):
        for j in range(len(unvis_spot)):
            if result[i][0] == unvis_spot[j][0]:
                unvisited.append(unvis_spot[j][1])
    for i in range(len(result)):
        for j in range(len(vis_spot)):
            if result[i][1][0] == vis_spot[j][0]:
                visited.append(vis_spot[j][1])
    set.extend([unvisited,visited])
    ## 一番類似するスポットの特徴語top10を求める
    all,top10 = [],[]
    for i in tqdm(range(len(set[0]))):
        temp = []
        for j in tqdm(range(len(set[0][i]))):
            for k in range(len(set[1][i])):
                if set[0][i][j][0]==set[1][i][k][0] and len(set[0][i][j][0])>1 and re.search(bytesymbols,set[0][i][j][0])==None:
                    temp.append([set[0][i][j][0],abs(2/(1/set[0][i][j][1]+1/set[1][i][k][1])),set[0][i][j][1],set[1][i][k][1]])
        all.append(temp)
        all[i].sort(key=lambda x:x[1],reverse=True)
        top10.append([result[i][0],result[i][1][0],all[i][:10]])
    return top10
