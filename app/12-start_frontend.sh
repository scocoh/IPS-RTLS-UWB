# Name: 12-start_frontend.sh
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
# DESC: Standalone wrapper to launch React frontend cleanly from tmux
# VERSION: 0P.1B.01

cd ~/parco_fastapi/app || exit 1
source ~/parco_fastapi/venv/bin/activate

echo "[$(date)] Starting frontend with npm start..." >> tmux_frontend.log
PORT=3000 BROWSER=none /usr/bin/npm start >> tmux_frontend.log 2>&1
