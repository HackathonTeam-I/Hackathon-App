from flask import Flask, jsonify,request, redirect,  render_template, session, flash, abort, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from functools import wraps
import uuid
import re
import os

from models import Department,User,Post,Image,CategoryGroup,Thread,Message,Notification

# パスワードバリデーション
PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'

# 定数定義　メール形式チェック用の正規表現とセッション有効期間（日数）を定義
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
SESSION_DAYS = 30

# 投稿許可される画像ファイルの拡張子を定義
ALLOWED_EXTENSIONS = {'jpg','jpeg','png'}

#Flaskアプリの本体を作成
app = Flask(__name__)

#セッションやCSRFの改ざん防止用の鍵,環境変数 SECRET_KEY があればそれを使うなければなければランダム文字列を生成
app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)

#セッションの有効期間を設定
app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)

#悪意あるサイトから勝手にリクエストを送られる攻撃
csrf = CSRFProtect(app)

# 投稿画像拡張子チェックデコレータ
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# 管理者権限チェック用デコレータ
def admin_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if session.get('role') != 'admin':
            abort(403)
        return f(*args,**kwargs)
    return decorated_function

"""
ログイン機能
"""
# ルートページのリダイレクト処理
@app.route('/', methods=['GET'])
def index():
    user_id = session.get('user_id')
    role = session.get('role')
    if user_id is None:
        return redirect(url_for('show_login'))
    if role == 'admin':
        return redirect(url_for('show_admin_top'))
    return redirect(url_for('show_posts'))

# ログイン画面
@app.route('/login', methods=['GET'])
def show_login():
    if session.get('user_id'):
        if session.get('role') == 'admin':
            return redirect(url_for('show_admin_top'))
        return redirect(url_for('show_posts'))
    return render_template('auth/login.html')

# ログイン処理
@app.route('/login', methods=['POST'])
def process_login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash('入力してください', 'error')
        return redirect(url_for('show_login'))

    user = User.get_user_by_email(email)

    # 認証チェック
    if not user or not check_password_hash(user['password'], password):
        flash('メールまたはパスワードが違います', 'error')
        return redirect(url_for('show_login'))

    # 初回ログイン（未変更）
    if not user['is_changed_password']:
        session.clear()
        session.permanent = True
        session['tmp_user_id'] = user['id']
        return redirect(url_for('get_password'))

    # 通常ログイン
    session.clear()
    session.permanent = True
    session['user_id'] = user['id']
    session['role'] = user['role']
    if user['role'] == 'admin':
        return redirect(url_for('show_admin_top'))
    else:
        return redirect(url_for('show_posts'))

# パスワード変更画面
@app.route('/password-reset', methods=['GET'])
def get_password():
    if 'tmp_user_id' not in session:
        return redirect(url_for('show_login'))
    return render_template('/auth/password_reset.html')

# パスワード変更処理
@app.route('/password-reset', methods=['POST'])
def update_password():
    if 'tmp_user_id' not in session:
        return redirect(url_for('show_login'))

    user_id = session['tmp_user_id']
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    user = User.get_user_by_id(user_id)

    # 未入力チェック
    if not new_password or not confirm_password:
        flash('入力してください', 'error')
        return redirect(url_for('get_password'))
    # 8文字以上チェック
    if not re.match(PASSWORD_PATTERN, new_password):
        flash(
            'パスワードは8文字以上・大文字・小文字・数字を含めてください',
            'error'
        )
        return redirect(url_for('get_password'))
    #現在と同じパスワード禁止
    if check_password_hash(user['password'], new_password):
        flash('同じパスワードは使用できません', 'error')
        return redirect(url_for('get_password'))
    # パスワード一致チェック
    if new_password != confirm_password:
        flash('パスワードが一致しません', 'error')
        return redirect(url_for('get_password'))

    # パスワード更新
    hashed_password = generate_password_hash(new_password)
    User.update_password(user_id, hashed_password)
    # 仮状態解除
    session.pop('tmp_user_id', None)
    flash('パスワード変更完了。再ログインしてください', 'success')
    return redirect(url_for('show_login'))

# 管理者用トップページ
@app.route('/admin/top')
@admin_required
def show_admin_top():
    return render_template('/admin/admin_top.html')

# ログアウト
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('show_login'))

"""
ユーザー登録機能
"""

