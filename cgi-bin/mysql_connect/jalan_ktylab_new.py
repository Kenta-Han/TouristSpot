import MySQLdb

def main():
    conn = MySQLdb.connect(host='localhost', user='root', passwd='mysql', db='jalan_ktylab_new', charset='utf8')
    cur = conn.cursor()
    return conn,cur
