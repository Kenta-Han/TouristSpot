# -*- coding: utf-8 -*-
## mysql -> jalan -> 分かち書きした文章を書き出す (助詞,助動詞,連体詞,記号を削除)
import MySQLdb
import time

# DBに接続しカーソルを取得する
conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
cur = conn.cursor()

try:
	## 関東のレビュー全体：各場所で一段落と見なす(1個目の空白の前は場所を示している)
	select_wakachi="SELECT spot_id,group_concat(wakachi separator '') FROM review_all GROUP BY spot_id INTO OUTFILE '/Users/hankenta/Desktop/spot_id_wakati.csv' LINES TERMINATED BY '\r\n';"
	cur.execute(select_wakachi)

except MySQLdb.Error as error:
	print("===MySQLdb.Error===\n",error)

conn.commit()
cur.close
conn.close
