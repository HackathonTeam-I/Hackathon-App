from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成して、接続を確立
db_pool = DB.init_db_pool()

# Postsクラス
class Post:
    @classmethod
    def get_all_posts(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT
                    posts.*,
                    users.name,
                    categories.name as category_name
                FROM posts
                LEFT JOIN users ON posts.user_id = users.id
                LEFT JOIN categories ON posts.category_id = categories.id
                WHERE deleted_at IS NULL
                ORDER BY created_at DESC;
                """
                cur.execute(sql)
                posts = cur.fetchall()
            return posts
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
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
    def create_posts(cls,user_id,category_id,found_date,found_place,description):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO
                posts (user_id,category_id,found_date,found_place,description) VALUES (%s,%s,%s,%s,%s)
                """
                cur.execute(sql,(user_id,category_id,found_date,found_place,description))
                conn.commit()
        except pymysql.Error as e:
            print(f'サーバー接続上のエラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)


    @classmethod
    def update_posts(cls,id):
        pass


    @classmethod
    def delete_posts(cls,id):
        pass