# 登録ユーザー一覧表示
@app.route('/admin/users',methods=['GET'])
@admin_required
def show_users():
    users = User.get_all_users()
    if not users:
        return render_template('admin/admin_users.html',message='登録ユーザーが存在しません')
    return render_template('admin/admin_users.html',users=users)

# ユーザー登録フォーム表示
@app.route('/admin/signup',methods=['GET'])
@admin_required
def show_signup():
    departments = Department.get_all_departments()
    return render_template('admin/admin_user_register.html',departments=departments)

# 新規ユーザー登録
@app.route('/admin/signup',methods=['POST'])
@admin_required
def register_user():
    name = request.form.get('name')
    email = request.form.get('email')
    department_id = request.form.get('department_id')
    password = request.form.get('password')

    if not all([name,email,password]):
        flash('必須項目を入力して下さい','error')
        return redirect(url_for('show_signup')) #登録画面に戻す

    # メールアドレスバリデーション
    if not re.match(EMAIL_PATTERN,email):
        flash('正しいメール形式で入力して下さい','error')
        return redirect(url_for('show_signup')) #登録画面に戻す

    # パスワードバリデーション
    if not re.match(PASSWORD_PATTERN,password):
        flash('パスワードは8文字以上で、大文字・小文字・英数字を含めてください','error')
        return redirect(url_for('show_signup')) #登録画面に戻す

    # 登録メール情報の重複チェック
    existing_user = User.get_user_by_email(email)
    if existing_user:
        flash('このメールアドレスは既に登録されています','error')
        return redirect(url_for('show_signup')) #登録画面に戻す

    hashed_pw = generate_password_hash(password)
    User.create_user(name,email,department_id,hashed_pw)
    flash('ユーザーを登録しました','success')
    return redirect(url_for('show_users'))

# ユーザー編集フォーム表示
@app.route('/admin/users/<int:id>/edit',methods=['GET'])
@admin_required
def show_edit_user(id):
    user = User.get_user_by_id(id)
    if user is None:
        abort(404,description='指定されたユーザーが見つかりません')
    departments = Department.get_all_departments()
    return render_template('admin/admin_user_edit.html',user=user,departments=departments)

# ユーザー情報更新
@app.route('/api/admin/users/<int:id>',methods=['PATCH'])
@admin_required
def update_user(id):
    user = User.get_user_by_id(id)
    if user is None:
        abort(404,description='指定されたユーザーが見つかりません')
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    department_id = data.get('department_id')
    password = data.get('password')

    # 1.必須項目が空欄になっていないか（存在確認）
    if not all([name,email]):
        return jsonify({
            'status':'error',
            'message':'必須項目を入力して下さい'
        }),400
    # 2.メール形式が問題ないか（形式確認）
    if not re.match(EMAIL_PATTERN,email):
        return jsonify({
            'status':'error',
            'message':'正しいメール形式で入力して下さい'
        }),400

    # パスワードのバリデーション（変更がある場合のみ）
    if password and not re.match(PASSWORD_PATTERN, password):
        return jsonify({
            'status': 'error',
            'message': 'パスワードは8文字以上で、大文字・小文字・英数字を含めてください'
        }), 400

    hashed_pw = generate_password_hash(password) if password else None
    User.update_user(id,name,email,department_id,hashed_pw)

    next_url = url_for('show_users')
    return jsonify({
        'status':'success',
        'message':'ユーザー情報を更新しました',
        'redirect_url':next_url
    }),200

# ユーザー情報削除
@app.route('/api/admin/users/<int:id>',methods=['DELETE'])
@admin_required
def delete_user(id):
    user = User.get_user_by_id(id)
    if user is None:
        abort(404,description='指定されたユーザーが見つかりません')
    User.delete_user(id)
    return jsonify({
        'status':'success',
        'message':'ユーザーを削除しました'
    }),200


"""
投稿機能
"""

# 投稿一覧表示
@app.route('/posts',methods=['GET'])
def show_posts():
    # セッションにuser_idが存在しない場合、ログイン画面へリダイレクト
    if 'user_id' not in session:
        return redirect(url_for('show_login'))

    # URLのクエリパラメータからcategory_idを取得
    category_id = request.args.get('category_id')

    # category_idの有無で取得関数を切り替え
    if category_id:
        posts = Post.get_posts_by_category(category_id)
    else:
        posts = Post.get_all_posts()

    # 各投稿に紐づく画像を取得
    if posts:
        for post in posts:
            post['images'] = Image.get_images_by_post_id(post['id'])
        return render_template('post/posts.html',posts=posts)
    else:
        return render_template('post/posts.html',message='投稿内容がありません')

