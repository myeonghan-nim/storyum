#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------
# ssl_generator.sh
# 프로젝트 루트에서 실행하세요.
# ---------------------------------------------------

# 1) 스크립트 위치 기준으로 프로젝트 루트 계산
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 2) SSL 저장 디렉터리
NGINX_SSL_DIR="$ROOT_DIR/nginx/ssl"
APP_SSL_DIR="$ROOT_DIR/app/ssl"
PG_SSL_DIR="$ROOT_DIR/postgresql/ssl"

# 3) 디렉터리 생성
mkdir -p "$NGINX_SSL_DIR" "$APP_SSL_DIR" "$PG_SSL_DIR"

# 4) 기존 .srl 파일 삭제 (재생성을 위해)
rm -f "$NGINX_SSL_DIR"/storyum_internal_ca.srl

echo "▶ Generating Nginx HTTPS cert (localhost)..."
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout "$NGINX_SSL_DIR/storyum_nginx.key" \
  -out    "$NGINX_SSL_DIR/storyum_nginx.crt" \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=Storyum/CN=localhost"

echo "▶ Generating internal CA (for app & postgres)..."
openssl genrsa -out "$NGINX_SSL_DIR/storyum_internal_ca.key" 2048
openssl req -x509 -new -nodes -sha256 -days 365 \
  -key   "$NGINX_SSL_DIR/storyum_internal_ca.key" \
  -out   "$NGINX_SSL_DIR/storyum_internal_ca.crt" \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=Storyum-Internal-CA/CN=storyum-internal-ca"

echo "▶ Generating app (Gunicorn/Django) cert for storyum_web..."
openssl genrsa -out "$APP_SSL_DIR/storyum_web.key" 2048
openssl req -new \
  -key   "$APP_SSL_DIR/storyum_web.key" \
  -out   "$APP_SSL_DIR/storyum_web.csr" \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=Storyum/CN=storyum_web"

cat > "$APP_SSL_DIR/web_ext.cnf" <<EOF
subjectAltName = DNS:storyum_web
EOF

openssl x509 -req \
  -in      "$APP_SSL_DIR/storyum_web.csr" \
  -CA      "$NGINX_SSL_DIR/storyum_internal_ca.crt" \
  -CAkey   "$NGINX_SSL_DIR/storyum_internal_ca.key" \
  -CAcreateserial \
  -out     "$APP_SSL_DIR/storyum_web.crt" \
  -days 365 -sha256 \
  -extfile "$APP_SSL_DIR/web_ext.cnf"

chmod 600 "$APP_SSL_DIR/storyum_web.key"

echo "▶ Generating Postgres cert for storyum_db..."
openssl genrsa -out "$PG_SSL_DIR/storyum_db.key" 2048
openssl req -new \
  -key   "$PG_SSL_DIR/storyum_db.key" \
  -out   "$PG_SSL_DIR/storyum_db.csr" \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=Storyum-DB/CN=storyum_db"

cat > "$PG_SSL_DIR/db_ext.cnf" <<EOF
subjectAltName = DNS:storyum_db
EOF

openssl x509 -req \
  -in      "$PG_SSL_DIR/storyum_db.csr" \
  -CA      "$NGINX_SSL_DIR/storyum_internal_ca.crt" \
  -CAkey   "$NGINX_SSL_DIR/storyum_internal_ca.key" \
  -CAcreateserial \
  -out     "$PG_SSL_DIR/storyum_db.crt" \
  -days 365 -sha256 \
  -extfile "$PG_SSL_DIR/db_ext.cnf"

chmod 600 "$PG_SSL_DIR/storyum_db.key"

echo "✅ All certificates generated successfully."
