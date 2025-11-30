#!/bin/sh
set -e

SSL_CERT=/etc/nginx/ssl/cert.pem
SSL_KEY=/etc/nginx/ssl/key.pem
TEMPLATE=/etc/nginx/conf.d/ssl.conf.template
OUT=/etc/nginx/conf.d/ssl.conf

echo "[nginx entrypoint] checking for SSL cert/key..."

if [ -f "$SSL_CERT" ] && [ -f "$SSL_KEY" ]; then
  echo "[nginx entrypoint] SSL certificate and key found: enabling HTTPS"
  if [ -f "$TEMPLATE" ]; then
    cp "$TEMPLATE" "$OUT"
    echo "[nginx entrypoint] copied ssl template to $OUT"
    # Validate nginx configuration
    nginx -t
  else
    echo "[nginx entrypoint] ssl template not found at $TEMPLATE — skipping HTTPS enable"
  fi
else
  echo "[nginx entrypoint] SSL cert or key missing — leaving HTTPS disabled"
  if [ -f "$OUT" ]; then
    rm -f "$OUT"
    echo "[nginx entrypoint] removed existing $OUT"
  fi
fi

echo "[nginx entrypoint] starting nginx..."
exec nginx -g 'daemon off;'
