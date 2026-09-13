#!/bin/sh
# Creates a self-signed certificate for 'localhost' on the first start.
# The nginx image runs all scripts in /docker-entrypoint.d/ before Nginx starts.
set -e

SSL_DIR=/etc/nginx/ssl

if [ -f "$SSL_DIR/cert.pem" ] && [ -f "$SSL_DIR/key.pem" ]; then
    echo "$0: using the existing certificate in $SSL_DIR"
    exit 0
fi

mkdir -p "$SSL_DIR"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$SSL_DIR/key.pem" \
    -out "$SSL_DIR/cert.pem" \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

echo "$0: created a self-signed certificate in $SSL_DIR"
