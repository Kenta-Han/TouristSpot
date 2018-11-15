from tqdm import tqdm
import re

bytesymbols = re.compile("[!-/:-@[-`{-~\d]") ## 半角記号，数字\d
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
                    temp.append([set[0][i][j][0],abs(2/(1/set[0][i][j][1]+1/set[1][i][k][1]))])
        all.append(temp)
        all[i].sort(key=lambda x:x[1],reverse=True)## 降順ソート
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
                    temp.append([set[0][i][j][0],abs(2/(1/set[0][i][j][1]+1/set[1][i][k][1]))])
        all.append(temp)
        all[i].sort(key=lambda x:x[1],reverse=True) ## 降順ソート
        top10.append([result[i][0],result[i][1][0],result[i][1][1],all[i][:10]])
    return top10
