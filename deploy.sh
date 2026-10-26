#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/bfl/IoclMobile_app/IOCL-mobile-app-backend"
IMAGE="ioclback"
WEB="ioclback"
WORKER="iocl_stage_worker_new"

cd "$APP_DIR"

PREV_COMMIT=$(git rev-parse HEAD)

# If anything fails before the swap, put the code back and keep old containers running
on_fail() {
  echo "!! Deploy failed before swap. Restoring code to $PREV_COMMIT"
  git reset --hard "$PREV_COMMIT"
}
trap on_fail ERR

echo ">> Pull latest code"
git fetch origin main
git reset --hard origin/main

echo ">> Tag current image as rollback"
docker tag $IMAGE:latest $IMAGE:previous 2>/dev/null || true

echo ">> Build new image"
docker build -t $IMAGE:latest .

echo ">> Run migrations (one-off container)"
docker run --rm --network iocl-network --env-file .env $IMAGE:latest \
  python manage.py migrate --noinput

start_web() {
  docker rm -f $WEB 2>/dev/null || true
  docker run -d --name $WEB --restart unless-stopped \
    --network iocl-network -p 127.0.0.1:8000:8000 \
    --env-file .env "$1" \
    python -m gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 \
      --worker-class gthread --worker-tmp-dir /dev/shm --timeout 120 \
      --access-logfile - --error-logfile - \
      iocl_backend.wsgi:application
}

start_worker() {
  docker rm -f $WORKER 2>/dev/null || true
  docker run -d --name $WORKER --restart unless-stopped \
    --network iocl-network \
    -v "$APP_DIR":/app --env-file .env "$1" \
    python manage.py process_stage_batches
}

healthy() {
  for i in $(seq 1 20); do
    code=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/ || true)
    # any HTTP response below 500 means gunicorn is up
    if [ -n "$code" ] && [ "$code" != "000" ] && [ "$code" -lt 500 ]; then
      return 0
    fi
    sleep 3
  done
  return 1
}

trap - ERR   # from here on we handle failures explicitly

echo ">> Swap web + worker"
start_web $IMAGE:latest
start_worker $IMAGE:latest

if healthy; then
  echo ">> Healthy. Deploy OK."
  docker image prune -f
else
  echo "!! Health check failed. Rolling back."
  docker logs --tail 50 $WEB || true
  git reset --hard "$PREV_COMMIT"
  start_web $IMAGE:previous
  start_worker $IMAGE:previous
  exit 1
fi
