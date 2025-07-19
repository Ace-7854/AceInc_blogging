import mysql.connector
from mysql.connector import Error

class MySQLManager:
    def __init__(self):
        from custom_modules.env_module import get_sql_config
        self.config = get_sql_config()


    def get_db_tbl(self) -> dict:
        return self.__fetch_query__("SHOW TABLES;")

    def create_required_tbls(self):
        tables = self.get_db_tbl()

        if tables is not None:
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

    #region user cmds
    def update_user(self, id:str|int, username:str=None, email:str=None, password:str=None, role:str=None, flag:str=None):
        query = "UPDATE user_tbl SET "
        params = []

        if username:
            query += "username = %s, "
            params.append(username)
        if email:
            query += "email = %s, "
            params.append(email)
        if password:
            from custom_modules.security_module import hash_alg
            query += "password = %s, "
            params.append(hash_alg(password))
        if role:
            query += "role = %s, "
            params.append(role)
        if flag:
            query += "flag = %s, "
            params.append(flag)

        query = query.rstrip(", ") + " WHERE user_id = %s"
        params.append(id)

        self.__execute_query__(query, tuple(params))

    def get_user_by_id(self, id:int|str) -> dict:
        query = """SELECT * FROM user_tbl WHERE user_id = %s"""

        params = (id, )
        return self.__fetch_query__(query, params)[0]

    def get_user_by_username(self, username:str) -> dict:
        query = """SELECT * FROM user_tbl WHERE username = %s AND flag != 'banned'"""

        params = (username,)
        return self.__fetch_query__(query, params)[0]

    def get_user_by_email(self, emails:str) -> dict:
        query = "SELECT * FROM user_tbl WHERE email = %s AND flag != 'banned'"

        params = (emails,)
        return self.__fetch_query__(query, params)[0]
    
    def insert_new_user(self, username:str, email:str, password:str):
        query = "INSERT INTO user_tbl(username, email, password) VALUES (%s, %s, %s)"

        from custom_modules.security_module import hash_alg
        params = (username, email, hash_alg(password))

        return self.__execute_query__(query, params)
    
    def get_all_users(self) -> list[dict]:
        query = "SELECT user_id, username, email, role, flag,created_at FROM user_tbl"

        return self.__fetch_query__(query)

    #endregion

    #region catagories cmds

    def get_catagories(self):
        query = "SELECT * FROM catagory_tbl"

        return self.__fetch_query__(query)
    
    def insert_new_catagory(self, title:str, description:str):
        from custom_modules.utils import simple_slugify as slugify
        query = "INSERT INTO catagory_tbl(cat_name, description, slug) VALUES(%s, %s, %s)"

        params = (title, description, slugify(title))
        self.__execute_query__(query, params)

    def get_cat_by_slug(self, slug:str) -> dict:
        query = "SELECT * FROM catagory_tbl WHERE slug = %s"

        params = (slug, )
        return self.__fetch_query__(query, params)[0]        

    #endregion

    #region posts
    def insert_new_post(self, id:str|int, title:str, content:str) -> None:
        query = "INSERT INTO posts_tbl(user_id, title, slug, content) VALUES(%s, %s, %s, %s)"

        from custom_modules.utils import simple_slugify as slug
        params = (id, title, slug(title), content)

        self.__execute_query__(query, params)
    
    def get_post_by_id(self, id:int|str) -> dict:
        query = "SELECT * FROM posts_tbl WHERE post_id = %s"

        params = (id, )
        return self.__fetch_query__(query, params)[0]
    
    def get_post_by_title(self, title:str) -> dict:
        query = "SELECT post_id FROM posts_tbl WHERE title = %s"

        params = (title, )
        return self.__fetch_query__(query, params)[0]
    
    def get_post_by_slug(self, slug:str) -> dict:
        query = "SELECT * FROM posts_tbl WHERE slug = %s"

        params = (slug, )
        return self.__fetch_query__(query, params)[0]
    
    def get_post_slug_by_id(self, id:str|int) -> str:
        query = "SELECT slug FROM posts_tbl WHERE post_id = %s"

        params = (id, )
        return self.__fetch_query__(query, params)[0]['slug']

    #endregion

    #region post cat
    def insert_link_cat_post(self, cat:str|int, post:str|int):
        query = "INSERT INTO post_cat_tbl(post_id, catagory_id) VALUES(%s, %s)"

        params = (post, cat)
        self.__execute_query__(query, params)

    def get_all_posts_by_cat(self, cat_id:str|int) -> list:
        query = "SELECT post_id FROM post_cat_tbl WHERE catagory_id = %s"

        params = (cat_id, )
        return self.__fetch_query__(query, params)

    #endregion

    #region comments

    def get_comments_by_post(self,id:str|int) -> list[dict]:
        query = "SELECT * FROM comments_tbl WHERE post_id = %s"

        params = (id,)
        return self.__fetch_query__(query, params)

    def insert_new_comment(self, post_id:str|int, user_id:str|int, username:str, content:str) -> None:
        query = "INSERT INTO comments_tbl(post_id, user_id, username, content) VALUES(%s, %s, %s, %s)"

        params = (post_id, user_id, username, content)
        self.__execute_query__(query, params)

    #endregion

    #region create tables
    def __define_posts(self):
        query = """CREATE TABLE posts_tbl(
        post_id INT AUTO_INCREMENT UNIQUE PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(80),
        slug VARCHAR(80),
        content TEXT,
        status ENUM('draft', 'published', 'archived') DEFAULT 'published',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user_tbl(user_id)
        )"""

        self.__execute_query__(query)

    def __define_users(self):
        query = """CREATE TABLE user_tbl (
        user_id INT AUTO_INCREMENT UNIQUE PRIMARY KEY,
        username VARCHAR(50),
        email VARCHAR(100),
        password VARCHAR(255),
        role ENUM('reader', 'author', 'admin') DEFAULT 'reader',
        flag ENUM('banned', 'warning', 'review', 'none') DEFAULT 'none',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""

        self.__execute_query__(query)

    def __define_catagories(self):
        query = """CREATE TABLE catagory_tbl (
        catagory_id INT AUTO_INCREMENT UNIQUE PRIMARY KEY, 
        cat_name VARCHAR(75),
        description TEXT,
        slug VARCHAR(75)
        )"""

        self.__execute_query__(query)

    def __define_post_cat(self):
        query = """CREATE TABLE post_cat_tbl (
        post_id INT NOT NULL,
        catagory_id INT NOT NULL,
        FOREIGN KEY (post_id) REFERENCES posts_tbl(post_id),
        FOREIGN KEY (catagory_id) REFERENCES catagory_tbl(catagory_id)
        )"""

        self.__execute_query__(query)

    def __define_comments(self):
        query = """CREATE TABLE comments_tbl(
        comment_id INT AUTO_INCREMENT UNIQUE PRIMARY KEY,
        post_id INT,
        user_id INT,
        username VARCHAR(50),
        content TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user_tbl(user_id),
        FOREIGN KEY (post_id) REFERENCES posts_tbl(post_id)
        )"""

        self.__execute_query__(query)

    #endregion

    #region drop cmds

    def drop_tbl(self, table:str):
        self.__execute_query__(f"DROP TABLE {table};")


    #endregion

    # region db commands
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.connection = None

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

    def __execute_query__(self, query, params=None):
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            self.connection.rollback()
            print(f"Error executing query: {e}")
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
            print(f"Error fetching data: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    #endregion