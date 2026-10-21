#!/usr/bin/env bash
# Idempotent deploy with automatic rollback. Run on the target host.
# Required env: IMAGE (ideally image@sha256:digest), DOMAIN
set -euo pipefail
: "${IMAGE:?}" "${DOMAIN:?}"
export IMAGE DOMAIN

PREV="$(cat .current_image 2>/dev/null || true)"
echo "Deploying ${IMAGE} (previous: ${PREV:-none})"

docker compose pull
if docker compose up -d --remove-orphans --wait --wait-timeout 90; then
  echo "${IMAGE}" > .current_image
  docker image prune -f >/dev/null
  echo "Deploy OK"
else
  echo "Deploy FAILED" >&2
  docker compose logs --tail=50 qr-service >&2 || true
  if [ -n "${PREV}" ]; then
    echo "Rolling back to ${PREV}" >&2
    IMAGE="${PREV}" docker compose up -d --remove-orphans --wait --wait-timeout 90
  fi
  exit 1
fi
