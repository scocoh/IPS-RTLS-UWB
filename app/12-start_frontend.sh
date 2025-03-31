#!/bin/bash
# DESC: Standalone wrapper to launch React frontend cleanly from tmux
# VERSION: 0P.1B.01

cd ~/parco_fastapi/app || exit 1
source ~/parco_fastapi/venv/bin/activate

echo "[$(date)] Starting frontend with npm start..." >> tmux_frontend.log
PORT=3000 BROWSER=none /usr/bin/npm start >> tmux_frontend.log 2>&1
