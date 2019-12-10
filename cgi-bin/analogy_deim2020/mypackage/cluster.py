import pandas as pd
import pandas.io.sql as psql
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import numpy as np

import MySQLdb
import os, sys ## 全フォルダ参照
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from mysql_connect import jalan_ktylab_new
conn,cur = jalan_ktylab_new.main()

## review_vectorsのリスト作成
def review_vectors_list(id):
    review_vectors_list = []
    cur.execute(id)
    for i in cur:
        review_vectors_list.append(i[1:-2])
    return review_vectors_list

# 階層的クラスタリングの結果を返す関数
def kaisoClustering(sql, threshold):
    # SQLの結果をデータフレーム形式で取得
    df = psql.read_sql(sql, conn)
    # 群平均法とコサイン距離による階層的クラスタリング
    result = linkage(df.iloc[:, 1:301], method = 'average', metric = 'cosine')
    # 各レビューに所属クラスタ番号の列を追加
    df['cls_num'] = fcluster(result, threshold, criterion = 'distance')
    return df

# クラスタリング結果から各クラスタの重心を求める関数
def calculateCenter(df):
    # クラスタ番号でグルーピングして重心出す
    df_mean = df.groupby('cls_num').mean()
    # 次元データだけ抽出
    df_result = df_mean.iloc[:, 1:301]
    return df_result

# 各クラスタを正規化ジニ分散指標とスポット数によるスコア付けをする関数
def clusterScorering(df, input_spot_num):
    # クラスタを構成する各スポットに対し，それぞれのスポットのレビュー数が全レビュー数の閾値(%)以上なら構成スポットとしてカウント
    cls_count_threshold = 0.01
    # クラスタ番号とスコアの辞書を用意
    score_dic = {}
    # クラスタ総数を取得
    cls_total_num = df['cls_num'].max()
    # 各クラスタのスコアを求める
    for count in range(1, cls_total_num + 1):
        # クラスタを取得
        cluster = df[df['cls_num'] == count]
        # クラスタを構成するレビュー数を取得
        cls_rev_num = len(cluster)
        # クラスタの各構成スポットのレビュー数を集計
        grouped = cluster.groupby('spot_id').size()
        # 各スポットのレビュー数をリストに変換
        cls_rev_list = grouped.values.tolist()
        # 各スポットのスポットIDをリストに変換
        spot_id_list = grouped.keys()
        # 各構成スポットのレビュー総数格納用のリスト
        rev_num_list = []
        # 各スポットのレビュー数を取得
        for id in spot_id_list:
            # SQL文作成
            sql = 'SELECT count(*) FROM review_all WHERE spot_id = '
            sql += '"' + str(id) + '";'
            pd_result = psql.read_sql(sql, conn)
            result = pd_result.iloc[0, 0]
            rev_num_list.append(result)
        # レビュー数の正規化（各スポットのレビュー数 ÷ 各スポットの全レビュー数）
        seiki_rev_num_list = [x / y for (x, y) in zip(cls_rev_list, rev_num_list)]
        # 正規化したレビュー数（分子）の総和を分母に設定
        seiki_rev_sum = sum(seiki_rev_num_list)

        # ジニ係数計算
        gini = 0
        for rev_num in seiki_rev_num_list:
            gini += (rev_num / seiki_rev_sum) ** 2
        gini = 1 - gini
        # クラスタ構成スポット数
        cls_in_spot_num = 0
        # スポット数計算（全体のn%以下で構成されるスポットのレビューは構成スポット数としてカウントしない）
        for i in range(len(grouped)):
            if (cls_rev_list[i] / rev_num_list[i]) > cls_count_threshold:
                cls_in_spot_num += 1
        # スコア計算（ジニ係数 * クラスタ構成スポット数 / 全スポット数）
        score = gini * (cls_in_spot_num / input_spot_num)
        # score_dicにクラスタのスコアを追加
        score_dic[str(count)] = score

    # print(score_dic, file=sys.stderr)
    # スコア0のクラスタを削除
    for key in list(score_dic):
        if score_dic[key] == 0:
            score_dic.pop(key)
    # スコア降順でソート
    sort_score_dic = sorted(score_dic.items(), key=lambda x:x[1], reverse=True)
    # クラスタと対応するレビュー番号を得る
    result = []
    for i in range(len(sort_score_dic)):
        tmp = []
        for j in range(len(df['cls_num'])):
            if df['cls_num'][j] == int(sort_score_dic[i][0]):
                tmp.append(df['id'][j])
        result.append([sort_score_dic[i][0],sort_score_dic[i][1],tmp])
    return result
    # 入力スポット数の50%をユーザの嗜好を示すクラスタとして利用
    # if len(sort_score_dic) > (input_spot_num / 2):
    #     result_dic = {}
    #     for i in range(int(input_spot_num / 2)):
    #         result_dic[sort_score_dic[i][0]] = sort_score_dic[i][1]
    # return result_dic

# 検索スポットのレビューをクラスタのスコアとレビューとの類似度によってスコアリングする関数
# def reviewScorering(center, search_spot_list, preference_num, norm_threshold, score_dic):
#     # 結果データフレームの初期化
#     res_data = pd.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)
#     # 1回目だけデータフレームをconcatしないためのフラグ
#     flag = False
#     # 利用クラスタごとに計算
#     for cls_num in score_dic:
#         # 重心ベクトルを用意
#         fav_vec = center[int(cls_num)-1:int(cls_num)]
#         # 重心ベクトルのノルムを用意
#         fav_norm = np.linalg.norm(fav_vec)
#         # COS類似度計算
#         dimention = []
#         for i in range(1,301):
#             dimention.append(f'd{i} * {fav_vec.iloc[0][i-1]}')
#         # select文作成
#         select_review = f"SELECT * ,{score_dic[cls_num]} * 0.25 + cos * 0.75 as cos25 , {score_dic[cls_num]} * 0.5 + cos * 0.5 as cos50, {score_dic[cls_num]} * 0.75 + cos * 0.25 as cos75 FROM (select {cls_num} as cls_num, id, spot_id, review_text, ({' + '.join(dimention)})/(norm * {fav_norm}) as cos from (SELECT * FROM (SELECT id,spot_id, review_text from review_all WHERE spot_id in ("
#         # 検索spot_idの動的入力
#         for spot_id in search_spot_list:
#             select_review += '"' + str(spot_id) + '"' + ','
#         # ゴリ押し調整
#         select_review = select_review[:-1]
#         select_review += ')) AS rev JOIN (SELECT * FROM review_vectors_spotname WHERE norm >= '
#         select_review += str(norm_threshold)
#         select_review += ') AS tmp using(id)) AS func) AS main'
#         res_reviews = pd.read_sql(select_review, conn)
#         # 1回目だけconcatしない
#         if (flag == False):
#             # 結果データに1回目の実行結果を代入
#             res_data = res_reviews
#             # フラグをTrueにして次回以降実行しない
#             flag = True
#             continue
#         # 各クラスタのスコアリング結果と今までの結果を結合
#         res_data = pd.concat([res_data,res_reviews])
#     return res_data
