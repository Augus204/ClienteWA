import pymysql.cursors

def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='Maxwell',
        password='123456',
        database='flask_login')
        # cursorclass=pymysql.cursors.DictCursor)
    return connection