# 投稿詳細表示
@app.route('/posts/<int:id>',methods=['GET'])
def show_post_detail(id):
    # セッションにuser_idが存在しない場合、ログイン画面へリダイレクト
    if 'user_id' not in session:
        return redirect(url_for('show_login'))

    post = Post.get_post_by_id(id)
    if post is None:
        abort(404, description='指定された投稿が見つかりません')
    images = Image.get_images_by_post_id(post['id'])

    category_id = request.args.get('category_id')

    return render_template('post/post_detail.html',post=post,images=images,category_id=category_id)

# 新規投稿フォーム表示
@app.route('/admin/posts',methods=['GET'])
@admin_required
def show_admin_posts():
    # 1.SQLでグループとカテゴリーを一括取得
    rows = CategoryGroup.get_all_category_groups()

    # 2.セレクトボックスの初期表示
    groups = []

    # グループ選択時にカテゴリーの絞り込みを実施
    categories_mapping = {}

    for row in rows:
        # グループ情報を追加
        groups.append({
            'id':row['id'],
            'name':row['name']
        })

        # グループを選択したら、カテゴリーを絞り込む
        group_key = str(row['id'])
        categories_mapping[group_key] = []

        # 選択したグループに対応するカテゴリーを取得
        for category in row['categories']:
            categories_mapping[group_key].append({
                'id': category['id'],
                'name': category['name']
            })

    return render_template('admin/admin_posts.html',groups=groups,categories_mapping=categories_mapping)

# 新規投稿処理
@app.route('/api/admin/posts',methods=['POST'])
@admin_required
def create_post():
    user_id = session.get('user_id')
    category_id = request.form.get('category_id')
    found_date = request.form.get('found_date')
    found_place = request.form.get('found_place')
    description = request.form.get('description')
    if not all([category_id,found_date,found_place]):
        return jsonify({
            'status': 'error',
            'message': '必須項目を入力して下さい'
        }),400

    Post.create_post(user_id,category_id,found_date,found_place,description)

    # 投稿作成＋ID取得
    post_id = Post.get_post_id_by_user(user_id)

    # フォームから画像ファイルを受け取る
    image_files = request.files.getlist('image')
    for image_file in image_files:
        if image_file and allowed_file(image_file.filename):

            # 1:保有するファイル名を生成
            filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]

            # 2:パスの組み立て
            image_path = os.path.join('uploads',filename)
            image_file.save(os.path.join(app.root_path,'static',image_path))

            # 3:DBに画像パスを登録
            Image.create_images(post_id,image_path)

    # 通知作成
    Notification.notify_on_post(post_id)

    return jsonify({
        'status': 'success',
        'redirect_url': url_for('show_posts')
    }),200

# 画像追加処理
@app.route('/api/admin/posts/<int:post_id>/images',methods=['POST'])
@admin_required
def upload_images(post_id):

    # １：フォームから画像ファイルを受け取る
    image_files = request.files.getlist('image')
    if not image_files:
        return jsonify({
            'status': 'error',
            'message': '投稿画像を選択して下さい'
        }),400

    # ２：先に全件バリデーションチェック
    for image_file in image_files:
        if not allowed_file(image_file.filename):
            return jsonify({
                'status': 'error',
                'message': 'jpg/jpeg/png形式のファイルを選択して下さい'
            }),400

    # ３：全件OKなら保存・DB登録
    for image_file in image_files:
        # 保存するファイル名を生成
        filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]

        # パスの組み立て
        image_path = os.path.join('uploads',filename)
        image_file.save(os.path.join(app.root_path,'static',image_path))

        # DBにパスを登録
        Image.create_images(post_id,image_path)

    return jsonify({'status': 'success',
                    'message': '画像を登録しました'
                    }),200

