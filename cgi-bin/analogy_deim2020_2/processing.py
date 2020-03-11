#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
from tqdm import tqdm
import datetime, re, json, copy, time, math
import numpy as np
import mypackage.other as myp_other
import mypackage.doc2vec_recommend as myp_doc_rec
import mypackage.tfidf as myp_tfidf
import mypackage.cluster as myp_cluster
import mypackage.json_cluster as myp_json_cluster
import mypackage.cos_sim_tfidf as myp_cos_tfidf
import mypackage.feature_mean as myp_feature
import mypackage.normal_distribution_map_line as myp_norm_l
from collections import Counter ## 単語出現頻度
from collections import defaultdict
from gensim import corpora
from gensim import models

import MySQLdb
import os, sys ## 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

def Randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

## 承認コード，乱数生成
def Response_Random():
    json_random = {"randomname":""}
    random = Randomname(12)
    json_random["randomname"] = random
    return random,json_random

def new_idf(docfreq, totaldocs, log_base=2.0, add=0.0):
    return add + math.log((totaldocs+1) / (docfreq+1), log_base)

cgitb.enable()
form = cgi.FieldStorage()
user_id = form.getvalue('user_id') ## CrowdWorksID
history = form.getlist('visited_name[]')
prefecture = form.getvalue('prefecture_name') ## 都道府県
area = form.getvalue('area_name') ## エリア
start_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
print('Content-type: text/html\nAccess-Control-Allow-Origin: *\n')

############################################################
## 既訪問スポット情報
############################################################
## 既訪問を利用
history_list = []
visited_spot_list = [] ## 履歴スポット
history = "---".join(history)
history_list = re.split("---", history)
like_spot_list,like_area_list = myp_other.make_history_list(history_list)

for i in range(len(like_spot_list[0])):
    select_user_history = "SELECT id,name,lat,lng,area_id,url,description,category1 from spot_mst2 where name like '{spot}' AND address like '{area}' AND (lat!=0 or lng!=0) AND review=(SELECT max(review) FROM spot_mst WHERE name like '{spot}' AND address like '{area}' AND review != 0);".format(spot=like_spot_list[0][i],area=like_area_list[0][i])
    cur.execute(select_user_history)
    spot_data = cur.fetchone()
    if spot_data is None:
        continue
    else:
        visited_spot_list.append(spot_data)

visited_spot_id_list = []
vis_spot_id,vis_name,vis_lat,vis_lng,vis_url,vis_description,vis_cate = [],[],[],[],[],[],[]
for i in range(len(visited_spot_list)):
    visited_spot_id_list.append(visited_spot_list[i][0])
    if visited_spot_list[i][2]!=0 and visited_spot_list[i][3]!=0:
        vis_spot_id.append(visited_spot_list[i][0])
        vis_name.append(visited_spot_list[i][1])
        vis_lat.append(str(visited_spot_list[i][2]))
        vis_lng.append(str(visited_spot_list[i][3]))
        vis_url.append(str(visited_spot_list[i][5]))
        vis_description.append(str(visited_spot_list[i][6]))
        vis_cate.append(str(visited_spot_list[i][7]))
    else:
        continue

vis_cate = [x for x in set(vis_cate) if vis_cate.count(x) >= 1]

############################################################
## DB挿入
############################################################
## ユーザ入力とDBヘ書き込む
sql_insert = "INSERT INTO analogy_deim2020(user_id, prefecture, area, start_datetime, history) VALUES(%s,%s,%s,%s,%s);"
cur.execute(sql_insert,(user_id, prefecture, area, start_datetime, history))
conn.commit()

## ユーザの最新情報を得る
cur.execute("SELECT max(id) FROM analogy_deim2020 WHERE user_id='{user}';".format(user = user_id))
record_id = cur.fetchone()[0]


############################################################
## 未訪問エリア情報
############################################################
## 未訪問エリアIDリスト
if area == None:
    select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND id < 30435;".format(pre = prefecture)
    unvisited_area_id_list = myp_other.area_id_list(select_unvisited_area_id)
    unvisited_area_id_list = myp_other.area_id_list(select_unvisited_area_id)
else:
    select_unvisited_area_id = "SELECT DISTINCT id FROM area_mst WHERE area1 LIKE '%{pre}%' AND (area2 LIKE '%{area}%' OR area3 LIKE '%{area}%') AND id < 30435;".format(pre = prefecture, area = area)
    unvisited_area_id_list = myp_other.area_id_list(select_unvisited_area_id)

## 未訪問エリア内(レビュー and [lat or lng])ありスポット
unvisited_spot_list = []
for i in range(len(vis_cate)):
    select_unvisited_spot = "SELECT DISTINCT id,name,lat,lng,area_id,review,url,description,category1 FROM spot_mst2 WHERE area_id IN {area} AND review!=0 AND (lat!=0 or lng!=0) AND id NOT IN {vis} AND name NOT LIKE '%レンタ%' AND category1 LIKE '%{vis_cate}%' ORDER BY review DESC limit 12;".format(area=tuple(unvisited_area_id_list),vis=tuple(visited_spot_id_list),vis_cate=vis_cate[i])
    tmp = myp_other.spot_or_reviewlist(select_unvisited_spot)
    unvisited_spot_list.append(tmp)

