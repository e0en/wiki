CREATE TABLE IF NOT EXISTS "articles" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "url_name" VARCHAR(100) NOT NULL,
    "ip_address" VARCHAR(32) NOT NULL,
    "content" TEXT NOT NULL,
    "content_html" TEXT NOT NULL,
    "time_create" DATETIME NOT NULL,
    "time_edit" DATETIME NOT NULL,
    "links" TEXT NOT NULL,
    "markdown" TEXT,
    "is_public" INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS "histories" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "ip_address" VARCHAR(32) NOT NULL,
    "content" TEXT NOT NULL,
    "time" DATETIME NOT NULL,
    "type" VARCHAR(16) NOT NULL
);

CREATE TABLE IF NOT EXISTS "users" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "hashed_pw" TEXT NOT NULL,
    "salt" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "links" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "from_name" VARCHAR(100) NOT NULL,
    "to_name" VARCHAR(100) NOT NULL
);
