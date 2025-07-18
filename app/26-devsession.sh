#!/bin/bash
# Name: 26-devsession.sh
# Version: 0.1.1
# Created: 250712
# Modified: 250713
# Creator: ParcoAdmin
# Modified By: ParcoAdmin + Claude
# Description: Dashboard tmux dev session: websocket_dashboard + websocket_realtime + AllTraq + wscat clients for dashboard testing
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Dependent: TRUE
# Note: Dashboard development session with port 8008 for dashboard WebSocket, port 18002 for AllTraq, and test clients
# Changelog:
# - 0.1.1 (250713): Added AllTraq service on port 18002 in pane 1, fixed to work properly
# - 0.1.0 (250712): Initial version based on 25-devsession.sh for dashboard development

# DESC: Dashboard development session with WebSocket servers and test clients for dashboard integration testing

SESSION="dashboard-dev"
LOGDIR="/home/parcoadmin/logs"

# Ensure log directory exists
mkdir -p "$LOGDIR"

# Function to check if a port is in use
check_port() {
    local port=$1
    if netstat -tuln 2>/dev/null | grep -q ":${port}\b.*LISTEN"; then
        echo "Error: Port ${port} is already in use (port $port)."
        echo "DEBUG: Port check failed for $port at $(date)" >> "$LOGDIR/debug.log"
        return 1
    fi
    echo "DEBUG: Port $port is available at $(date)" >> "$LOGDIR/debug.log"
    return 0
}

# Function to wait for a port to be ready
wait_for_port() {
    local port=$1
    local max_attempts=30
    local attempt=1
    echo "DEBUG: Waiting for port $port to be ready at $(date)" >> "$LOGDIR/debug.log"
    while ! netstat -tuln 2>/dev/null | grep -q ":${port}\b.*LISTEN"; do
        if [ $attempt -ge $max_attempts ]; then
            echo "Error: Timeout waiting for port $port to be ready after $max_attempts seconds."
            echo "DEBUG: Timeout waiting for port $port at $(date)" >> "$LOGDIR/debug.log"
            return 1
        fi
        echo "DEBUG: Port $port not ready, attempt $attempt/$max_attempts at $(date)" >> "$LOGDIR/debug.log"
        sleep 1
        ((attempt++))
    done
    echo "DEBUG: Port $port is ready at $(date)" >> "$LOGDIR/debug.log"
    return 0
}

# Check ports before starting (Dashboard: 8008, AllTraq: 18002, assume 8002 exists from parco-dev)
for port in 8008 18002; do
    if ! check_port $port; then exit 1; fi
done

tmux kill-session -t $SESSION 2>/dev/null

# Pane 0: websocket_dashboard.py (port 8008)
tmux new-session -d -s $SESSION -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.0 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.0 'export PS1="\[\033[1;35m\][DASHBOARD:8008]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.0 'uvicorn manager.websocket_dashboard:app --host 0.0.0.0 --port 8008 --reload --log-level debug' C-m

# Pane 1: AllTraq WebSocket (port 18002)
tmux split-window -h -t $SESSION:0.0 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.1 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.1 'export PS1="\[\033[1;32m\][ALLTRAQ:18002]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.1 'uvicorn manager.websocket_alltraq:app --host 0.0.0.0 --port 18002 --reload --log-level debug' C-m

# Pane 2: AllTraq Service Control
tmux split-window -h -t $SESSION:0.1 -c ~/parco_fastapi/app/DataSources/AllTraqAppAPI
tmux send-keys -t $SESSION.2 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.2 'export PS1="\[\033[1;33m\][ALLTRAQ-SERVICE]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.2 'echo "AllTraq Service Control:"' C-m
tmux send-keys -t $SESSION.2 'echo "  START: python alltraq_service.py"' C-m
tmux send-keys -t $SESSION.2 'echo "  STOP:  Ctrl+C"' C-m
tmux send-keys -t $SESSION.2 'echo ""' C-m

# Pane 3: wscat to Dashboard Customer 1 (port 8008)
tmux split-window -h -t $SESSION:0.2 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.3 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.3 'export PS1="\[\033[1;36m\][WSCAT:DASH-CUST1]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.3 'echo "DEBUG: Starting wscat for Dashboard Customer 1 at $(date)" >> '"$LOGDIR/debug.log" C-m
tmux send-keys -t $SESSION.3 'until netstat -tuln 2>/dev/null | grep -q ":8008\b.*LISTEN"; do sleep 1; done' C-m
tmux send-keys -t $SESSION.3 'wscat -c ws://192.168.210.226:8008/ws/dashboard/1' C-m
tmux send-keys -t $SESSION.3 'echo "Connected to Dashboard Customer 1. Send ping with: {\"type\": \"ping\"}"' C-m
tmux send-keys -t $SESSION.3 'sync' C-m