unvisited_spot_list_map_l,unvisited_spot_list_map_t,unvisited_spot_list_map_p = [],[],[]
for i in range(len(unvisited_spot_list)):
    n = 0
    unvisited_spot_list_map_p.extend(unvisited_spot_list[i][n:n+3])
    n = 3
    unvisited_spot_list_map_l.extend(unvisited_spot_list[i][n:n+3])
    n = 6
    unvisited_spot_list_map_t.extend(unvisited_spot_list[i][n:n+3])
if len(unvisited_spot_list_map_l) != len(unvisited_spot_list_map_t) or len(unvisited_spot_list_map_t) != len(unvisited_spot_list_map_p) or len(unvisited_spot_list_map_l) != len(unvisited_spot_list_map_p):
    a = min([len(unvisited_spot_list_map_l),len(unvisited_spot_list_map_t),len(unvisited_spot_list_map_p)])
    unvisited_spot_list_map_p = unvisited_spot_list_map_p[:a]
    unvisited_spot_list_map_l = unvisited_spot_list_map_l[:a]
    unvisited_spot_list_map_t = unvisited_spot_list_map_t[:a]

## 未訪問エリア内スポットIDリスト
unvisited_spot_id_list = []
## GoogleMapの表示
unvis_spot_id,unvis_name,unvis_lat,unvis_lng,unvis_url,unvis_description = [],[],[],[],[],[]
for i in range(len(unvisited_spot_list_map_p)):
    for j in range(len(unvisited_spot_list_map_p[i])):
        unvisited_spot_id_list.append(unvisited_spot_list_map_p[i][j][0])
        if unvisited_spot_list_map_p[i][j][2]!=0 and unvisited_spot_list_map_p[i][j][3]!=0:
            unvis_spot_id.append(unvisited_spot_list_map_p[i][j][0])
            unvis_name.append(unvisited_spot_list_map_p[i][j][1])
            unvis_lat.append(str(unvisited_spot_list_map_p[i][j][2]))
            unvis_lng.append(str(unvisited_spot_list_map_p[i][j][3]))
            unvis_url.append(str(unvisited_spot_list_map_p[i][j][6]))
            unvis_description.append(str(unvisited_spot_list_map_p[i][j][7]))
        else:
            continue


############################################################
############################################################
## 既訪問スポットベクトル
select_visited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(visited_spot_id_list))
## 特徴ベクトル
visited_spot_vectors = myp_doc_rec.spot_list(select_visited_spot_vectors)
## 特徴ベクトル差分
visited_spot_vectors_doc = myp_doc_rec.doc2vec_feature(visited_spot_vectors)

## 未訪問スポットベクトル
select_unvisited_spot_vectors = "SELECT * FROM spot_vectors_name WHERE id IN {};".format(tuple(unvisited_spot_id_list))
unvisited_spot_vectors = myp_doc_rec.spot_list(select_unvisited_spot_vectors)
unvisited_spot_vectors_doc = myp_doc_rec.doc2vec_feature(unvisited_spot_vectors)

############################################################
## 相対的な特徴（差分ベクトル）
############################################################
## 既訪問と未訪問スポットベクトルの差の類似度計算(1番高い)
visited_spot_name_all,unvisited_spot_name_all = [],[]
visited_spot_review_all,unvisited_spot_review_all = [],[]
for i in range(len(visited_spot_vectors_doc)):
    visited_spot_name_all.append(visited_spot_vectors_doc[i][0])
    visited_spot_review_all.append(visited_spot_vectors_doc[i][1])
for i in range(len(unvisited_spot_vectors_doc)):
    unvisited_spot_name_all.append(unvisited_spot_vectors_doc[i][0])
    unvisited_spot_review_all.append(unvisited_spot_vectors_doc[i][1])
result_UtoV_top = myp_doc_rec.recommend_all(visited_spot_name_all,unvisited_spot_name_all,visited_spot_review_all,unvisited_spot_review_all)

## 類似度高い順でソート
result_UtoV_top.sort(key=lambda x:x[1][1],reverse=True)

## 既訪問スポットの単語に重み付け
select_visited_spot_reviews = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(visited_spot_id_list))
visited_spot_reviews = myp_tfidf.spot_list_tfidf(select_visited_spot_reviews)
# visited_tfidf = myp_tfidf.tfidf(visited_spot_reviews)
visited_reviews = []
visited_reviews.extend(visited_spot_reviews)
dictionary = corpora.Dictionary(visited_spot_reviews)
corpus = list(map(dictionary.doc2bow,visited_reviews))
test_model = models.TfidfModel(corpus,wglobal=new_idf,normalize=False)
corpus_tfidf = list(test_model[corpus])
visited_tfidf = myp_tfidf.tfidf_res(dictionary,corpus_tfidf)

