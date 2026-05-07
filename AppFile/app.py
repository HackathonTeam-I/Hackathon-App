from flask import Flask, jsonify,request, redirect,  render_template, session, flash, abort, url_for
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from functools import wraps
import hashlib
import uuid
import re
import os

from models import Post,Image,Thread,Message

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

# 管理者権限チェック用デコレータ
def admin_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if session.get('role') != 'admin':
            abort(403)
        return f(*args,**kwargs)
    return decorated_function

"""
投稿機能
"""

# 投稿一覧表示
@app.route('/posts',methods=['GET'])
def show_posts():
    posts = Post.get_all_posts()
    if posts:
        for post in posts:
            post['images'] = Image.get_images_by_post_id(post['id'])
        return render_template('post/posts.html',posts=posts)
    else:
        return render_template('post/posts.html',message='投稿内容がありません')

# 投稿詳細表示
@app.route('/posts/<int:id>',methods=['GET'])
def show_posts_detail(id):
    post = Post.get_post_by_id(id)
    if post is None:
        abort(404, description='指定された投稿が見つかりません')
    images = Image.get_images_by_post_id(post['id'])
    return render_template('post/posts_detail.html',post=post,images=images)

# 新規投稿処理
@app.route('/api/admin/posts',methods=['POST'])
@admin_required
def create_posts():
    user_id = session.get('user_id')
    category_id = request.form.get('category_id')
    found_date = request.form.get('found_date')
    found_place = request.form.get('found_place')
    description = request.form.get('description')
    if not all([category_id,found_date,found_place]):
        flash('必須項目を入力して下さい','error')
        return redirect(url_for('show_admin_posts')) #新規投稿画面へ

    Post.create_posts(category_id,found_date,found_place,description)
    flash('投稿が完了しました','success')
    return redirect(url_for('show_admin_top')) #管理者トップ画面へ

# 画像追加処理
@app.route('/api/admin/posts/<int:post_id>/images',methods=['POST'])
@admin_required
def upload_images(post_id):
    # １：フォームから画像ファイルを受け取る
    image_file = request.files.get('image')
    if image_file is None:
        flash('投稿画像を選択して下さい','error')
        return redirect(url_for('show_admin_posts')) #新規投稿画面へ

    # ２：保存するファイル名を生成
    filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]

    # ３：パスの組み立て
    image_path = os.path.join('static/uploads',filename)
    image_file.save(os.path.join('AppFile',image_path))

    # ４：DBにパスを登録
    Image.create_images(post_id,image_path)
    flash('画像を登録しました','success')
    return redirect(url_for('show_posts_detail',id=post_id))

# 投稿更新処理
@app.route('/api/admin/posts/<int:id>',methods=['PATCH'])
@admin_required
def update_posts(id):
    post = Post.get_post_by_id(id)
    if post is None:
        abort(404,description='指定された投稿が見つかりません')

    category_id = request.form.get('category_id')
    found_date = request.form.get('found_date')
    found_place = request.form.get('found_place')
    description = request.form.get('description')

    Post.update_posts(id,category_id,found_date,found_place,description)

    next_url = url_for('show_posts_detail',id=id)  #処理成功後の行き先を指定

    return jsonify({
        'status':'success',
        'message':'投稿内容が更新されました',
        'redirect_url':next_url  #先ほど指定した行き先を渡す
    }),200

# 画像更新処理
@app.route('/api/admin/posts/<int:post_id>/images/<int:image_id>',methods=['PATCH'])
@admin_required
def update_images(post_id,image_id):
    image = Image.get_image_by_image_id(image_id)
    if image is None:
        abort(404,description='指定された画像が見つかりません')
    old_path = os.path.join('AppFile',image['image_path'])
    if os.path.exists(old_path):
        os.remove(old_path)
    image_file = request.files.get('image')
    if image_file is None:
        abort(400,description='画像ファイルがありません')
    filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
    image_path = os.path.join('static/uploads',filename)
    image_file.save(os.path.join('AppFile',image_path))

    Image.update_image_by_image_id(image_id,image_path)

    next_url = url_for('show_posts_detail',id=post_id)

    return jsonify({
        'status':'success',
        'message':'画像が更新されました',
        'redirect_url':next_url
    }),200

# 投稿削除処理
@app.route('/api/admin/posts/<int:id>',methods=['DELETE'])
@admin_required
def delete_posts(id):
    post = Post.get_post_by_id(id)
    images = Image.get_images_by_post_id(id)
    for image in images:
        file_path = os.path.join('AppFile',image['image_path'])
        if os.path.exists(file_path):
            os.remove(file_path)
    if post is None:
        abort(404,description='指定された投稿が見つかりません')
    Post.delete_posts(id)
    return jsonify({
        'status':'success',
        'message':'投稿を削除しました'
        }),200

# 画像削除処理
@app.route('/api/admin/posts/<int:post_id>/images/<int:image_id>',methods=['DELETE'])
@admin_required
def delete_images(post_id,image_id):
    image = Image.get_image_by_image_id(image_id)
    if image is None:
        abort(404,description='指定された画像が見つかりません')
    file_path = os.path.join('AppFile',image['image_path'])
    if os.path.exists(file_path):
        os.remove(file_path)
    Image.delete_image_by_image_id(image_id)
    return jsonify({
        'status':'success',
        'message':'画像を削除しました'
    }),200



#DM画面表示
@app.route('/threads', methods=['GET'])
def show_threads():
    threads = Thread.get_all_threads()



"""
プログラム実行
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
