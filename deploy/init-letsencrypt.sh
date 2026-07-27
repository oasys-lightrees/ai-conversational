#!/usr/bin/env bash
# Bootstrap a Let's Encrypt certificate for the reverse proxy, then start nginx.
# Run once per domain, from this deploy/ directory, after DNS points at the host.
#
#   export DOMAIN=example.com EMAIL=you@example.com
#   ./init-letsencrypt.sh
#
# Env:
#   DOMAIN   (required)  the domain to secure
#   EMAIL    (optional)  contact email for Let's Encrypt notices
#   STAGING  (optional)  set to 1 while testing to avoid hitting rate limits
set -e

DOMAIN="${DOMAIN:?Set DOMAIN, e.g. export DOMAIN=example.com}"
EMAIL="${EMAIL:-}"
STAGING="${STAGING:-0}"
COMPOSE="docker compose -f docker-compose.prod.yml"
data_path="./certbot"
rsa_key_size=4096

if [ -d "$data_path/conf/live/$DOMAIN" ]; then
  read -p "Existing certificate for $DOMAIN found. Replace? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
fi

if [ ! -s "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -f "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Copying recommended TLS parameters from the Certbot image..."

  mkdir -p "$data_path/conf"

  docker run --rm \
    -v "$PWD/$data_path/conf:/output" \
    --entrypoint sh certbot/certbot \
    -c "
      cp /opt/certbot/src/certbot/src/certbot/_internal/plugins/nginx/tls_configs/options-ssl-nginx.conf /output/ &&
      cp /opt/certbot/src/certbot/src/certbot/ssl-dhparams.pem /output/
    "
fi

echo "### Creating a dummy certificate so nginx can start ..."
live_path="/etc/letsencrypt/live/$DOMAIN"
mkdir -p "$data_path/conf/live/$DOMAIN"
$COMPOSE run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1 \
    -keyout '$live_path/privkey.pem' \
    -out '$live_path/fullchain.pem' \
    -subj '/CN=localhost'" certbot

echo "### Starting nginx ..."
$COMPOSE up --force-recreate -d nginx

echo "### Removing the dummy certificate ..."
$COMPOSE run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$DOMAIN && \
  rm -Rf /etc/letsencrypt/archive/$DOMAIN && \
  rm -Rf /etc/letsencrypt/renewal/$DOMAIN.conf" certbot

echo "### Requesting the Let's Encrypt certificate ..."
email_arg="--register-unsafely-without-email"
[ -n "$EMAIL" ] && email_arg="--email $EMAIL"
staging_arg=""
[ "$STAGING" != "0" ] && staging_arg="--staging"

$COMPOSE run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg $email_arg \
    -d $DOMAIN \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --non-interactive \
    --force-renewal" certbot

echo "### Reloading nginx ..."
$COMPOSE exec nginx nginx -s reload

echo "### Done. Bring up the full stack with:"
echo "    $COMPOSE up -d"
echo "    $COMPOSE exec backend python -m backend.database.init_db"