## 未訪問スポットの単語に重み付け
select_unvisited_spot_reviews = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE spot_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(unvisited_spot_id_list))
unvisited_spot_reviews = myp_tfidf.spot_list_tfidf(select_unvisited_spot_reviews)
# unvisited_tfidf = myp_tfidf.tfidf(unvisited_spot_reviews)
unvisited_reviews = []
unvisited_reviews.extend(unvisited_spot_reviews)
dictionary = corpora.Dictionary(unvisited_spot_reviews)
corpus = list(map(dictionary.doc2bow,unvisited_reviews))
test_model = models.TfidfModel(corpus,wglobal=new_idf,normalize=False)
corpus_tfidf = list(test_model[corpus])
unvisited_tfidf = myp_tfidf.tfidf_res(dictionary,corpus_tfidf)

bytesymbols = re.compile("[!-/:*-@[-`{-~\d]") ## 半角記号，数字\d
## 調和平均
def Word_Harmonic(all_spot,result):
    ## 一番類似するスポットの特徴語top10を求める
    all_data,top10 = [],[]
    for i in tqdm(range(len(all_spot[0]))):
        temp = []
        same_word = list(set([all_spot[0][i][j][0] for j in range(len(all_spot[0][i]))]) & set([all_spot[1][i][j][0] for j in range(len(all_spot[1][i]))]))
        for sw in same_word:
            un = [j for j in range(len(all_spot[0][i])) if all_spot[0][i][j][0] == sw][0]
            vi = [j for j in range(len(all_spot[1][i])) if all_spot[1][i][j][0] == sw][0]
            if len(all_spot[0][i][un][0])>1 and re.search(bytesymbols,all_spot[0][i][un][0])==None:
                 if all_spot[1][i][vi][1]==0 or all_spot[0][i][un][1]==0:
                     temp.append([all_spot[0][i][un][0],0])
                 else:
                     temp.append([all_spot[0][i][un][0],(2/(1/all_spot[0][i][un][1]+1/all_spot[1][i][vi][1]))])
        all_data.append(temp)
        all_data[i].sort(key=lambda x:x[1],reverse=True)## 降順ソート
        tmp = []
        for j in range(len(all_data[i])):
            tmp.append(all_data[i][j][0])
        # ## 未訪問，既訪問，類似度，単語(最初の10個まで)
        top10.append([result[i][0],result[i][1][0],result[i][1][1],tmp[:15]])
        # temp.append(["__finish__",0])
        # all_data.append(temp)
        # all_data[i].sort(key=lambda x:x[1],reverse=True)
        # ## 対応付け(調和平均>=0)のキーワードを取り出す
        # for a in range(len(all_data[i])):
        #     if all_data[i][a][1] <= 0:
        #         tmp = []
        #         for j in range(len(all_data[i][:a])):
        #             tmp.append(all_data[i][j][0])
        #         top10.append([result[i][0],result[i][1][0],result[i][1][1],tmp])
        #         break
    return top10

def Sort_TFIDF_UtoV(vis_tfidf,unvis_tfidf,vis_spot_name,unvis_spot_name,result):
    ## TFIDFの結果にスポット名を追加
    vis_spot,unvis_spot = [],[]
    for i in range(len(vis_spot_name)):
        vis_spot.append([vis_spot_name[i],vis_tfidf[i]])
    for i in range(len(unvis_spot_name)):
        unvis_spot.append([unvis_spot_name[i],unvis_tfidf[i]])
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
    top_harmonic = Word_Harmonic(all_spot,result)
    return top_harmonic

## 既訪問と未訪問スポット特徴語TOP10(算術平均，調和平均)
top10_harmonic = Sort_TFIDF_UtoV(visited_tfidf,unvisited_tfidf,visited_spot_name_all,unvisited_spot_name_all,result_UtoV_top)

print("従来手法",top10_harmonic, file=sys.stderr)
print("\n================================\n", file=sys.stderr)



############################################################
## 既訪問スポット 階層的クラスタリング
############################################################
start_time = time.time()
## 既訪問スポットのレビューベクトルを得る
select_vis_spot_vectors = "SELECT * FROM review_vectors_spotname WHERE spot_id IN ({})".format(str(vis_spot_id)[1:-1])
vis_review_vectors = myp_other.review_id_and_vectors_list(select_vis_spot_vectors)

threshold = 0.65 ## クラスタ分けの閾値
vis_res = myp_cluster.kaisoClustering(select_vis_spot_vectors,threshold)
## 階層的クラスタリングの結果から，各クラスタのスコアを求める
vis_score_dic = myp_cluster.clusterScorering(vis_res, len(vis_spot_id))
# print("vis_score_dic",vis_score_dic, file=sys.stderr)

