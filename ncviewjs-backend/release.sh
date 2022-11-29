#!/usr/bin/env bash

# Run database migrations
echo "Running database migrations..."

/opt/conda/bin/aerich migrate
/opt/conda/bin/aerich upgrade
/opt/conda/bin/aerich inspectdb -t store

# exit 123
