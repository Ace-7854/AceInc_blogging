import mysql.connector
from mysql.connector import Error
from env_module import get_sql_config

class MySQLManager:
    def __init__(self):
        self.config = get_sql_config

    def __define_blog(self):
        query = """CREATE TABLE posts_tbl(
        blog_id INT AUTO_INCREMENT UNIQUE PRIMARY KEY,
        author_id INT NOT_NULL,
        title VARCHAR(80),
        description TEXT
        )"""

    # region db commands
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print("✅ Connected to MySQL database")
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 MySQL connection closed")

    def __execute_query__(self, query, params=None):
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            print("✅ Query executed successfully")
        except Error as e:
            self.connection.rollback()
            print(f"❌ Error executing query: {e}")
        finally:
            if cursor:
                cursor.close()

    def __fetch_query__(self, query, params=None):
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            return cursor.fetchall()
        except Error as e:
            print(f"❌ Error fetching data: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    #endregion