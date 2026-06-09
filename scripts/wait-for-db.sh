#!/usr/bin/env bash
# Wait for MySQL to be ready
set -e

host="${MYSQL_HOST:-localhost}"
port="${MYSQL_PORT:-3306}"
user="${MYSQL_USER:-root}"
password="${MYSQL_ROOT_PASSWORD:-example}"
timeout=30

echo "Waiting for MySQL at $host:$port..."
for i in $(seq 1 $timeout); do
    if mysqladmin ping -h"$host" -P"$port" -u"$user" -p"$password" --silent; then
        echo "MySQL is ready!"
        exit 0
    fi
    echo -n "."
    sleep 1
done
echo ""
echo "MySQL not ready after $timeout seconds."
exit 1