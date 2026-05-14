DROP DATABASE IF EXISTS FindIt;

DROP USER IF EXISTS 'testuser' @'%';

CREATE USER 'testuser' @'%' IDENTIFIED BY 'testuser';

CREATE DATABASE IF NOT EXISTS FindIt DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON FindIt.* TO 'testuser' @'%';

FLUSH PRIVILEGES;

USE FindIt;

-- （１）所属部署テーブル
CREATE TABLE IF NOT EXISTS departments (
  id BIGINT UNSIGNED AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  PRIMARY KEY (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- （２）カテゴリーグループテーブル（例：「小物・アクセサリー類」）
CREATE TABLE IF NOT EXISTS category_groups (
  id BIGINT UNSIGNED AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL UNIQUE,
  PRIMARY KEY(id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- （３）カテゴリーテーブル（各グループに属する個別カテゴリー）
CREATE TABLE IF NOT EXISTS categories (
  id BIGINT UNSIGNED AUTO_INCREMENT,
  group_id BIGINT UNSIGNED NOT NULL,
  name VARCHAR(100) NOT NULL UNIQUE,
  PRIMARY KEY(id),
  KEY idx_categories_group_id(group_id),
  CONSTRAINT fk_categories_group FOREIGN KEY(group_id) REFERENCES category_groups(id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- （４）登録ユーザーテーブル
CREATE TABLE IF NOT EXISTS users (
  id BIGINT UNSIGNED AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  department_id BIGINT UNSIGNED,
  role ENUM('admin', 'user') DEFAULT 'user' NOT NULL,
  created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email (email),
  KEY idx_users_department(department_id),
  CONSTRAINT fk_users_department FOREIGN KEY(department_id) REFERENCES departments(id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- （５）投稿テーブル
CREATE TABLE IF NOT EXISTS posts (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  category_id BIGINT UNSIGNED NOT NULL,
  found_date DATE NOT NULL,
  found_place VARCHAR(100) NOT NULL,
  description TEXT,
  created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  remind_at DATETIME(6) DEFAULT NULL,
  deleted_at DATETIME (6) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idx_posts_user_id (user_id),
  KEY idx_posts_category_id (category_id),
  CONSTRAINT fk_posts_user FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_posts_category FOREIGN KEY (category_id) REFERENCES categories (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- （６）投稿写真テーブル
CREATE TABLE IF NOT EXISTS images (
  id BIGINT UNSIGNED AUTO_INCREMENT,
  post_id BIGINT UNSIGNED NOT NULL,
  image_path VARCHAR(255) NOT NULL,
  PRIMARY KEY(id),
  KEY idx_images_post_id (post_id),
  CONSTRAINT fk_image_post FOREIGN KEY (post_id) REFERENCES posts (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- （７）DMリストテーブル
CREATE TABLE IF NOT EXISTS threads (
  id BIGINT UNSIGNED AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY(id),
  CONSTRAINT fk_thread_user FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- （８）DM投稿メッセージ用テーブル
CREATE TABLE IF NOT EXISTS messages (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  post_id BIGINT UNSIGNED NOT NULL,
  sender_id BIGINT UNSIGNED NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY idx_messages_post (post_id),
  KEY idx_messages_sender (sender_id),
  CONSTRAINT fk_messages_post FOREIGN KEY (post_id) REFERENCES posts (id),
  CONSTRAINT fk_messages_sender FOREIGN KEY (sender_id) REFERENCES users (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- （９）通知テーブル
CREATE TABLE IF NOT EXISTS notifications (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  post_id BIGINT UNSIGNED DEFAULT NULL,
  type ENUM('new_post', 'message', 'system', 'reminder') NOT NULL,
  is_read BOOLEAN DEFAULT FALSE,
  created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY idx_notifications_user_id (user_id),
  KEY idx_notifications_post_id (post_id),
  CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_notifications_post FOREIGN KEY (post_id) REFERENCES posts (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- 部署
INSERT INTO
  departments (name)
VALUES
  ('総務部'),
  ('人事部'),
  ('経理部'),
  ('営業部'),
  ('マーケティング部'),
  ('システム開発部'),
  ('カスタマーサポート部'),
  ('経営企画部');

-- カテゴリーグループ
INSERT INTO
  category_groups(name)
VALUES
  ('小物・アクセサリー'),
  ('カード・書類系'),
  ('貴重品'),
  ('デジタル機器'),
  ('食べ物・日用品'),
  ('その他');

-- 各カテゴリー内容
INSERT INTO
  categories (group_id, name)
VALUES
  -- 小物・アクセサリー
  (1, 'ハンカチ'),
  (1, '小物入れ'),
  (1, '文房具'),
  (1, 'メガネ'),
  (1, '化粧品'),
  (1, '傘'),
  -- カード・書類系
  (2, 'カード類'),
  (2, '書籍類'),
  -- 貴重品
  (3, '財布'),
  (3, '時計'),
  (3, '鍵'),
  -- デジタル機器
  (4, 'スマートフォン'),
  (4, '電子機器'),
  (4, 'イヤホン'),
  -- 食べ物・日用品
  (5, '水筒・弁当箱'),
  (5, 'バッグ'),
  (5, '医薬品'),
  (5, '衣類'),
  -- その他
  (6, 'その他');

-- ユーザー情報の登録
INSERT INTO
  users (name, email, password, department_id, role)
VALUES
  (
    'admin',
    'admin@example.com',
    '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244',
    1,
    'admin'
  ),
  (
    '鈴木二郎',
    'jiro@example.com',
    '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244',
    2,
    'user'
  );

-- 投稿内容
INSERT INTO
  posts (
    user_id,
    category_id,
    found_date,
    found_place,
    description
  )
VALUES
  (
    1,
    1,
    '2026-04-25',
    '2階女性トイレ',
    '白地でレースが施されている。Mの刺繍が1か所あり。'
  ),
  (
    1,
    2,
    '2026-04-27',
    '3F休憩室',
    '白猫がプリントされた紺色のポーチ。'
  ),
  (
    1,
    3,
    '2026-05-08',
    '第1会議室',
    '茶色のリングノートとカラフルな正方形の付箋。'
  );

INSERT INTO
  images (post_id, image_path)
VALUES
  (1, 'static/uploads/handkerchief.png'),
  (2, 'static/uploads/pouch.jpg'),
  (3, 'static/uploads/stationery1.jpg'),
  (3, 'static/uploads/stationery2.jpg');
