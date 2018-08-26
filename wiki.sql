CREATE TABLE IF NOT EXISTS "wiki_article" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "ip_address" VARCHAR(32) NOT NULL,
    "content" TEXT NOT NULL,
    "content_html" TEXT NOT NULL,
    "time_create" DATETIME NOT NULL,
    "time_edit" DATETIME NOT NULL,
    "links" TEXT NOT NULL, 
    "markdown" TEXT);

CREATE TABLE IF NOT EXISTS "wiki_history" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "ip_address" VARCHAR(32) NOT NULL,
    "content" TEXT NOT NULL,
    "time" DATETIME NOT NULL,
    "type" VARCHAR(16) NOT NULL
);

CREATE TABLE IF NOT EXISTS "admin_only_articles" (
    "id" INTEGER NOT NULL PRIMARY KEY
);