# 編集フォーム画面表示
@app.route('/admin/posts/<int:id>/edit',methods=['GET'])
@admin_required
def show_update_post(id):
    post = Post.get_post_by_id(id)
    if post is None:
        abort(404,description='指定された投稿がありません')
    images= Image.get_images_by_post_id(id)
    categories = CategoryGroup.get_all_category_groups()

    # カテゴリーをグループIDでまとめる
    groups = []
    categories_mapping = {}
    for category in categories:
        # グループ情報の整列
        groups.append({
            'id': category['id'],
            'name': category['name']
        })
        # JSで扱えるように、グループIDを文字列に変換する
        group_id = str(category['id'])
        categories_mapping[group_id] = []
        for c in category['categories']:
            # グループIDに対応するカテゴリーに振り分ける
            categories_mapping[group_id].append({
                'id':c['id'],
                'name':c['name']
            })
    return render_template('admin/admin_edit.html',post=post,images=images,groups=groups,categories_mapping=categories_mapping)

# 投稿更新処理
@app.route('/api/admin/posts/<int:id>',methods=['PATCH'])
@admin_required
def update_post(id):
    post = Post.get_post_by_id(id)
    if post is None:
        abort(404,description='指定された投稿が見つかりません')

    data = request.get_json()
    category_id = data.get('category_id')
    found_date = data.get('found_date')
    found_place = data.get('found_place')
    description = data.get('description')

    if not all([category_id,found_date,found_place]):
        return jsonify({
            'status':'error',
            'message':'必須項目を入力して下さい'
        }),400

    Post.update_post(id,category_id,found_date,found_place,description)

    next_url = url_for('show_post_detail',id=id)  #処理成功後の行き先を指定

    return jsonify({
        'status':'success',
        'message':'投稿内容が更新されました',
        'redirect_url':next_url  #先ほど指定した行き先を渡す
    }),200

# 画像更新処理
@app.route('/api/admin/posts/<int:post_id>/images',methods=['PATCH'])
@admin_required
def update_images(post_id):
    image_files = request.files.getlist('image') #複数ファイルを受け取る
    image_ids = request.form.getlist('image_id') #複数image_idを受け取る

    for image_id,image_file in zip(image_ids,image_files):
        image = Image.get_image_by_image_id(image_id)
        # 1.DB内に該当する画像が存在するか（存在確認）
        if image is None:
            abort(404,description='指定された画像が見つかりません')
        # 2.リクエストに画像ファイルが添付されているか
        if image_file is None:
            abort(400,description='画像ファイルがありません')
        # 3.画像が指定されたファイル形式か（形式確認）
        if not allowed_file(image_file.filename):
            abort(400,description='jpg/jpeg/png形式の画像ファイルを選択して下さい')
        old_path = os.path.join(app.root_path,'static',image['image_path'])
        if os.path.exists(old_path):
            os.remove(old_path)
        filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
        image_path = os.path.join('uploads',filename)
        image_file.save(os.path.join(app.root_path,'static',image_path))

        Image.update_image_by_image_id(image_id,image_path)

    next_url = url_for('show_post_detail',id=post_id)

    return jsonify({
        'status':'success',
        'message':'画像が更新されました',
        'redirect_url':next_url
    }),200

# 投稿削除処理
@app.route('/api/admin/posts/<int:id>',methods=['DELETE'])
@admin_required
def delete_post(id):
    post = Post.get_post_by_id(id)
    if post is None:
        abort(404,description='指定された投稿が見つかりません')
    images = Image.get_images_by_post_id(id)
    for image in images:
        file_path = os.path.join(app.root_path,'static',image['image_path'])
        if os.path.exists(file_path):
            os.remove(file_path)
    Post.delete_post(id)
    Image.delete_images_by_post_id(id)
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
    file_path = os.path.join(app.root_path,'static',image['image_path'])
    if os.path.exists(file_path):
        os.remove(file_path)
    Image.delete_image_by_image_id(image_id)
    return jsonify({
        'status':'success',
        'message':'画像を削除しました'
    }),200

"""
検索機能
"""

# 検索画面表示
@app.route('/categories',methods=['GET'])
def show_categories():
    categories = CategoryGroup.get_all_category_groups()
    if categories:
        return render_template('post/categories.html',groups=categories)
    else:
        return render_template('post/categories.html',message='カテゴリーが設定されていません')

