from tqdm import tqdm
import re

bytesymbols = re.compile("[!-/:*-@[-`{-~\d]") ## 半角記号，数字\d
## 平均以上 or 0.01以上 or なし
def Sort_TFIDF_VtoU(vis_tfidf,unvis_tfidf,vis_spot_name,unvis_spot_name,vis_mean,unvis_mean,result):
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
        for j in range(len(vis_spot)):
            if result[i][0] == vis_spot[j][0]:
                visited.append(vis_spot[j][1])
                visited_mean.append(unvis_spot[j][2])
    for i in range(len(result)):
        for j in range(len(unvis_spot)):
            if result[i][1][0] == unvis_spot[j][0]:
                unvisited.append(unvis_spot[j][1])
                unvisited_mean.append(unvis_spot[j][2])
    all_spot.extend([visited,unvisited])
    ## 一番類似するスポットの特徴語top10を求める
    all,top10 = [],[]
    for i in tqdm(range(len(all_spot[0]))):
        temp = []
        same_word = list(set([all_spot[0][i][j][0] for j in range(len(all_spot[0][i]))]) & set([all_spot[1][i][j][0] for j in range(len(all_spot[1][i]))]))
        for sw in same_word:
            vi = [j for j in range(len(all_spot[0][i])) if all_spot[0][i][j][0] == sw][0]
            un  = [j for j in range(len(all_spot[1][i])) if all_spot[1][i][j][0] == sw][0]
            if len(all_spot[0][i][vi][0])>1 and all_spot[0][i][vi][1]>=visited_mean[i]/2 and all_spot[1][i][un][1]>=unvisited_mean[i]/2 and re.search(bytesymbols,all_spot[0][i][vi][0])==None:
                 temp.append([all_spot[0][i][vi][0],abs(all_spot[0][i][vi][1]-all_spot[1][i][un][1])])
        all.append(temp)
        all[i].sort(key=lambda x:x[1]) ## 昇順ソート(0に近い程が良い)
        # ## 未訪問，既訪問，類似度，単語(最初の10個まで)
        top10.append([result[i][0],result[i][1][0],result[i][1][1],all[i][:10]])

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
        same_word = list(set([all_spot[0][i][j][0] for j in range(len(all_spot[0][i]))]) & set([all_spot[1][i][j][0] for j in range(len(all_spot[1][i]))]))
        for sw in same_word:
            un = [j for j in range(len(all_spot[0][i])) if all_spot[0][i][j][0] == sw][0]
            vi  = [j for j in range(len(all_spot[1][i])) if all_spot[1][i][j][0] == sw][0]
            if len(all_spot[0][i][un][0])>1 and all_spot[0][i][un][1]>=unvisited_mean[i]/2 and all_spot[1][i][vi][1]>=visited_mean[i]/2 and re.search(bytesymbols,all_spot[0][i][un][0])==None:
                 temp.append([all_spot[0][i][un][0],abs(all_spot[0][i][un][1]-all_spot[1][i][vi][1])])
        all.append(temp)
        all[i].sort(key=lambda x:x[1]) ## 昇順ソート(0に近い程が良い)
        # ## 未訪問，既訪問，類似度，単語(最初の10個まで)
        top10.append([result[i][0],result[i][1][0],result[i][1][1],all[i][:5]])
    return top10
