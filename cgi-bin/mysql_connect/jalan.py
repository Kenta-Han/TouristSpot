import MySQLdb

def connect_jalan():
    conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan', charset='utf8')
    cur = conn.cursor()
    return conn,cur
