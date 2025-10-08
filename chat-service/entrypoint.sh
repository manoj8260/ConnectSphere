#!/usr/bin/env sh
set -e

# Optional: wait for Postgres (no extra packages needed; uses asyncpg)
# Set DB_DSN like:
#   - For asyncpg directly:           postgresql://user:pass@host:5432/dbname
#   - For SQLAlchemy + async engine:  postgresql+asyncpg://user:pass@host:5432/dbname
if [ -n "$DB_DSN" ]; then
  echo "Waiting for DB at $DB_DSN ..."
  python - <<'PY'
import asyncio, os, sys
import asyncpg

dsn = os.getenv("DB_DSN")
async def wait_for_db():
    while True:
        try:
            conn = await asyncpg.connect(dsn)
            await conn.close()
            print("DB is ready")
            return
        except Exception as e:
            print(f"DB not ready yet: {e}")
            await asyncio.sleep(0.5)

asyncio.run(wait_for_db())
PY
fi

# Optional: run Alembic migrations (requires alembic in requirements)
if [ "${RUN_MIGRATIONS:-1}" != "0" ] && [ -f "alembic.ini" ]; then
  echo "Running Alembic migrations..."
  alembic upgrade head
fi

# Start the app
exec "$@"