vis_reviews = []
for i in range(len(vis_score_dic)):
    select_review = "SELECT wakachi_neologd5 FROM review_all WHERE review_id IN ({}) ;".format(str(vis_score_dic[i][2])[1:-1])
    cur.execute(select_review)
    tmp = []
    for i in cur:
        tmp.extend(list(i)[0].split())
    vis_reviews.append(tmp) ## 全クラスタのクラスタ毎のレビューの分かち書きデータ

## TFIDFによる特徴語抽出
visited_tfidf = myp_tfidf.tfidf(vis_reviews)
visited_tfidf_set = []
for i in range(len(vis_score_dic)):
    visited_tfidf_set.append([vis_score_dic[i][0],visited_tfidf[i]])

def tfidf_set(data,vis_score_dic):
    tfidf = []
    for i in range(len(data)):
        tfidf.append([data[i][0],sorted(data[i][1],key=lambda x:x[1],reverse=True)])
    word = []
    for i in range(len(tfidf)):
        tmp = []
        for j in range(len(tfidf[i][1])):
            tmp.append(tfidf[i][1][j][0])
        ## 各クラスタ提示キーワード：上位10件
        word.append([tfidf[i][0],tmp[:50]])
    # for i in range(len(vis_score_dic)):
    #     vis_score_dic[i][2] = [int(n) for n in vis_score_dic[i][2]]
    return word

word = tfidf_set(visited_tfidf_set[:5],vis_score_dic[:5])
print("クラスタ特徴語：\n",word, file=sys.stderr)

use_word = []
for i in range(len(vis_score_dic)):
    tmp = []
    if vis_score_dic[i][1] >= 0.1 and len(use_word)<=3:
        use_word.append(word[i])
# print(use_word, file=sys.stderr)

############################################################
## 平均類以度
############################################################
def cos_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

## 既訪問スポットのレビューベクトルを得る(クラスタのスコア値は0.1以上)
vis_review_vectors_clu = []
for i in range(len(vis_score_dic)):
    tmp = []
    if vis_score_dic[i][1] >= 0.1:
        print("クラスタ番号：",vis_score_dic[i][0],"クラスタ値：",vis_score_dic[i][1], file=sys.stderr)
        select_vis_spot_vectors = "SELECT * FROM review_vectors_spotname WHERE id IN {};".format(tuple(vis_score_dic[i][2]))
        cur.execute(select_vis_spot_vectors)
        review_set = []
        for j in cur:
            review_set.append([j[0],list(j[1:-2])])
        tmp.extend(review_set)
        vis_review_vectors_clu.append([vis_score_dic[i][0],vis_score_dic[i][1],tmp])
# print("vis_score_dic",vis_score_dic, file=sys.stderr)
# print("vis_review_vectors_clu",vis_review_vectors_clu, file=sys.stderr)

## 未訪問スポットのレビューベクトルを得る
select_unvis_spot_vectors = "SELECT * FROM review_vectors_spotname WHERE spot_id IN ({});".format(str(unvis_spot_id)[1:-1])
unvis_review_vectors = myp_other.review_id_and_vectors_list(select_unvis_spot_vectors)


## 未訪問スポットのレビューベクトルはどのクラスタに属するか（計算時間大体3分~5分）
unvis_review_groupby_vis_cluster = []
for i in tqdm(range(len(unvis_review_vectors))): ## 未訪問エリアのレビュー
    unvis_review_avg = []
    for j in range(len(vis_review_vectors_clu)): ## 作成したクラスタ
        tmp = []
        for k in range(len(vis_review_vectors_clu[j][2])): ## クラスタに含まれているレビュー
            tmp.append(cos_sim(np.array(unvis_review_vectors[i][1]),np.array(vis_review_vectors_clu[j][2][k][1])))
        unvis_review_avg.append([vis_review_vectors_clu[j][0],np.mean(np.array(tmp))])
    ## 類似度が一番大きいのクラスタを出す
    short = max(unvis_review_avg,key=lambda x:x[1])
    if short[1] >= 0.125:
        unvis_review_groupby_vis_cluster.append([short[0],unvis_review_vectors[i][0]])
# print("unvis_review_groupby_vis_cluster",unvis_review_groupby_vis_cluster, file=sys.stderr)

dic_unvis_review_groupby_vis_cluster_id = defaultdict(list)
for i in unvis_review_groupby_vis_cluster:
    dic_unvis_review_groupby_vis_cluster_id[i[0]].append(i[1])
dic_unvis_r_key = list(dic_unvis_review_groupby_vis_cluster_id.keys()) ## 全キー
## クラスタに属する検査結果レビュー
# print("dic_unvis_review_groupby_vis_cluster_id", dic_unvis_review_groupby_vis_cluster_id, file=sys.stderr)

