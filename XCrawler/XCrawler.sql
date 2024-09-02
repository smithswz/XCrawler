/*
 Navicat Premium Dump SQL

 Source Server         : wsl
 Source Server Type    : PostgreSQL
 Source Server Version : 150008 (150008)
 Source Host           : 172.31.20.39:5432
 Source Catalog        : XData
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 150008 (150008)
 File Encoding         : 65001

 Date: 02/09/2024 14:10:26
*/


-- ----------------------------
-- Sequence structure for account_num
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."account_num";
CREATE SEQUENCE "public"."account_num" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."id_seq";
CREATE SEQUENCE "public"."id_seq" 
INCREMENT 1
MAXVALUE 9223372036854775807
CACHE 1;

-- ----------------------------
-- Table structure for X_Information
-- ----------------------------
DROP TABLE IF EXISTS "public"."X_Information";
CREATE TABLE "public"."X_Information" (
  "id" int4 NOT NULL DEFAULT nextval('id_seq'::regclass),
  "url" varchar(255) COLLATE "pg_catalog"."default",
  "target_id" varchar(255) COLLATE "pg_catalog"."default",
  "stop_time" varchar(255) COLLATE "pg_catalog"."default",
  "status" int2 DEFAULT nextval('id_seq'::regclass)
)
;
COMMENT ON COLUMN "public"."X_Information"."id" IS 'ID';
COMMENT ON COLUMN "public"."X_Information"."url" IS '目标url';
COMMENT ON COLUMN "public"."X_Information"."target_id" IS '目标账号的user_id';
COMMENT ON COLUMN "public"."X_Information"."stop_time" IS '采集帖子最新的时间';
COMMENT ON COLUMN "public"."X_Information"."status" IS '0为正在采集
1为停止采集
2为user_id出现变更需要刷新';

-- ----------------------------
-- Table structure for X_account
-- ----------------------------
DROP TABLE IF EXISTS "public"."X_account";
CREATE TABLE "public"."X_account" (
  "id" int4 NOT NULL DEFAULT nextval('account_num'::regclass),
  "email" varchar(255) COLLATE "pg_catalog"."default",
  "email_passwd" varchar(255) COLLATE "pg_catalog"."default",
  "passwd" varchar(255) COLLATE "pg_catalog"."default",
  "cookie" text COLLATE "pg_catalog"."default",
  "status" int2,
  "get_num" int8
)
;
COMMENT ON COLUMN "public"."X_account"."id" IS 'ID';
COMMENT ON COLUMN "public"."X_account"."email" IS '账号邮箱';
COMMENT ON COLUMN "public"."X_account"."email_passwd" IS '账号邮箱密码';
COMMENT ON COLUMN "public"."X_account"."passwd" IS '账号密码';
COMMENT ON COLUMN "public"."X_account"."cookie" IS 'cookie信息';
COMMENT ON COLUMN "public"."X_account"."status" IS '账号状态：
状态为0，账号正常
状态为1，账号被429临时禁用
状态为2，账号异常';
COMMENT ON COLUMN "public"."X_account"."get_num" IS '记录账号使用次数';

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
SELECT setval('"public"."account_num"', 1, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
SELECT setval('"public"."id_seq"', 3, true);

-- ----------------------------
-- Primary Key structure for table X_Information
-- ----------------------------
ALTER TABLE "public"."X_Information" ADD CONSTRAINT "X_Information_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table X_account
-- ----------------------------
ALTER TABLE "public"."X_account" ADD CONSTRAINT "X_account_pkey" PRIMARY KEY ("id");
