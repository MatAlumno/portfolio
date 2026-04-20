import pymysql

def get_db():
    try:
        return pymysql.connect(
            host='localhost',
            user='root', 
            password='mazapan0220', 
            database='portfolio_db',
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"Errorazo en la conexión: {e}")
        return None
