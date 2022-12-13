#!/usr/bin/env bash

set -e

# Run database migrations
echo "Running database migrations..."
python -m alembic upgrade head

echo "release complete!"

echo "initalizing skyplane"

skyplane init -y --disable-config-azure --disable-config-gcp

echo "skyplane init setup complete"