############################################################
## 既訪問スポットと未訪問スポットの計算 ベクトル総当たり
############################################################
## クラスタに属する未訪問スポットレビューベクトル
unvis_dic_all = defaultdict(list)
for i in range(len(dic_unvis_review_groupby_vis_cluster_id)):
    select_tmp = "SELECT * FROM review_vectors_spotname WHERE id IN {};".format(tuple(dic_unvis_review_groupby_vis_cluster_id[dic_unvis_r_key[i]]))
    cur.execute(select_tmp)
    unvis_dic = defaultdict(list)
    for j in cur:
        unvis_dic[j[-1]].append(list(j[1:-2]))
    # print("unvis_dic",i ,unvis_dic, file=sys.stderr)
    unvis_dic_all[dic_unvis_r_key[i]].extend(list(unvis_dic.items()))
# print("unvis_dic_all", unvis_dic_all, file=sys.stderr)

# ## クラスタに属する既訪問スポットレビューベクトル
vis_dic_all = defaultdict(list)
for i in range(len(vis_review_vectors_clu)):
    select_tmp = "SELECT * FROM review_vectors_spotname WHERE id IN {};".format(tuple(vis_score_dic[i][2]))
    cur.execute(select_tmp)
    vis_dic = defaultdict(list)
    for j in cur:
        vis_dic[j[-1]].append(list(j[1:-2]))
    # print("vis_dic",i ,vis_dic, file=sys.stderr)
    vis_dic_all[vis_review_vectors_clu[i][0]].extend(list(vis_dic.items()))
# print("vis_dic_all", vis_dic_all, file=sys.stderr)

## ベクトル総当たり
unvis_vis_set_clu = []
unvis_dic_all_keys = list(unvis_dic_all.keys())
vis_dic_all_keys = list(vis_dic_all.keys())
for i in tqdm(range(len(unvis_dic_all_keys))):
    unvis_tmp = dict(unvis_dic_all[unvis_dic_all_keys[i]]) ## クラスタ
    unvis_keys = list(unvis_tmp.keys()) ## 検索結果スポット
    vis_tmp = dict(vis_dic_all[unvis_dic_all_keys[i]])
    vis_keys = list(vis_tmp.keys())
    unvis_vis_one_set = []
    for j in range(len(unvis_keys)):
        if len(unvis_tmp[unvis_keys[j]]) <= 5: ## レビュー数5以下の検索結果を無視
            # print("pass",unvis_dic_all_keys[i],unvis_keys[j],len(unvis_tmp[unvis_keys[j]]), file=sys.stderr)
            pass
        else:
            for k in range(len(vis_keys)):
                if len(vis_tmp[vis_keys[k]]) <= 5: ## レビュー数5以下の検索結果を無視
                    pass
                else:
                    tmp2 = []
                    for jx in range(len(unvis_tmp[unvis_keys[j]])):
                        tmp = []
                        for kx in range(len(vis_tmp[vis_keys[k]])):
                            tmp.append(cos_sim(unvis_tmp[unvis_keys[j]][jx],vis_tmp[vis_keys[k]][kx]))
                        tmp2.extend(tmp)
                    unvis_vis_one_set.append([unvis_keys[j],vis_keys[k],np.mean(np.array(tmp2))])
    tmp3,main_tmp = [],[]
    for j in range(len(unvis_vis_one_set)):
        try:
            if unvis_vis_one_set[j][0] == unvis_vis_one_set[j+1][0] and unvis_vis_one_set[j][1] == unvis_vis_one_set[j+1][1]:
                tmp3.append(unvis_vis_one_set[j][2])
            else:
                tmp3.append(unvis_vis_one_set[j][2])
                main_tmp.append([unvis_dic_all_keys[i],unvis_vis_one_set[j][0],unvis_vis_one_set[j][1],np.mean(np.array(tmp3))])
                tmp3 = []
        except IndexError:
            tmp3.append(unvis_vis_one_set[j][2])
            main_tmp.append([unvis_dic_all_keys[i],unvis_vis_one_set[j][0],unvis_vis_one_set[j][1],np.mean(np.array(tmp3))])
    unvis_vis_set_clu.append([unvis_dic_all_keys[i],main_tmp])
# print("unvis_vis_set_clu", unvis_vis_set_clu, file=sys.stderr)

## spot_idをスポット名に変更
for i in range(len(unvis_vis_set_clu)):
    for j in range(len(unvis_vis_set_clu[i][1])):
        tmp = "SELECT name FROM spot_mst2 WHERE id =  '{}';".format(unvis_vis_set_clu[i][1][j][1])
        cur.execute(tmp)
        unvis_vis_set_clu[i][1][j][1] = cur.fetchone()[0]
        tmp2 = "SELECT name FROM spot_mst2 WHERE id =  '{}';".format(unvis_vis_set_clu[i][1][j][2])
        cur.execute(tmp2)
        unvis_vis_set_clu[i][1][j][2] = cur.fetchone()[0]

## クラスタ毎ソート
for i in range(len(unvis_vis_set_clu)):
    unvis_vis_set_clu[i][1] = sorted(unvis_vis_set_clu[i][1],key=lambda x:x[3],reverse=True)
# print("\nクラスタ結果", unvis_vis_set_clu, file=sys.stderr)

