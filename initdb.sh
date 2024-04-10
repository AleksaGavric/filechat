#!/bin/bash
set -e

# Create the 'usconstitution' database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE usconstitution;
EOSQL

# Connect to the 'usconstitution' database and create the 'vector' extension
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "usconstitution" <<-EOSQL
    CREATE EXTENSION vector;
EOSQL
