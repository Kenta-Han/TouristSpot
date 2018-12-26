from tqdm import tqdm
import re
import random

bytesymbols = re.compile("[!-/:*-@[-`{-~\d]") ## 半角記号，数字\d

def Word_Random(all_spot,result):
    ## 既訪問と未訪問が共に出現する単語
    all_data,top10 = [],[]
    # for i in tqdm(range(len(all_spot[0]))):
    #     temp = []
    #     same_word = list(set([all_spot[0][i][j][0] for j in range(len(all_spot[0][i]))]) & set([all_spot[1][i][j][0] for j in range(len(all_spot[1][i]))]))
    #     for sw in same_word:
    #         un = [j for j in range(len(all_spot[0][i])) if all_spot[0][i][j][0] == sw][0]
    #         vi = [j for j in range(len(all_spot[1][i])) if all_spot[1][i][j][0] == sw][0]
    #         if len(all_spot[0][i][un][0])>1 and re.search(bytesymbols,all_spot[0][i][un][0])==None:
    #              temp.append(all_spot[0][i][un][0])
    #     all_data.append(temp)
    #     random.shuffle(all_data[i])
    #     # ## 未訪問，既訪問，類似度，単語(最初の10個まで)
    #     top10.append([result[i][0],result[i][1][0],result[i][1][1],all_data[i][:5]])
    ## 既訪問と未訪問が共に出現する単語でなくでも大丈夫
    for i in range(len(all_spot[0])):
        temp1,temp2 = [],[]
        for j in range(len(all_spot[0][i])):
            if len(all_spot[0][i][j][0])>1 and re.search(bytesymbols,all_spot[0][i][j][0])==None:
                temp1.append(all_spot[0][i][j][0])
        for k in range(len(all_spot[1][i])):
            if len(all_spot[1][i][k][0])>1 and re.search(bytesymbols,all_spot[1][i][k][0])==None:
                temp2.append(all_spot[1][i][k][0])
        all_data.append(temp1+temp2)
        # random.shuffle(all_data[i]) ## ランダムソート
        word = random.sample(all_data[i],5) ## ランダム5つ取り出す
        top10.append([result[i][0],result[i][1][0],result[i][1][1],word])
    return top10

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
                 temp.append([all_spot[0][i][un][0],abs(2/(1/all_spot[0][i][un][1]+1/all_spot[1][i][vi][1]))])
        all_data.append(temp)
        all_data[i].sort(key=lambda x:x[1],reverse=True)## 降順ソート
        # ## 未訪問，既訪問，類似度，単語(最初の10個まで)
        top10.append([result[i][0],result[i][1][0],result[i][1][1],all_data[i][:5]])
    return top10

## 調和平均 差が小値が大，差が大値が小 → 値が大の方が良い(昇順後ろから10個)
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
    # all_data,top10 = [],[]
    # for i in tqdm(range(len(all_spot[0]))):
    #     temp = []
    #     same_word = list(set([all_spot[0][i][j][0] for j in range(len(all_spot[0][i]))]) & set([all_spot[1][i][j][0] for j in range(len(all_spot[1][i]))]))
    #     for sw in same_word:
    #         un = [j for j in range(len(all_spot[0][i])) if all_spot[0][i][j][0] == sw][0]
    #         vi = [j for j in range(len(all_spot[1][i])) if all_spot[1][i][j][0] == sw][0]
    #         if len(all_spot[0][i][un][0])>1 and re.search(bytesymbols,all_spot[0][i][un][0])==None:
    #              temp.append([all_spot[0][i][un][0],abs(2/(1/all_spot[0][i][un][1]+1/all_spot[1][i][vi][1]))])
    #     all_data.append(temp)
    #     word_r = random.sample(all_data, 5)
    #     word_h = all_data[i].sort(key=lambda x:x[1],reverse=True)## 降順ソート
    #     # ## 未訪問，既訪問，類似度，単語(最初の10個まで)
    #     top10.append([result[i][0],result[i][1][0],result[i][1][1],word_r,word_h])
    # return top10
    top_random = Word_Random(all_spot,result)
    top_harmonic = Word_Harmonic(all_spot,result)
    return top_random,top_harmonic
