#!/bin/bash
# Name: 06-devsession.sh
# Version: 0.1.4
# Created: 971201
# Modified: 250719
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Shell script for ParcoRTLS utilities
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Dependent: TRUE
# Note: Do not run this script simultaneously with 21-start-servers.sh, as they both use ports 8001-8004 and will conflict.

# DESC: Launches a tmux session with 6 panes:
#        Pane 0: Backend (8000, green, top-left)
#        Pane 1: WebSocket Control (8001, blue, top-middle)
#        Pane 2: WebSocket RealTimeData (8002, purple, top-middle)
#        Pane 3: WebSocket HistoricalData (8003, magenta, top-middle)
#        Pane 4: WebSocket AveragedData (8004, orange, top-middle)
#        Pane 5: Frontend (3000, cyan, top-right)
#        Pane 6: Simulator (python script, yellow, bottom-right)
# VERSION: 0P.2B.08
# Previous: Added panes for all WebSocket servers (ports 8001-8004) (0P.2B.07)

SESSION="parco-dev"

# Function to check if a port is in use
check_port() {
    local port=$1
    if netstat -tuln 2>/dev/null | grep -q ":${port}\b.*LISTEN"; then
        echo "Error: Port ${port} is already in use. Stop any processes using this port (e.g., servers started by 21-start-servers.sh) and try again."
        return 1
    fi
    return 0
}

# Check ports before starting servers
ports=(8000 8001 8002 8003 8004 3000)
for port in "${ports[@]}"; do
    if ! check_port $port; then
        exit 1
    fi
done

# Kill any previous session with the same name
tmux kill-session -t $SESSION 2>/dev/null

# Start new tmux session (Pane 0 - Backend)
tmux new-session -d -s $SESSION -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.0 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.0 'export PS1="\[\033[1;32m\][Backend:8000]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.0 'uvicorn app:app --host 0.0.0.0 --port 8000 --reload' C-m

# Split horizontally from Pane 0 → Pane 1 (WebSocket Control)
tmux split-window -h -t $SESSION:0.0 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.1 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.1 'export PS1="\[\033[1;34m\][WebSocket:8001]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.1 'uvicorn manager.websocket_control:app --host 0.0.0.0 --port 8001 --reload' C-m

# Split horizontally from Pane 1 → Pane 2 (WebSocket RealTimeData)
tmux split-window -h -t $SESSION:0.1 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.2 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.2 'export PS1="\[\033[1;35m\][WebSocket:8002]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.2 'uvicorn manager.websocket_realtime:app --host 0.0.0.0 --port 8002 --reload' C-m

# Split horizontally from Pane 2 → Pane 3 (WebSocket HistoricalData)
tmux split-window -h -t $SESSION:0.2 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.3 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.3 'export PS1="\[\033[1;31m\][WebSocket:8003]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.3 'uvicorn manager.websocket_historical:app --host 0.0.0.0 --port 8003 --reload' C-m

# Split horizontally from Pane 3 → Pane 4 (WebSocket AveragedData)
tmux split-window -h -t $SESSION:0.3 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.4 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.4 'export PS1="\[\033[1;33m\][WebSocket:8004]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.4 'uvicorn manager.websocket_averaged:app --host 0.0.0.0 --port 8004 --reload' C-m

# Split vertically from Pane 4 → Pane 5 (Frontend React app)
tmux split-window -v -t $SESSION:0.4 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.5 'export PS1="\[\033[1;36m\][Frontend:3000]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.5 'npm start' C-m

# Split vertically under Pane 5 → Pane 6 (Simulator)
tmux split-window -v -t $SESSION:0.5 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.6 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.6 'export PS1="\[\033[1;33m\][Simulator]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.6 'python /home/parcoadmin/parco_fastapi/app/manager/simulator.py' C-m

# Balance layout
tmux select-layout -t $SESSION tiled

# Attach session
tmux attach-session -t $SESSION