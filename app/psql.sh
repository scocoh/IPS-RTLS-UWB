# Name: psql.sh
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Shell script for ParcoRTLS utilities
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Dependent: TRUE

#!/bin/bash
# DESC: Opens a psql session to the 'parco' database as the 'postgres' user
# VERSION 0P.1B.01

echo "🐘 Connecting to PostgreSQL database 'parco' as user 'postgres'..."
psql -U postgres -d parco
