from tqdm import tqdm

## 平均以上 or 0.01以上
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
                    temp.append([set[0][i][j][0],abs(set[0][i][j][1]-set[1][i][k][1])])
                    # ,set[0][i][j][1],set[1][i][k][1]]) ## 元の値をみる
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
                if set[0][i][j][0]==set[1][i][k][0] and set[0][i][j][1]>=unvisited_mean[i] and set[1][i][k][1]>=visited_mean[i]:
                # if set[0][i][j][0]==set[1][i][k][0] and set[0][i][j][1]>=0.01 and set[1][i][k][1]>=0.01:
                    temp.append([set[0][i][j][0],abs(set[0][i][j][1]-set[1][i][k][1])])
                    # ,set[0][i][j][1],set[1][i][k][1]]) ## 元の値をみる
        all.append(temp)
        all[i].sort(key=lambda x:x[1]) ## 昇順ソート(0に近い程が良い)
        top10.append([result[i][0],result[i][1][0],all[i][:10]])
    return top10
