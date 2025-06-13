import mysql.connector
from mysql.connector import Error
from env_module import get_sql_config

class MySQLManager:
    def __init__(self):
        self.config = get_sql_config


    def create_required_tbls(self):
        tables = self.__fetch_query__("SHOW TABLES;")

        if tables:
            posts = False 
            users = False
            cat = False
            pos_cat = False
            comments = False

            for table in tables:
                if table['Tables_in_db_blog'].lower() == "posts_tbl":
                    posts = True
                if table['Tables_in_db_blog'].lower() == "user_tbl":
                    users = True
                if table['Tables_in_db_blog'].lower() == "catagory_tbl":
                    cat = True
                if table['Tables_in_db_blog'].lower() == "post_cat_tbl":
                    pos_cat = True
                if table['Tables_in_db_blog'].lower() == "comments_tbl":
                    comments = True
                
            if not posts:
                self.__define_posts()
            if not users:
                self.__define_users()
            if not cat:
                self.__define_catagories()
            if not pos_cat:
                self.__define_post_cat()
            if not comments:
                self.__define_comments()
        else:
            self.__define_posts()
            self.__define_users()
            self.__define_catagories()
            self.__define_comments()
            self.__define_post_cat()

    #region create tables
    def __define_posts(self):
        query = """CREATE TABLE posts_tbl(
        blog_id INT AUTO_INCREMENT UNIQUE PRIMARY KEY,
        user_id INT NOT_NULL,
        title VARCHAR(80),
        slug VARCHAR(80),
        content TEXT,
        status ENUM('draft', 'published', 'archived'),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FORIEGN KEY (user_id) REFERENCES user_tbl(user_id)
        )"""

        self.__execute_query__(query)

    def __define_users(self):
        query = """CREATE TABLE user_tbl (
        user_id INT AUTO_INCREMENT UNIQUE PRIMARY KEY,
        username VARCHAR(50),
        email VARCHAR(100),
        password VARCHAR(255),
        role ENUM('reader', 'author', 'admin') DEFAULT 'reader',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""

        self.__execute_query__(query)

    def __define_catagories(self):
        query = """CREATE TABLE catagory_tbl (
        catagory_id INT AUTO_INCREMENT UNIQUE PRIMARY KEY, 
        cat_name VARCHAR(75),
        slug VARCHAR(75)
        )"""

        self.__execute_query__(query)

    def __define_post_cat(self):
        query = """CREATE TABLE post_cat_tbl (
        post_id INT NOT NULL,
        catagory_id INT NOT NULL,
        FORIEGN KEY (post_id) REFERENCES post_tbl(post_id),
        FORIEGN KEY (catagory_id) REFERENCES catagory_tbl(catagory_id)
        )"""

    def __define_comments():
        query = """CREATE TABLE comments_tbl(
        comment_id INT AUTO_INCREMENT UNIQUE PRIMARY KEY,
        post_id INT,
        user_id INT,
        username VARCHAR(50),
        content TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""

    #endregion

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