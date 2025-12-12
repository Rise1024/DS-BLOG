/*
 Navicat Premium Dump SQL

 Source Server         : ds
 Source Server Type    : SQLite
 Source Server Version : 3045000 (3.45.0)
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3045000 (3.45.0)
 File Encoding         : 65001

 Date: 12/12/2025 11:20:41
*/

PRAGMA
foreign_keys = false;

-- ----------------------------
-- Table structure for article_question_relations
-- ----------------------------
DROP TABLE IF EXISTS "article_question_relations";
CREATE TABLE "article_question_relations"
(
    id          INTEGER  NOT NULL,
    article_id  INTEGER  NOT NULL,
    question_id INTEGER  NOT NULL,
    created_at  DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (article_id, question_id),
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
);

-- ----------------------------
-- Table structure for article_tags
-- ----------------------------
DROP TABLE IF EXISTS "article_tags";
CREATE TABLE "article_tags"
(
    article_id INTEGER NOT NULL,
    tag_id     INTEGER NOT NULL,
    PRIMARY KEY (article_id, tag_id),
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
);

-- ----------------------------
-- Table structure for articles
-- ----------------------------
DROP TABLE IF EXISTS "articles";
CREATE TABLE "articles"
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT,
    content     TEXT,
    category_id INTEGER,
    tags        TEXT,
    created_at  TEXT,
    updated_at  TEXT,
    view_count  INTEGER DEFAULT 0,
    "order"     INTEGER DEFAULT 0,
    author      TEXT,
    cover       TEXT,
    is_top      INTEGER DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES blog_categories (id) ON DELETE SET NULL
);

-- ----------------------------
-- Table structure for blog_categories
-- ----------------------------
DROP TABLE IF EXISTS "blog_categories";
CREATE TABLE "blog_categories"
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    parent_id   INTEGER NULL REFERENCES "blog_categories"(id) ON DELETE SET NULL,
    description TEXT,
    "order"     INTEGER       DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (parent_id, name)
);

-- ----------------------------
-- Table structure for categories
-- ----------------------------
DROP TABLE IF EXISTS "categories";
CREATE TABLE categories
(
    id          INTEGER      NOT NULL,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id   INTEGER,
    "order"     INTEGER,
    created_at  DATETIME     NOT NULL,
    updated_at  DATETIME     NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (parent_id) REFERENCES categories (id) ON DELETE SET NULL
);

