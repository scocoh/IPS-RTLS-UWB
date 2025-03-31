#!/bin/bash
# DESC: Opens a psql session to the 'parco' database as the 'postgres' user
# VERSION 0P.1B.01

echo "🐘 Connecting to PostgreSQL database 'parco' as user 'postgres'..."
psql -U postgres -d parco
