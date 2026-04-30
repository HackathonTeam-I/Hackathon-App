from flask import Flask, request, redirect,  render_template, session, flash, abort, url_for
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
import hashlib
import uuid
import re
import os

from models import Post, Thread, Message


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