"""
DM機能
"""
#DMスレッド一覧画面の表示
@app.route('/threads', methods=['GET'])
@admin_required
def show_threads():
    threads = Thread.get_all_threads()
    return render_template('/admin/admin_threads.html', threads=threads)


#スレッド画面の表示と取得
@app.route('/threads/<int:thread_id>', methods=['GET'])
def show_thread_detail(thread_id):
    # ログインチェック
    if "user_id" not in session:
       return redirect("/login")
    user_id = session.get('user_id')
    role = session.get('role')
    #スレット取得
    thread = Thread.get_thread_by_id(thread_id)
    # スレッドが存在しない
    if not thread:
        abort(404)
    #一般ユーザだげ所有者チェック
    if role != 'admin':
        if not thread or thread['user_id'] != user_id:
            abort(403)
    # 管理者、または自分のスレッドならメッセージを取得して表示
    messages = Message.get_messages_by_thread_id(thread_id)

    # JSTへ変換
    for message in messages:
        if message['created_at']:
            message['created_at'] = (
                message['created_at'] + timedelta(hours=9)
            )

    return render_template(
        'messages/messages.html',
        messages=messages,
        thread_id=thread_id,
        role=role,
        user_name=thread['user_name']
    )

@app.route('/my_chat', methods=['GET'])
def redirect_to_my_chat():
    if "user_id" not in session:
        return redirect(url_for('show_login'))

    # 自分のスレッドIDを探す
    thread = Thread.create_thread_by_user_id(session['user_id'])

    if thread:
        # スレッドがあれば、本番ルート（/threads/〇〇）へ転送！
        return redirect(url_for('show_thread_detail', thread_id=thread['id']))
    else:
        # 無ければ「まだないよ」という空っぽ画面を直接出す（※IDがないので転送できないため）
        return render_template('messages/messages.html', thread_id=None, messages=[], role=session.get('role'))

"""
メッセージ機能
"""
#「DMで申告」からスレッド➕定型文を作成
@app.route('/messages/<int:post_id>/request', methods=['GET'])
def create_thread(post_id):
    # ログインチェック
    if "user_id" not in session:
       return redirect("/login")
    user_id = session.get('user_id')
    # スレッドの作成 or　取得
    thread = Thread.create_thread_by_user_id(user_id)
    # 同じ投稿メッセージがまだ無い場合だけ送信
    exists = Message.exists_post_message(
        thread["id"],
        post_id
    )

    if not exists:
        Message.create_template(
            thread["id"],
            user_id,
            post_id
        )

    #チャット画面へ
    return redirect(f"/threads/{thread['id']}")


#メッセージ送信
@app.route('/api/messages/<int:thread_id>', methods=['POST'])
def create_messages(thread_id):
    # ログインチェック
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    role = session.get("role")

    # スレッドの所有者チェック
    thread = Thread.get_thread_by_id(thread_id)
    if not thread:
        abort(404)

    # 一般ユーザーだけ所有者チェック
    if role != 'admin' and thread["user_id"] != user_id:
        abort(403)

    # フォームからメッセージ取得
    content = request.form.get("content")

    post_id = request.form.get("post_id")

    # 空チェック
    if not content or not content.strip():
        return redirect(f"/threads/{thread_id}")

    # メッセージ保存
    Message.create_message(
        thread_id=thread_id,
        sender_id=user_id,
        content=content,
        post_id=post_id
    )
    return redirect(f"/threads/{thread_id}")

"""
通知機能
"""
#通知一覧
@app.route('/notifications', methods=['GET'])
def show_notifications():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    user_id = session['user_id']
    # 通知取得（画像付き）
    notifications = Notification.get_all_notifications(user_id)

    # JSTへ変換（+9時間）
    for notification in notifications:
        if notification['created_at']:
            notification['created_at'] = (
                notification['created_at'] + timedelta(hours=9)
            )

    return render_template(
        'messages/notifications.html',
        notifications=notifications
    )

# 通知クリック時
@app.route('/notifications/<int:notification_id>/read', methods=['GET'])
def read_notification(notification_id):
    # ログインチェック
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    user_id = session['user_id']
    # 既読に変更
    Notification.mark_as_read(notification_id, user_id)
    # 通知情報取得
    notification = Notification.get_notification_by_id(notification_id)
    # 投稿詳細へ遷移
    return redirect(f"/posts/{notification['post_id']}")

"""
プログラム実行
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