## ターミナルに表示用
cmd = []
for i in range(len(unvis_vis_set_clu)):
    for j in range(len(unvis_vis_set_clu[i][1])):
        cmd.append(unvis_vis_set_clu[i][1][j])
cmd.sort(key=lambda x:x[3],reverse=True)
print("\nクラスタ結果", cmd, file=sys.stderr)

use_clu_num = []
for i in range(len(unvis_vis_set_clu)):
    use_clu_num.append(unvis_vis_set_clu[i][0])
    print("\nクラスタ番号：",unvis_vis_set_clu[i][0],"対応付け：",unvis_vis_set_clu[i][1][:5], file=sys.stderr)

# print(use_clu_num, file=sys.stderr)
use_vis_review = []
for i in range(len(use_clu_num)):
    for j in range(len(vis_score_dic)):
        if use_clu_num[i] == vis_score_dic[j][0]:
            use_vis_review.append(vis_score_dic[j])
# print("use_vis_review",use_vis_review, file=sys.stderr) ## クラスタに属する既訪問レビュー

def mean_clu_same(use_w,res):
    use_word = dict(use_w)
    data_set = []
    for i in range(len(res)):
        for j in range(len(res[i][1])):
            tmp = []
            for k in range(len(res[i][1][j][4])):
                if res[i][1][j][4][k][0] in use_word[res[i][0]]:
                    tmp.append(res[i][1][j][4][k][0])
            if len(tmp) == 0:
                data_set.append([res[i][1][j][:3],"no word"])
            else:
                data_set.append([res[i][1][j][0],res[i][1][j][1],res[i][1][j][2],tmp])
    return data_set

############################################################
## 既訪問スポットと未訪問スポットの特徴語抽出（既訪問スポットの特徴語は，RCfからTFを，クラスタ関係なく既訪問スポットをdとしたIDF．検索結果は，RCfをRCu，IDFも同様に変更したもの．(既訪問：IDFの分子の全文書数=全既訪問スポットの数．検索結果：IDFの分子の全文書数=全検索結果スポットの数．))
############################################################
print("\n================\n IDF範囲：既訪問or検索結果スポット \n================", file=sys.stderr)
# print("visited_spot_reviews",visited_spot_reviews, file=sys.stderr)
# print("unvisited_spot_reviews",unvisited_spot_reviews, file=sys.stderr)
visited_reviews = []
visited_spot_count = []
## クラスタに属する既訪問スポットレビューの単語に重みつけ
for i in range(len(vis_review_vectors_clu)):
    tmp = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE review_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(use_vis_review[i][2]))
    everyspot = myp_tfidf.spot_list_tfidf(tmp)
    visited_reviews.extend(everyspot)
    visited_spot_count.append([use_vis_review[i][0],len(visited_reviews)])

dictionary = corpora.Dictionary(visited_spot_reviews)
vis_length = len(visited_spot_reviews) ##全既訪問スポット数
visited_tfidf_tmp = myp_tfidf.tfidf_res1(dictionary,vis_length,visited_reviews)

# corpus = list(map(dictionary.doc2bow,visited_reviews))
# test_model = models.TfidfModel(corpus,wglobal=new_idf,normalize=False)
# corpus_tfidf = list(test_model[corpus])
# visited_tfidf_tmp = myp_tfidf.tfidf_res(dictionary,corpus_tfidf)

visited_tfidf = []
s = 0
for i in range(len(visited_spot_count)):
    visited_tfidf.append([visited_spot_count[i][0],visited_tfidf_tmp[s:visited_spot_count[i][1]]])
    s = visited_spot_count[i][1]
# print("visited_tfidf",visited_tfidf, file=sys.stderr)

## TFIDFの結果にスポット名を追加
visited_spot_name_all,visited_spot_review_num = [],[]
for i in range(len(vis_review_vectors_clu)):
    tmp_name_all = []
    cur.execute("SELECT name,count(name) FROM review_all WHERE review_id IN {} GROUP BY name;".format(tuple(use_vis_review[i][2])))
    for j in cur.fetchall():
        tmp_name_all.append(j[0])
    # print(use_vis_review[i], file=sys.stderr)
    # print(tmp_name_all, file=sys.stderr)
    visited_spot_name_all.append([use_vis_review[i][0],tmp_name_all])
print("\nvisited_spot_name_all",visited_spot_name_all, file=sys.stderr)

vis_spot_clu = defaultdict(list)
for i in range(len(visited_spot_name_all)):
    for j in range(len(visited_spot_name_all[i][1])):
        vis_spot_clu[visited_spot_name_all[i][0]].append([visited_spot_name_all[i][1][j],visited_tfidf[i][1][j]])

