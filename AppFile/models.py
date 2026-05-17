from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成して、接続を確立
db_pool = DB.init_db_pool()

# Departmentクラス
class Department:
    @classmethod
    def get_all_departments(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT *
                FROM departments
                ORDER BY id ASC;
                """
                cur.execute(sql)
                return cur.fetchall()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

# Userクラス
class User:
    @classmethod
    def get_all_users(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT id,name
                FROM users
                ORDER BY id ASC;
                """
                cur.execute(sql)
                return cur.fetchall()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def get_user_by_id(cls,id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT
                    id,
                    name,
                    email,
                    department_id,
                    password
                FROM users
                WHERE id = %s;
                """
                cur.execute(sql,(id,))
                return cur.fetchone()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def get_user_by_email(cls,email):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT *
                FROM users
                WHERE email = %s;
                """
                cur.execute(sql,(email,))
                return cur.fetchone()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def create_user(cls,name,email,department_id,hashed_pw):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO users(name,email,department_id,password)
                VALUES(%s,%s,%s,%s);
                """
                cur.execute(sql,(name,email,department_id,hashed_pw))
                conn.commit()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def update_user(cls,id,name,email,department_id,hashed_pw):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                if hashed_pw:
                    sql = """
                    UPDATE users
                    set name=%s,email=%s,department_id=%s,password=%s
                    WHERE id = %s;
                    """
                    cur.execute(sql,(name,email,department_id,hashed_pw,id))
                else:
                    sql = """
                    UPDATE users
                    set name=%s,email=%s,department_id=%s
                    WHERE id = %s;
                    """
                    cur.execute(sql,(name,email,department_id,id))
                conn.commit()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def delete_user(cls,id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                DELETE
                FROM users
                WHERE id = %s;
                """
                cur.execute(sql,(id,))
            conn.commit()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

# Postクラス
class Post:
    @classmethod
    def get_all_posts(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT
                    posts.*,
                    categories.name as category_name
                FROM posts
                LEFT JOIN categories ON posts.category_id = categories.id
                WHERE deleted_at IS NULL
                ORDER BY created_at DESC;
                """
                cur.execute(sql)
                posts = cur.fetchall()
            return posts
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def get_post_by_id(cls,id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT posts.*,
                    categories.name as category_name
                FROM posts
                LEFT JOIN categories ON posts.category_id = categories.id
                WHERE posts.id = %s AND deleted_at IS NULL;
                """
                cur.execute(sql,(id,))
                post = cur.fetchone()
            return post
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def get_posts_by_category(cls,category_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT *
                FROM posts as p
                LEFT JOIN categories as c
                ON p.category_id = c.id
                WHERE p.category_id = %s AND p.deleted_at IS NULL
                ORDER BY p.created_at DESC;
                """
                cur.execute(sql,(category_id,))
                posts = cur.fetchall()
            return posts
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def create_post(cls,user_id,category_id,found_date,found_place,description):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO
                posts (user_id,category_id,found_date,found_place,description) VALUES (%s,%s,%s,%s,%s);
                """
                cur.execute(sql,(user_id,category_id,found_date,found_place,description))
                conn.commit()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def update_post(cls,id,category_id,found_date,found_place,description):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                UPDATE posts
                SET category_id=%s,found_date=%s,found_place=%s,description=%s
                WHERE id = %s;
                """
                cur.execute(sql,(category_id,found_date,found_place,description,id))
                conn.commit()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def delete_post(cls,id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql ="""
                UPDATE posts
                SET deleted_at = NOW()
                where id = %s
                """
                cur.execute(sql,(id,))
                conn.commit()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

# Imageクラス
class Image:
    @classmethod
    def get_images_by_post_id(cls,post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT *
                FROM images
                WHERE post_id = %s;
                """
                cur.execute(sql,(post_id,))
                images = cur.fetchall()
            return images
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def get_image_by_image_id(cls,image_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT *
                from images
                WHERE id = %s;
                """
                cur.execute(sql,(image_id,))
                image = cur.fetchone()
            return image
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def create_images(cls,post_id,image_path):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO images (post_id,image_path) VALUES (%s,%s);
                """
                cur.execute(sql,(post_id,image_path))
                conn.commit()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def update_image_by_image_id(cls,id,image_path):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                UPDATE images
                SET image_path = %s
                WHERE id = %s;
                """
                cur.execute(sql,(image_path,id))
                conn.commit()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラー場発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def delete_images_by_post_id(cls,post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                DELETE FROM images
                WHERE post_id = %s;
                """
                cur.execute(sql,(post_id,))
                conn.commit()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def delete_image_by_image_id(cls,image_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                DELETE FROM images
                WHERE id = %s;
                """
                cur.execute(sql,(image_id,))
                conn.commit()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています{e}')
            abort(500)
        finally:
            db_pool.release(conn)

# Category_groupクラス
class CategoryGroup:
    @classmethod
    def get_all_category_groups(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT
                    cg.id as group_id,
                    cg.name as group_name,
                    c.id as category.id,
                    c.name as category
                FROM category_groups as cg
                LEFT JOIN categories as c
                ON cg.id = c.group_id
                ORDER BY cg.id ASC,c.id ASC;
                """
                cur.execute(sql)
                return cur.fetchall()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

# Threadクラス
class Thread:
    #管理者用DMスレッド一覧
    @classmethod
    def get_all_threads(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT
                    threads.id,
                    users.name AS sender_name,
                    MAX(threads.created_at) AS last_message_at
                FROM messages
                LEFT JOIN users ON threads.users.id = users.id
                GROUP BY users.id, users.name
                ORDER BY last_message_at DESC;
                """
                cur.execute(sql)
                return cur.fetchall()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    #user_idに紐づいたスレッド作成 or 取得
    @classmethod
    def create_thread_by_user_id(cls, user_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:

                # 既存チェック
                sql = """
                SELECT id
                FROM threads
                WHERE user_id = %s
                LIMIT 1;
                """
                cur.execute(sql, (user_id,))
                thread = cur.fetchone()

                if thread:
                    return thread  # 既存スレッドを表示

                # 新規作成
                sql = """
                INSERT INTO threads (user_id)
                VALUES (%s);
                """
                cur.execute(sql, (user_id,))
                conn.commit()

                return {"id": cur.lastrowid}

        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)


# Messageクラス
class Message:
        #管理者用のDMスレッド一覧から対象ユーザーとのメッセージ内容を取得
        @classmethod
        def get_messages_by_thread_id(cls, thread_id):
            conn = db_pool.get_conn()
            try:
                with conn.cursor(pymysql.cursors.DictCursor) as cur:
                    sql = """
                    SELECT
                        messages.id,
                        messages.content,
                        messages.created_at,
                        messages.sender_id,
                        users.name AS sender_name
                    FROM messages
                    LEFT JOIN users ON messages.sender_id = users.id
                    WHERE messages.thread_id = %s
                    ORDER BY messages.created_at ASC;
                    """
                    cur.execute(sql, (thread_id,))
                    messages = cur.fetchall()
                return messages
            except pymysql.Error as e:
                print(f'エラーが発生しています：{e}')
                abort(500)
            finally:
                db_pool.release(conn)

        #定型文の作成
        @classmethod
        def create_template(cls, thread_id, sender_id, post_id):
            conn = db_pool.get_conn()
            try:
                with conn.cursor() as cur:
                    sql =  """
                INSERT INTO messages (
                    thread_id,
                    sender_id,
                    content,
                    post_id
                )
                VALUES (%s, %s, %s, %s);
                """
                cur.execute(sql, (
                    thread_id,
                    sender_id,
                    "この落し物は私のものです",
                    post_id
                ))
                conn.commit()
            finally:
                db_pool.release(conn)

        #メッセージ内容を取得
        @classmethod
        def get_messages_by_user_id(cls):
            conn = db_pool.get_conn()
            try:
                with conn.cursor() as cur:
                    sql = """
                    SELECT
                        messages.id,
                        messages.content,
                        messages.created_at,
                        messages.sender_id,
                        users.name AS sender_name
                    FROM messages
                    LEFT JOIN users ON messages.sender_id = users.id
                    WHERE messages.sender_id = %s
                    ORDER BY messages.created_at ASC;
                    """
                    cur.execute(sql, (thread_id,))
                    messages = cur.fetchone()
                return messages
            except pymysql.Error as e:
                print(f'エラーが発生しています：{e}')
                abort(500)
            finally:
                db_pool.release(conn)


        #メッセージ内容を追加
        @classmethod
        def create_message(cls, thread_id, sender_id, content):
            conn = db_pool.get_conn()
            try:
                with conn.cursor() as cur:
                    sql = """
                    INSERT INTO messages (
                        thread_id,
                        sender_id,
                        content,
                        post_id
                    )
                    VALUES (%s, %s, %s, %s);
                    """
                    cur.execute(sql, (
                        thread_id,
                        sender_id,
                        content,
                        None
                    ))
                    conn.commit()
            except pymysql.Error as e:
                print(f'エラーが発生しています：{e}')
                abort(500)
            finally:
                db_pool.release(conn)

# Notificationクラス
class Notification:
    #通知一覧表示と取得
    @classmethod
    def get_all_notifications(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                sql = """
                SELECT
                    notifications.id,
                    notifications.type,
                    notifications.is_read,
                    notifications.created_at,
                    notifications.post_id,
                    posts.description,
                    posts.found_place,
                    posts.found_date,
                    categories.name AS category_name
                    -- 画像1枚だけ取得
                    (
                        SELECT image_path
                        FROM images
                        WHERE images.post_id = posts.id
                        LIMIT 1
                    ) AS image_path

                FROM notifications
                LEFT JOIN posts ON notifications.post_id = posts.id
                LEFT JOIN categories ON posts.category_id = categories.id
                ORDER BY notifications.created_at ASC;
                """
                cur.execute(sql)
                return cur.fetchall()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)
