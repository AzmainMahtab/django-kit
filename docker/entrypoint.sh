#!/bin/bash
set -e

# Wait for the database to be ready.
python - <<PY
import os
import socket
import time

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))

print(f"Waiting for PostgreSQL at {host}:{port}...")
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=1):
            print("PostgreSQL is available.")
            break
    except OSError:
        time.sleep(1)
else:
    raise RuntimeError("PostgreSQL did not become available in time.")
PY

# Coordinate migrations across containers with a PostgreSQL advisory lock.
python - <<PY
import os
import sys

import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ.get("DJANGO_SETTINGS_MODULE", "backend.core.settings.base_settings"))
django.setup()

from django.db import connection

MIGRATION_LOCK_ID = 42_424_242

print("Acquiring migration lock...")
with connection.cursor() as cursor:
    cursor.execute("SELECT pg_advisory_lock(%s);", [MIGRATION_LOCK_ID])

try:
    print("Applying migrations...")
    from django.core.management import call_command
    call_command("migrate", "--noinput")
finally:
    print("Releasing migration lock...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_unlock(%s);", [MIGRATION_LOCK_ID])
PY

# Collect static files. This may fail on read-only dev mounts, so ignore errors.
python manage.py collectstatic --noinput --clear >/dev/null 2>&1 || true

exec "$@"
