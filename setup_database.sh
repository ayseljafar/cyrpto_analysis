#!/bin/bash

set -e

# Credentials
DB_USER="ayseljafar"
DB_PASSWORD="crypto86"
DB_NAME="crypto_prices"

# Drop DB and user
psql postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" || true
psql postgres -c "DROP USER IF EXISTS $DB_USER;" || true

#  user and database
psql postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
psql postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# TimescaleDB and permissions
psql $DB_NAME -c "CREATE EXTENSION IF EXISTS timescaledb;"
psql $DB_NAME -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;"
psql $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;"
psql $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"
