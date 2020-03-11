from tqdm import tqdm
import re,sys

bytesymbols = re.compile("[!-/:*-@[-`{-~\d]") ## 半角記号，数字\d
## 調和平均 差が小値が大，差が大値が小 → 値が大の方が良い(昇順後ろから10個)
checkword = ["行く","行う","とても","思う","良い","よい","できる","また","とにかく","それほど","そんなに","あまり","ない","無い","もう","もっと","かなり","いい","ぜひ","いつも","なかなか","ちょっと","出来る","とっても","やはり","入れる","いれる","なぜ","みる","見る"]

## 相対的特徴 元sort_tfidf_UtoV_harmonic
def sort_tfidf_UtoV_relative(vis_tfidf,unvis_tfidf,vis_spot_name,unvis_spot_name,result):
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
    ## 一番類似するスポットの特徴語を求める
    all,top10 = [],[]
    for i in tqdm(range(len(all_spot[0]))):
        temp = []
        same_word = list(set([all_spot[0][i][j][0] for j in range(len(all_spot[0][i]))]) & set([all_spot[1][i][j][0] for j in range(len(all_spot[1][i]))]))
        for sw in same_word:
            un = [j for j in range(len(all_spot[0][i])) if all_spot[0][i][j][0] == sw][0]
            vi = [j for j in range(len(all_spot[1][i])) if all_spot[1][i][j][0] == sw][0]
            if len(all_spot[0][i][un][0])>1 and re.search(bytesymbols,all_spot[0][i][un][0])==None:
                 temp.append([all_spot[0][i][un][0],abs(2/(1/all_spot[0][i][un][1]+1/all_spot[1][i][vi][1]))])
        all.append(temp)
        all[i].sort(key=lambda x:x[1],reverse=True)## 降順ソート
        # ## 未訪問，既訪問，類似度，単語(最初の10個まで)
        top10.append([result[i][0],result[i][1][0],result[i][1][1],all[i][:11]])
    return top10

## tfidf
def sort_tfidf_UtoV_tfidfcos(cluid,vis_tfidf,unvis_tfidf,vis_spot_name,unvis_spot_name,result):
    ## TFIDFの結果にスポット名を追加
    vis_spot,unvis_spot = [],[]
    for i in range(len(vis_spot_name)):
        vis_spot.append([vis_spot_name[i],vis_tfidf[i]])
    for i in range(len(unvis_spot_name)):
        unvis_spot.append([unvis_spot_name[i],unvis_tfidf[i]])
    ## スポットを関連付ける
    visited,unvisited,all_spot = [],[],[]
    for i in range(len(result)):
        for j in range(len(unvis_spot)):
            if result[i][0] == unvis_spot[j][0]:
                unvisited.append(unvis_spot[j][1])
    for i in range(len(result)):
        for j in range(len(vis_spot)):
            if result[i][1] == vis_spot[j][0]:
                visited.append(vis_spot[j][1])
    all_spot.extend([unvisited,visited])
    ## 一番類似するスポットの特徴語を求める
    all_d,top10 = [],[]
    # print("all_spot",all_spot, file=sys.stderr)
    for i in tqdm(range(len(all_spot[0]))):
        temp = []
        same_word = list(set([all_spot[0][i][j][0] for j in range(len(all_spot[0][i]))]) & set([all_spot[1][i][j][0] for j in range(len(all_spot[1][i]))]))
        for sw in same_word:
            un = [j for j in range(len(all_spot[0][i])) if all_spot[0][i][j][0] == sw][0]
            vi = [j for j in range(len(all_spot[1][i])) if all_spot[1][i][j][0] == sw][0]
            if (len(all_spot[0][i][un][0])>1 and re.search(bytesymbols,all_spot[0][i][un][0])==None):
                if all_spot[1][i][vi][1]==0 or all_spot[0][i][un][1]==0:
                    temp.append([all_spot[0][i][un][0],0])
                else:
                    temp.append([all_spot[0][i][un][0],(2/(1/all_spot[0][i][un][1]+1/all_spot[1][i][vi][1]))])
        temp.append(["__finish__",0])
        all_d.append(temp)
        all_d[i].sort(key=lambda x:x[1],reverse=True)
        ## 対応付け(調和平均>=0)のキーワードを取り出す
        for a in range(len(all_d[i])):
            if all_d[i][a][1] <= 0:
                tmp = []
                for j in range(len(all_d[i][:a])):
                    tmp.append(all_d[i][j][0])
                # top10.append([cluid,result[i][0],result[i][1],result[i][2],all_d[i][:a]])
                top10.append([cluid,result[i][0],result[i][1],result[i][2],tmp[:15]])
                break
        # ## 未訪問，既訪問，類似度，単語(最初の10個まで)
        # tmp = []
        # for j in range(len(all_d[i])):
        #     tmp.append(all_d[i][j][0])
        # top10.append([cluid,result[i][0],result[i][1],result[i][2],tmp[:10]])
    return top10

## doc2vec特徴(一的)
def sort_tfidf_UtoV_doc2vec(vis_tfidf,unvis_tfidf,vis_spot_name,unvis_spot_name,result):
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
    # print(all_spot, file=sys.stderr)
    ## 一番類似するスポットの特徴語を求める
    all,top10 = [],[]
    for i in tqdm(range(len(all_spot[0]))):
        temp = []
        same_word = list(set([all_spot[0][i][j][0] for j in range(len(all_spot[0][i]))]) & set([all_spot[1][i][j][0] for j in range(len(all_spot[1][i]))]))
        for sw in same_word:
            un = [j for j in range(len(all_spot[0][i])) if all_spot[0][i][j][0] == sw][0]
            vi = [j for j in range(len(all_spot[1][i])) if all_spot[1][i][j][0] == sw][0]
            if len(all_spot[0][i][un][0])>1 and re.search(bytesymbols,all_spot[0][i][un][0])==None:
                 temp.append([all_spot[0][i][un][0],abs(2/(1/all_spot[0][i][un][1]+1/all_spot[1][i][vi][1]))])
        all.append(temp)
        all[i].sort(key=lambda x:x[1],reverse=True)## 降順ソート
        # ## 未訪問，既訪問，類似度，単語(最初の10個まで)
        top10.append([result[i][0],result[i][1][0],result[i][1][1],all[i][:11]])
    return top10
