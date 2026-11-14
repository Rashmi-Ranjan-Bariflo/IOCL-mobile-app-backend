#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/bfl/IoclMobile_app/IOCL-mobile-app-backend"
ENV_MASTER="/home/bfl/env-store/backend.env"
IMAGE="ioclback"
WEB="ioclback"
WORKER="iocl_stage_worker_new"
MQTT="iocl_mqtt_worker"
NETWORK="iocl-network"

cd "$APP_DIR"
git checkout main
PREV_COMMIT=$(git rev-parse HEAD)

restore_env() { [ -f "$ENV_MASTER" ] && cp -p "$ENV_MASTER" .env || true; }

on_fail() {
  echo "!! Failed before swap. Restoring code."
  git reset --hard "$PREV_COMMIT"; restore_env
}
trap on_fail ERR

echo ">> Pull latest code"
git fetch origin main
git reset --hard origin/main
restore_env

echo ">> Keep current image as rollback"
docker tag $IMAGE:latest $IMAGE:previous 2>/dev/null || true

echo ">> Build new image"
docker build -t $IMAGE:latest .

echo ">> Run migrations"
docker run --rm --network $NETWORK --env-file .env $IMAGE:latest \
  python manage.py migrate --noinput

trap - ERR

start_web() {
  docker rm -f $WEB 2>/dev/null || true
  docker run -d --name $WEB --restart unless-stopped \
    --network $NETWORK -p 127.0.0.1:8000:8000 \
    --env-file .env "$1" \
    python -m gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 \
      --worker-class gthread --worker-tmp-dir /dev/shm --timeout 120 \
      --access-logfile - --error-logfile - \
      iocl_backend.wsgi:application
}

start_worker() {
  docker rm -f $WORKER 2>/dev/null || true
  docker run -d --name $WORKER --restart unless-stopped \
    --network $NETWORK \
    -v "$APP_DIR":/app --env-file .env "$1" \
    python manage.py process_stage_batches
}

start_mqtt() {
  docker stop -t 20 $MQTT 2>/dev/null || true
  docker rm -f $MQTT 2>/dev/null || true
  docker run -d --name $MQTT --restart unless-stopped \
    --network $NETWORK \
    --log-opt max-size=10m --log-opt max-file=3 \
    -v "$APP_DIR":/app --env-file .env "$1" \
    python manage.py mqtt_worker
}

web_healthy() {
  for i in $(seq 1 20); do
    code=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/ || true)
    if [ -n "$code" ] && [ "$code" != "000" ] && [ "$code" -lt 500 ]; then return 0; fi
    sleep 3
  done
  return 1
}

mqtt_ok() {
  [ "$(docker inspect -f '{{.State.Running}} {{.RestartCount}}' $MQTT 2>/dev/null)" = "true 0" ]
}

echo ">> Swap web + workers"
start_web $IMAGE:latest
start_worker $IMAGE:latest
start_mqtt $IMAGE:latest
sleep 15

if web_healthy; then
  echo ">> Web healthy."
  docker image prune -f
  if mqtt_ok; then
    echo ">> MQTT worker running. Deploy OK."
  else
    echo "!! MQTT worker is not stable (web is fine and stays up):"
    docker logs --tail 30 $MQTT || true
    exit 1
  fi
else
  echo "!! Web health check failed. Rolling back."
  docker logs --tail 50 $WEB || true
  git reset --hard "$PREV_COMMIT"; restore_env
  start_web $IMAGE:previous
  start_worker $IMAGE:previous
  if [ -f mqtt/management/commands/mqtt_worker.py ]; then
    start_mqtt $IMAGE:previous
  else
    docker rm -f $MQTT 2>/dev/null || true
  fi
  exit 1
fi
