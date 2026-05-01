from flask import Flask, jsonify,request, redirect,  render_template, session, flash, abort, url_for
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
import hashlib
import uuid
import re
import os

from models import Post,Thread,Message

# 定数定義　メール形式チェック用の正規表現とセッション有効期間（日数）を定義
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
SESSION_DAYS = 30


#Flaskアプリの本体を作成
app = Flask(__name__)

#セッションやCSRFの改ざん防止用の鍵,環境変数 SECRET_KEY があればそれを使うなければなければランダム文字列を生成
app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)

#セッションの有効期間を設定
app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)

#悪意あるサイトから勝手にリクエストを送られる攻撃
csrf = CSRFProtect(app)

"""
投稿機能
"""
#投稿内容を取得
@app.route('/api/posts',methods=['GET'])
def get_posts():
    posts = Post.get_all_posts()
    return jsonify(posts)

# 投稿一覧表示
@app.route('/posts',methods=['GET'])
def show_posts():
    posts = Post.get_all_posts()
    if posts:
        return render_template('post/posts.html',posts=posts)
    else:
        return render_template('post/posts.html',message='投稿内容がありません')

# 投稿表示取得
@app.route('/api/posts/<int:id>',methods=['GET'])
def get_posts_detail(id):
    post = Post.get_post_by_id(id)
    if post is None:
        abort(404, description='指定された投稿が見つかりません')
    return jsonify(post)

# 投稿詳細表示
@app.route('/posts/<int:id>',methods=['GET'])
def show_posts_detail(id):
    post = Post.get_post_by_id(id)
    if post is None:
        abort(404, description='指定された投稿が見つかりません')
    return render_template('post/posts_detail.html',post=post)

# 新規投稿処理
@app.route('/api/admin/posts',methods=['POST'])
@admin_required
def create_posts():
    category_id = request.form.get('category_id')
    found_date = request.form.get('found_date')
    found_place = request.form.get('found_place')
    description = request.form.get('description')
    if not all[category_id,found_date,found_place]:
        flash('必須項目を入力して下さい','error')
        return redirect(url_for('show_admin_posts')) #新規投稿画面へ

    Post.create_posts(category_id,found_date,found_place,description)
    flash('投稿が完了しました','success')
    return redirect(url_for('show_admin_top')) #管理者トップ画面へ

# 投稿更新処理
@app.route('/api/admin/posts/<int:id>',methods=['PATCH'])
@admin_required
def update_posts(id):
    post = Post.get_post_by_id(id)
    if post is None:
        abort(404)

    category_id = request.form.get('category_id')
    found_date = request.form.get('found_date')
    found_place = request.form.get('found_place')
    description = request.form.get('description')

    Post.update_posts(id,category_id,found_date,found_place,description)
    flash('投稿内容が更新されました','success')
    return redirect(url_for('show_posts_detail',id=id))






"""
プログラム実行
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