-- ----------------------------
-- Table structure for feedbacks
-- ----------------------------
DROP TABLE IF EXISTS "feedbacks";
CREATE TABLE feedbacks
(
    id           INTEGER     NOT NULL,
    user_id      INTEGER,
    content      TEXT        NOT NULL,
    contact      VARCHAR(200),
    status       VARCHAR(20) NOT NULL,
    created_at   DATETIME    NOT NULL,
    processed_at DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- ----------------------------
-- Table structure for knowledge_points
-- ----------------------------
DROP TABLE IF EXISTS "knowledge_points";
CREATE TABLE knowledge_points
(
    id          INTEGER      NOT NULL,
    category_id INTEGER      NOT NULL,
    title       VARCHAR(500) NOT NULL,
    "order"     INTEGER,
    created_at  DATETIME     NOT NULL,
    updated_at  DATETIME     NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
);

-- ----------------------------
-- Table structure for question_favorites
-- ----------------------------
DROP TABLE IF EXISTS "question_favorites";
CREATE TABLE question_favorites
(
    id          INTEGER  NOT NULL,
    user_id     INTEGER  NOT NULL,
    question_id INTEGER  NOT NULL,
    created_at  DATETIME NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_user_question_favorite UNIQUE (user_id, question_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
);

-- ----------------------------
-- Table structure for question_tags
-- ----------------------------
DROP TABLE IF EXISTS "question_tags";
CREATE TABLE question_tags
(
    question_id INTEGER NOT NULL,
    tag_id      INTEGER NOT NULL,
    PRIMARY KEY (question_id, tag_id),
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
);

-- ----------------------------
-- Table structure for questions
-- ----------------------------
DROP TABLE IF EXISTS "questions";
CREATE TABLE questions
(
    id          INTEGER      NOT NULL,
    category_id INTEGER,
    type        VARCHAR(20)  NOT NULL,
    title       VARCHAR(500) NOT NULL,
    content     TEXT         NOT NULL,
    answer      TEXT         NOT NULL,
    explanation TEXT,
    difficulty  INTEGER      NOT NULL,
    created_at  DATETIME     NOT NULL,
    updated_at  DATETIME     NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
);

-- ----------------------------
-- Table structure for sqlite_sequence
-- ----------------------------
DROP TABLE IF EXISTS "sqlite_sequence";
CREATE TABLE sqlite_sequence
(
    name,
    seq
);

-- ----------------------------
-- Table structure for tags
-- ----------------------------
DROP TABLE IF EXISTS "tags";
CREATE TABLE tags
(
    id         INTEGER     NOT NULL,
    name       VARCHAR(50) NOT NULL,
    count      INTEGER,
    created_at DATETIME    NOT NULL,
    PRIMARY KEY (id)
);

-- ----------------------------
-- Table structure for user_tokens
-- ----------------------------
DROP TABLE IF EXISTS "user_tokens";
CREATE TABLE user_tokens
(
    id         INTEGER      NOT NULL,
    user_id    INTEGER      NOT NULL,
    token      VARCHAR(256) NOT NULL,
    expires_at DATETIME     NOT NULL,
    created_at DATETIME     NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS "users";
CREATE TABLE "users"
(
    id            INTEGER                      NOT NULL,
    openid        VARCHAR(128),
    username      VARCHAR(64),
    password_hash VARCHAR(128),
    nickname      VARCHAR(64),
    avatar_url    VARCHAR(256),
    role          VARCHAR(64)                  NOT NULL,
    created_at    DATETIME                     NOT NULL,
    last_login    DATETIME                     NOT NULL,
    user_type     VARCHAR(16) DEFAULT 'wechat' NOT NULL,
    PRIMARY KEY (id)
);

-- ----------------------------
-- Auto increment value for articles
-- ----------------------------
UPDATE "main"."sqlite_sequence"
SET seq = 5
WHERE name = 'articles';

-- ----------------------------
-- Indexes structure for table articles
-- ----------------------------
CREATE INDEX "main"."idx_articles_category_id"
    ON "articles" (
                   "category_id" ASC
        );
CREATE INDEX "main"."idx_articles_created_at"
    ON "articles" (
                   "created_at" ASC
        );

-- ----------------------------
-- Auto increment value for blog_categories
-- ----------------------------
UPDATE "main"."sqlite_sequence"
SET seq = 8
WHERE name = 'blog_categories';

-- ----------------------------
-- Indexes structure for table categories
-- ----------------------------
CREATE INDEX "main"."ix_categories_parent_id"
    ON "categories" (
                     "parent_id" ASC
        );

-- ----------------------------
-- Indexes structure for table feedbacks
-- ----------------------------
CREATE INDEX "main"."ix_feedbacks_user_id"
    ON "feedbacks" (
                    "user_id" ASC
        );

-- ----------------------------
-- Indexes structure for table knowledge_points
-- ----------------------------
CREATE INDEX "main"."ix_knowledge_points_category_id"
    ON "knowledge_points" (
                           "category_id" ASC
        );

-- ----------------------------
-- Indexes structure for table question_favorites
-- ----------------------------
CREATE INDEX "main"."ix_question_favorites_question_id"
    ON "question_favorites" (
                             "question_id" ASC
        );
CREATE INDEX "main"."ix_question_favorites_user_id"
    ON "question_favorites" (
                             "user_id" ASC
        );

-- ----------------------------
-- Indexes structure for table questions
-- ----------------------------
CREATE INDEX "main"."ix_questions_category_id"
    ON "questions" (
                    "category_id" ASC
        );

-- ----------------------------
-- Indexes structure for table tags
-- ----------------------------
CREATE UNIQUE INDEX "main"."ix_tags_name"
    ON "tags" (
               "name" ASC
        );

-- ----------------------------
-- Indexes structure for table user_tokens
-- ----------------------------
CREATE UNIQUE INDEX "main"."ix_user_tokens_token"
    ON "user_tokens" (
                      "token" ASC
        );
CREATE INDEX "main"."ix_user_tokens_user_id"
    ON "user_tokens" (
                      "user_id" ASC
        );

PRAGMA
foreign_keys = true;
