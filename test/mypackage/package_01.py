import numpy as np
import copy
import MySQLdb
import mypackage.cossim as myp_cos
from pprint import pprint
sc = myp_cos.SimCalculator()

conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

def Spot_List(select_spot):
    spot_list = []
    cur.execute(select_spot)
    for i in cur:
        spot_list.append(i)
    return spot_list

def Doc2Cec_Feature(spot_vectors):
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
        # print(name)
        result_list.append([name, list(result)])
        target = []
        result = []
    return result_list

def Recommend_All(his_spot_id,spot_id,his_spot_review,spot_review):
    value_HtoA = []
    value_AtoH = []
    for i in range(len(spot_id)):
        temp_HtoA = []
        temp_AtoH = []
        for j in range(len(his_spot_id)):
            his_to_area = sc.sim_cos(his_spot_review[i],spot_review[j])
            temp_HtoA.append([spot_id[j],his_to_area])
            area_to_his = sc.sim_cos(spot_review[i],his_spot_review[j])
            temp_AtoH.append([his_spot_id[j],area_to_his])
        value_HtoA.append(temp_HtoA)
        value_AtoH.append(temp_AtoH)
    dic_HtoA = dict(zip(his_spot_id,value_HtoA)) ## 辞書作成 (スポット名,類似度)
    dic_AtoH = dict(zip(spot_id,value_AtoH)) ## 辞書作成 (スポット名,類似度)
    # result = sorted(dic.items(),key=lambda x:x[1],reverse=True) ##降順にソート
    # pprint(result)
    # pprint(list(dic_HtoA.values()))
    return dic_HtoA,dic_AtoH
