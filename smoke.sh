#!/usr/bin/env bash
set -e
for url in \
  "https://lb2-analytics-service.onrender.com/health" \
  "https://lb2-users-service.onrender.com/health" \
  "https://lb2-tasks-service.onrender.com/health"; do
  echo "Checking $url"
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [ "$status" != "200" ]; then
    echo "FAIL: $url -> $status" >&2
    exit 1
  fi
done
echo "All health endpoints OK"
