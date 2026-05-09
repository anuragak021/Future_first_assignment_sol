#!/bin/sh
set -e

PORT="${PORT:-80}"
BACKEND_URL="${BACKEND_URL:-http://backend.railway.internal:8000}"

export PORT BACKEND_URL

# Substitute only our vars; nginx's $uri $host $remote_addr etc. are untouched
envsubst '${PORT} ${BACKEND_URL}' \
    < /etc/nginx/conf.d/default.conf.template \
    > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
