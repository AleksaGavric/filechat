#!/bin/bash
set -e

# Set the PostgreSQL connection parameters
export PGHOST=localhost
export PGPORT=5432
export PGUSER=postgres
export PGPASSWORD=postgres
export PGDATABASE=usconstitution

# Create the 'documents' database
psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE documents;"

# Connect to the 'documents' database and create the 'vector' extension
psql -v ON_ERROR_STOP=1 -d documents -c "CREATE EXTENSION vector;"
