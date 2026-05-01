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