################################################################
unvisited_reviews = []
unvisited_spot_count = []
## クラスタに属する未訪問スポットレビューの単語に重みつけ
for i in range(len(dic_unvis_review_groupby_vis_cluster_id)):
    tmp = "SELECT spot_id,wakachi_neologd5 FROM review_all WHERE review_id IN {} GROUP BY spot_id,wakachi_neologd5;".format(tuple(dic_unvis_review_groupby_vis_cluster_id[dic_unvis_r_key[i]]))
    unvisited_reviews.extend(myp_tfidf.spot_list_tfidf(tmp))
    unvisited_spot_count.append([dic_unvis_r_key[i],len(unvisited_reviews)])
# print("unvisited_reviews",unvisited_reviews, file=sys.stderr)

del dictionary
dictionary = corpora.Dictionary(unvisited_spot_reviews)
unvis_length = len(unvisited_spot_reviews) ##全検索結果スポット数
unvisited_tfidf_tmp = myp_tfidf.tfidf_res1(dictionary,unvis_length,unvisited_reviews)

# corpus = list(map(dictionary.doc2bow,unvisited_reviews))
# test_model = models.TfidfModel(corpus,wglobal=new_idf,normalize=False)
# corpus_tfidf = list(test_model[corpus])
# unvisited_tfidf_tmp = myp_tfidf.tfidf_res(dictionary,corpus_tfidf)

unvisited_tfidf = []
s = 0
for i in range(len(unvisited_spot_count)):
    unvisited_tfidf.append([unvisited_spot_count[i][0],unvisited_tfidf_tmp[s:unvisited_spot_count[i][1]]])
    s = unvisited_spot_count[i][1]
# print("unvisited_tfidf",unvisited_tfidf, file=sys.stderr)

## TFIDFの結果にスポット名を追加
unvisited_spot_name_all,unvisited_spot_review_num = [],[]
for i in range(len(dic_unvis_review_groupby_vis_cluster_id)):
    tmp_name_all = []
    cur.execute("SELECT name,count(name) FROM review_all WHERE review_id IN {} GROUP BY name;".format(tuple(dic_unvis_review_groupby_vis_cluster_id[dic_unvis_r_key[i]])))
    for j in cur.fetchall():
        tmp_name_all.append(j[0])
    unvisited_spot_name_all.append([dic_unvis_r_key[i],tmp_name_all])
print("\nunvisited_spot_name_all", unvisited_spot_name_all, file=sys.stderr)

unvis_spot_clu = defaultdict(list)
for i in range(len(unvisited_spot_name_all)):
    for j in range(len(unvisited_spot_name_all[i][1])):
        unvis_spot_clu[unvisited_spot_name_all[i][0]].append([unvisited_spot_name_all[i][1][j],unvisited_tfidf[i][1][j]])

## TFIDFによるコサイン類似度計算
# print("vis_spot_clu",vis_spot_clu, file=sys.stderr)
# print("unvis_spot_clu",unvis_spot_clu, file=sys.stderr)
sctfidf = myp_cos_tfidf.SimCalculator()
result_cos_tfidf = []
for i in vis_spot_clu:
    tmp = []
    for j in range(len(vis_spot_clu[i])):
        for k in range(len(unvis_spot_clu[i])):
            cos_tfidf = sctfidf.sim_cos(vis_spot_clu[i][j],unvis_spot_clu[i][k])
            tmp.append([unvis_spot_clu[i][k][0],vis_spot_clu[i][j][0],cos_tfidf])
    result_cos_tfidf.append([i,tmp])
# print("result_cos_tfidf", result_cos_tfidf, file=sys.stderr)

res1 = []
for i in range(len(result_cos_tfidf)):
    if result_cos_tfidf == []:
        pass
    else:
        tmp = myp_feature.sort_tfidf_UtoV_tfidfcos(result_cos_tfidf[i][0],visited_tfidf[i][1],unvisited_tfidf[i][1],visited_spot_name_all[i][1],unvisited_spot_name_all[i][1],result_cos_tfidf[i][1])
        res1.append([result_cos_tfidf[i][0],tmp])
print("対応付けキーワード",res1, file=sys.stderr)

# result1 = mean_clu_same(use_word,res1)
# print("対応付けキーワード(調和平均>=0 & クラスタの上位50個の単語に入っている)\n",result1, file=sys.stderr)


############################################################
## 既訪問スポットと未訪問スポットの特徴語抽出（既訪問スポットの特徴語は，RCfからTFを，各クラスタをdとしたIDF．検索結果に関しては以下略．(既訪問，検索結果：IDFの分子の全文書数 = 全！！クラスタ数))
############################################################
print("\n================\n IDF範囲：全クラスタ数 \n================", file=sys.stderr)
del dictionary
dictionary = corpora.Dictionary(vis_reviews)
vis_allclu_length = len(vis_reviews) ##全クラスタ数
visited_tfidf_tmp = myp_tfidf.tfidf_res2(dictionary,vis_allclu_length,visited_reviews)

# corpus = list(map(dictionary.doc2bow,visited_reviews))
# test_model = models.TfidfModel(corpus,wglobal=new_idf,normalize=False)
# corpus_tfidf = list(test_model[corpus])
# visited_tfidf_tmp = myp_tfidf.tfidf_res(dictionary,corpus_tfidf)

