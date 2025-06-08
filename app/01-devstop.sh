# Name: 01-devstop.sh
# Version: 0.1.1
# Created: 971201
# Modified: 250604
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Shell script for ParcoRTLS utilities
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Dependent: TRUE

#!/bin/bash
# DESC: Stops the tmux session, kills processes on ports 3000/8000/8001, and clears dev environment

SESSION="parco-dev"
PORTS=("3000" "8000" "8001" "8002" "8003" "8004" "8005" "8006" "8007" "8998" "9000")

echo "🛑 Stopping tmux session: $SESSION..."
tmux kill-session -t $SESSION 2>/dev/null

echo "🧹 Cleaning up processes on ports: ${PORTS[*]}..."
for PORT in "${PORTS[@]}"; do
    PID=$(lsof -ti tcp:$PORT)
    if [ ! -z "$PID" ]; then
        echo "⚠️  Port $PORT is in use by PID $PID. Killing..."
        kill -9 $PID || echo "Failed to kill PID $PID"
    else
        echo "✅ Port $PORT is already free."
    fi
done

echo "🧼 Killing leftover node/npm processes..."
pkill -f "react-scripts/scripts/start.js"
pkill -f "node .*start.js"

echo "✅ Development environment shut down cleanly."