# Pane 4: wscat to AllTraq Manager (port 18002)
tmux split-window -h -t $SESSION:0.3 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.4 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.4 'export PS1="\[\033[1;31m\][WSCAT:ALLTRAQ]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.4 'echo "DEBUG: Starting wscat for AllTraq Manager at $(date)" >> '"$LOGDIR/debug.log" C-m
tmux send-keys -t $SESSION.4 'echo "Waiting for AllTraq service on port 18002..."' C-m
tmux send-keys -t $SESSION.4 'until netstat -tuln 2>/dev/null | grep -q ":18002\b.*LISTEN"; do echo "Port 18002 not ready, waiting..."; sleep 2; done' C-m
tmux send-keys -t $SESSION.4 'wscat -c ws://192.168.210.226:18002/ws/AllTraqManager' C-m
tmux send-keys -t $SESSION.4 'echo "Send BeginStream: {\"type\": \"request\", \"request\": \"BeginStream\", \"reqid\": \"alltraq_test\", \"params\": [{\"id\": \"ALLTRAQ1\", \"data\": \"true\"}], \"zone_id\": 417}"' C-m
tmux send-keys -t $SESSION.4 'sync' C-m

# Pane 5: RealTime WebSocket Monitor (port 8002) - Monitor existing service
tmux split-window -h -t $SESSION:0.4 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.5 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.5 'export PS1="\[\033[1;34m\][WSCAT:REALTIME]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.5 'echo "DEBUG: Waiting for existing RealTime Manager (port 8002) at $(date)" >> '"$LOGDIR/debug.log" C-m
tmux send-keys -t $SESSION.5 'echo "Waiting for existing RealTime service on port 8002..."' C-m
tmux send-keys -t $SESSION.5 'until netstat -tuln 2>/dev/null | grep -q ":8002\b.*LISTEN"; do echo "Port 8002 not ready, waiting..."; sleep 2; done' C-m
tmux send-keys -t $SESSION.5 'wscat -c ws://192.168.210.226:8002/ws/RealTimeManager' C-m
tmux send-keys -t $SESSION.5 'echo "Send BeginStream: {\"type\": \"request\", \"request\": \"BeginStream\", \"reqid\": \"rt_test\", \"params\": [{\"id\": \"SIM1\", \"data\": \"true\"}], \"zone_id\": 417}"' C-m
tmux send-keys -t $SESSION.5 'sync' C-m

# Pane 6: Dashboard Log Monitor - Real-time dashboard activity
tmux split-window -v -t $SESSION:0.5 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.6 'export PS1="\[\033[1;31m\][DASH-LOGS]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.6 'echo "Dashboard Log Monitor - Real-time activity"' C-m
tmux send-keys -t $SESSION.6 'echo "Waiting for dashboard server to start..."' C-m
tmux send-keys -t $SESSION.6 'until [ -f /home/parcoadmin/parco_fastapi/app/logs/websocket_dashboard.log ]; do sleep 1; done' C-m
tmux send-keys -t $SESSION.6 'tail -f /home/parcoadmin/parco_fastapi/app/logs/websocket_dashboard.log' C-m

# Balance layout
tmux select-layout -t $SESSION tiled

echo "Dashboard Development Session Starting..."
echo "======================================"
echo "Session: $SESSION"
echo "Requirements: parco-dev session must be running (./06-devsession.sh)"
echo "Panes:"
echo "  0: Dashboard WebSocket Server (port 8008)"
echo "  1: AllTraq WebSocket Service (port 18002)"
echo "  2: AllTraq Service Control - Manual Start/Stop"
echo "  3: Dashboard Customer 1"
echo "  4: AllTraq Manager"
echo "  5: RealTime Manager"
echo "  6: Dashboard Log Monitor"
echo ""
echo "Prerequisites:"
echo "  1. Run: ./06-devsession.sh (for ports 8000-8004 and frontend)"
echo "  2. Then run: ./26-devsession.sh (this script)"
echo ""
echo "Test Commands:"
echo "  Pane 2: python alltraq_service.py (to start), Ctrl+C (to stop)"
echo "  Pane 3: {\"type\": \"ping\"}"
echo "  Pane 4: {\"type\": \"request\", \"request\": \"BeginStream\", \"reqid\": \"alltraq_test\", \"params\": [{\"id\": \"ALLTRAQ1\", \"data\": \"true\"}], \"zone_id\": 417}"
echo "  Pane 5: {\"type\": \"request\", \"request\": \"BeginStream\", \"reqid\": \"rt_test\", \"params\": [{\"id\": \"SIM1\", \"data\": \"true\"}], \"zone_id\": 417}"
echo ""

# Attach
tmux attach-session -t $SESSION