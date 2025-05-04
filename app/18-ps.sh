# Name: 18-ps.sh
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
# DESC: Runs ps to list running processes
# VERSION 0P.1B.01

echo "Listing processes with ps..."
ps aux
echo "Press Enter to return to the menu..."
read
