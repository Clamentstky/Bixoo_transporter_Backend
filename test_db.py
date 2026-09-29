import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="Realme30122026",
    database="bixoo_transportation",
    cursorclass=pymysql.cursors.DictCursor
)
cursor = conn.cursor()
cursor.execute("SELECT id, status, completed_at FROM trips WHERE trip_code = 'TRIP-8E7B281D'")
print(cursor.fetchall())
