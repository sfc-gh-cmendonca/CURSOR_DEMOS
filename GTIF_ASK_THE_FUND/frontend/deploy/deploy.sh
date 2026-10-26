#!/usr/bin/env bash
# Build the React app locally and deploy server + static build to the EC2 host.
# Usage: ./deploy.sh <ec2-public-ip> <ssh-key.pem> <snowflake-private-key.p8>
set -euo pipefail

HOST="$1"; SSH_KEY="$2"; SF_KEY="$3"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
SSH="ssh -i $SSH_KEY ec2-user@$HOST"

(cd "$HERE/web" && npm ci && npm run build)

$SSH 'mkdir -p ~/gtif_app/server/keys ~/gtif_app/web'
scp -i "$SSH_KEY" "$HERE/server/server.js" "$HERE/server/package.json" "$HERE/server/package-lock.json" "ec2-user@$HOST:~/gtif_app/server/"
scp -i "$SSH_KEY" -r "$HERE/web/dist" "ec2-user@$HOST:~/gtif_app/web/"
scp -i "$SSH_KEY" "$SF_KEY" "ec2-user@$HOST:~/gtif_app/server/keys/rsa_key.p8"
scp -i "$SSH_KEY" "$HERE/deploy/gtif-app.service" "$HERE/deploy/nginx-gtif.conf" "ec2-user@$HOST:/tmp/"

$SSH 'set -e
  chmod 700 ~/gtif_app/server/keys && chmod 600 ~/gtif_app/server/keys/rsa_key.p8
  cd ~/gtif_app/server && npm ci --omit=dev --silent
  sudo mv /tmp/gtif-app.service /etc/systemd/system/gtif-app.service
  sudo mv /tmp/nginx-gtif.conf /etc/nginx/conf.d/gtif.conf
  sudo systemctl daemon-reload
  sudo systemctl enable --now gtif-app nginx
  sudo systemctl restart gtif-app
  sudo nginx -t && sudo systemctl reload nginx
  sleep 2 && curl -sf http://127.0.0.1/api/health'
echo
echo "Deployed: http://$HOST/"