visited_tfidf = []
s = 0
for i in range(len(visited_spot_count)):
    visited_tfidf.append([visited_spot_count[i][0],visited_tfidf_tmp[s:visited_spot_count[i][1]]])
    s = visited_spot_count[i][1]
# print("visited_tfidf",visited_tfidf, file=sys.stderr)

## TFIDFの結果にスポット名を追加
visited_spot_name_all,visited_spot_review_num = [],[]
for i in range(len(vis_review_vectors_clu)):
    tmp_name_all = []
    cur.execute("SELECT name,count(name) FROM review_all WHERE review_id IN {} GROUP BY name;".format(tuple(use_vis_review[i][2])))
    for j in cur.fetchall():
        tmp_name_all.append(j[0])
    # print(use_vis_review[i], file=sys.stderr)
    # print(tmp_name_all, file=sys.stderr)
    visited_spot_name_all.append([use_vis_review[i][0],tmp_name_all])
print("\nvisited_spot_name_all",visited_spot_name_all, file=sys.stderr)

vis_spot_clu = defaultdict(list)
for i in range(len(visited_spot_name_all)):
    for j in range(len(visited_spot_name_all[i][1])):
        vis_spot_clu[visited_spot_name_all[i][0]].append([visited_spot_name_all[i][1][j],visited_tfidf[i][1][j]])

################################################################
unvisited_tfidf_tmp = myp_tfidf.tfidf_res2(dictionary,vis_allclu_length,unvisited_reviews)

# corpus = list(map(dictionary.doc2bow,unvisited_reviews))
# test_model = models.TfidfModel(corpus,wglobal=new_idf,normalize=False)
# corpus_tfidf = list(test_model[corpus])
# unvisited_tfidf_tmp = myp_tfidf.tfidf_res(dictionary,corpus_tfidf)

unvisited_tfidf = []
s = 0
for i in range(len(unvisited_spot_count)):
    unvisited_tfidf.append([unvisited_spot_count[i][0],unvisited_tfidf_tmp[s:unvisited_spot_count[i][1]]])
    s = unvisited_spot_count[i][1]
# print("unvisited_tfidf",unvisited_tfidf, file=sys.stderr)

## TFIDFの結果にスポット名を追加
unvisited_spot_name_all,unvisited_spot_review_num = [],[]
for i in range(len(dic_unvis_review_groupby_vis_cluster_id)):
    tmp_name_all = []
    cur.execute("SELECT name,count(name) FROM review_all WHERE review_id IN {} GROUP BY name;".format(tuple(dic_unvis_review_groupby_vis_cluster_id[dic_unvis_r_key[i]])))
    for j in cur.fetchall():
        tmp_name_all.append(j[0])
    unvisited_spot_name_all.append([dic_unvis_r_key[i],tmp_name_all])
print("\nunvisited_spot_name_all", unvisited_spot_name_all, file=sys.stderr)

unvis_spot_clu = defaultdict(list)
for i in range(len(unvisited_spot_name_all)):
    for j in range(len(unvisited_spot_name_all[i][1])):
        unvis_spot_clu[unvisited_spot_name_all[i][0]].append([unvisited_spot_name_all[i][1][j],unvisited_tfidf[i][1][j]])

## TFIDFによるコサイン類似度計算
# print("vis_spot_clu",vis_spot_clu, file=sys.stderr)
# print("unvis_spot_clu",unvis_spot_clu, file=sys.stderr)
sctfidf = myp_cos_tfidf.SimCalculator()
result_cos_tfidf = []
for i in vis_spot_clu:
    tmp = []
    for j in range(len(vis_spot_clu[i])):
        for k in range(len(unvis_spot_clu[i])):
            cos_tfidf = sctfidf.sim_cos(vis_spot_clu[i][j],unvis_spot_clu[i][k])
            tmp.append([unvis_spot_clu[i][k][0],vis_spot_clu[i][j][0],cos_tfidf])
    result_cos_tfidf.append([i,tmp])
# print("result_cos_tfidf", result_cos_tfidf, file=sys.stderr)

res2 = []
for i in range(len(result_cos_tfidf)):
    if result_cos_tfidf == []:
        pass
    else:
        tmp = myp_feature.sort_tfidf_UtoV_tfidfcos(result_cos_tfidf[i][0],visited_tfidf[i][1],unvisited_tfidf[i][1],visited_spot_name_all[i][1],unvisited_spot_name_all[i][1],result_cos_tfidf[i][1])
        res2.append([result_cos_tfidf[i][0],tmp])
print("対応付けキーワード", res2, file=sys.stderr)

# result2 = mean_clu_same(use_word,res2)
# print("対応付けキーワード(調和平均>=0 & クラスタの上位50個の単語に入っている)\n",result2, file=sys.stderr)

print("処理時間：{} sec".format(time.time() - start_time), file=sys.stderr)
