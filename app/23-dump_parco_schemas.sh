# Name: 23-dump_parco_schemas.sh
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS utility script
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Dependent: TRUE

#!/bin/bash

# Set PostgreSQL credentials
export PGPASSWORD="parcoMCSE04106!"
USER="parcoadmin"
HOST="localhost"

# List of databases to dump
DATABASES=("ParcoRTLSMaint" "ParcoRTLSHistR" "ParcoRTLSHistO" "ParcoRTLSHistP" "ParcoRTLSData")

# Directory to store schema dumps
mkdir -p ~/parco_schemas
cd ~/parco_schemas

echo "Dumping schemas..."
for DB in "${DATABASES[@]}"; do
  echo "Dumping $DB..."
  pg_dump -U "$USER" -h "$HOST" -s -d "$DB" -f "${DB}_schema.sql"
done

# Optional: Create markdown-style table lists
echo "Generating markdown table lists..."
for DB in "${DATABASES[@]}"; do
  echo "Database: $DB" > "${DB}_tables.md"
  psql -U "$USER" -h "$HOST" -d "$DB" -c "\dt" >> "${DB}_tables.md"
done

echo "Schema extraction complete. Files are in ~/parco_schemas"

