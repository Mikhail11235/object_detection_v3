import MySQLdb

db = MySQLdb.connect(host='0.0.0.0', user='root', passwd='123456', db='ovd', port=3306)
cursor = db.cursor()
cursor.execute("select * from users")

for row in cursor.fetchall():
    print(row)
