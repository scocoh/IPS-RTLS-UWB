#!/bin/bash
# Name: 25-devsession.sh
# Version: 0.1.3
# Created: 250526
# Modified: 250719
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: TETSE tmux dev session: websocket_tetse + psql + wscat clients
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Note: Added wscat commands for panes 2-5 with delays for ports 8998, 9000; port 8002 not checked as managed by parco-dev
# Changelog:
# - 0.1.3 (250719): Removed --log-level debug from uvicorn commands; bumped version
# - 0.1.2 (250607): Added wait_for_port to delay wscat in panes 3-5 until ports 8998, 9000 are ready; bumped version
# - 0.1.1 (250607): Updated panes 2-5 with wscat commands; reverted port check to 8998, 9000
# - 0.1.0 (250526): Initial version with websocket_tetse and psql

SESSION="tetse-dev"
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

# Check ports before starting
for port in 8998 9000; do
    if ! check_port $port; then exit 1; fi
done

tmux kill-session -t $SESSION 2>/dev/null

# Pane 0: websocket_tetse_event.py (port 9000)
tmux new-session -d -s $SESSION -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.0 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.0 'export PS1="\[\033[1;35m\][TETSE-EVENT:9000]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.0 'uvicorn manager.websocket_tetse_event:app --host 0.0.0.0 --port 9000' C-m

# Pane 1: websocket_tetse.py (port 8998)
tmux split-window -h -t $SESSION:0.0 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.1 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.1 'export PS1="\[\033[1;34m\][TETSE:8998]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.1 'uvicorn manager.websocket_tetse:app --host 0.0.0.0 --port 8998' C-m

# Pane 2: wscat to RealTimeManager (port 8002)
# Original:
# tmux split-window -h -t $SESSION:0.1 -c ~/parco_fastapi/app
# tmux send-keys -t $SESSION.2 'source ~/parco_fastapi/venv/bin/activate' C-m
# tmux send-keys -t $SESSION.2 'export PS1="\[\033[1;32m\][TETSE-VENV2]\[\033[0m\] \w $ "' C-m
tmux split-window -h -t $SESSION:0.1 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.2 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.2 'export PS1="\[\033[1;32m\][WSCAT:8002]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.2 'echo "DEBUG: Starting wscat for RealTimeManager at $(date)" >> '"$LOGDIR/debug.log" C-m
tmux send-keys -t $SESSION.2 'wscat -c ws://192.168.210.226:8002/ws/RealTimeManager' C-m
tmux send-keys -t $SESSION.2 'echo "{\"type\": \"request\", \"request\": \"BeginStream\", \"reqid\": \"test_cli\", \"params\": [{\"id\": \"SIM1\", \"data\": \"true\"}, {\"id\": \"SIM2\", \"data\": \"true\"}], \"zone_id\": 417}"' C-m
tmux send-keys -t $SESSION.2 'sync' C-m

# Pane 3: wscat to tetse_event/test_entity (port 9000)
# Original:
# tmux split-window -h -t $SESSION:0.2 -c ~/parco_fastapi/app
# tmux send-keys -t $SESSION.3 'source ~/parco_fastapi/venv/bin/activate' C-m
# tmux send-keys -t $SESSION.3 'export PS1="\[\033[1;36m\][TETSE-VENV3]\[\033[0m\] \w $ "' C-m
tmux split-window -h -t $SESSION:0.2 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.3 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.3 'export PS1="\[\033[1;36m\][WSCAT:9000]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.3 'echo "DEBUG: Waiting for ports 8998, 9000 for pane 3 at $(date)" >> '"$LOGDIR/debug.log" C-m
tmux send-keys -t $SESSION.3 'until netstat -tuln 2>/dev/null | grep -q ":8998\b.*LISTEN" && netstat -tuln 2>/dev/null | grep -q ":9000\b.*LISTEN"; do sleep 1; done' C-m
tmux send-keys -t $SESSION.3 'echo "DEBUG: Starting wscat for tetse_event/test_entity at $(date)" >> '"$LOGDIR/debug.log" C-m
tmux send-keys -t $SESSION.3 'wscat -c ws://192.168.210.226:9000/ws/tetse_event/test_entity' C-m
tmux send-keys -t $SESSION.3 'sync' C-m

# Pane 4: wscat to forward_event (port 8998)
# Original:
# tmux split-window -h -t $SESSION:0.3 -c ~/parco_fastapi/app
# tmux send-keys -t $SESSION.4 'source ~/parco_fastapi/venv/bin/activate' C-m
# tmux send-keys -t $SESSION.4 'export PS1="\[\033[1;33m\][TETSE-VENV4]\[\033[0m\] \w $ "' C-m
tmux split-window -h -t $SESSION:0.3 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.4 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.4 'export PS1="\[\033[1;33m\][WSCAT:8998]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.4 'echo "DEBUG: Waiting for ports 8998, 9000 for pane 4 at $(date)" >> '"$LOGDIR/debug.log" C-m
tmux send-keys -t $SESSION.4 'until netstat -tuln 2>/dev/null | grep -q ":8998\b.*LISTEN" && netstat -tuln 2>/dev/null | grep -q ":9000\b.*LISTEN"; do sleep 1; done' C-m
tmux send-keys -t $SESSION.4 'echo "DEBUG: Starting wscat for forward_event at $(date)" >> '"$LOGDIR/debug.log" C-m
tmux send-keys -t $SESSION.4 'wscat -c ws://192.168.210.226:8998/ws/forward_event' C-m
tmux send-keys -t $SESSION.4 'sync' C-m

# Pane 5: wscat to tetse_event/test_entity (port 9000)
# Original:
# tmux split-window -h -t $SESSION:0.4 -c ~/parco_fastapi/app
# tmux send-keys -t $SESSION.5 'source ~/parco_fastapi/venv/bin/activate' C-m
# tmux send-keys -t $SESSION.5 'export PS1="\[\033[1;37m\][TETSE-VENV5]\[\033[0m\] \w $ "' C-m
tmux split-window -h -t $SESSION:0.4 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.5 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.5 'export PS1="\[\033[1;37m\][WSCAT:9000]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.5 'echo "DEBUG: Waiting for ports 8998, 9000 for pane 5 at $(date)" >> '"$LOGDIR/debug.log" C-m
tmux send-keys -t $SESSION.5 'until netstat -tuln 2>/dev/null | grep -q ":8998\b.*LISTEN" && netstat -tuln 2>/dev/null | grep -q ":9000\b.*LISTEN"; do sleep 1; done' C-m
tmux send-keys -t $SESSION.5 'echo "DEBUG: Starting wscat for tetse_event/test_entity at $(date)" >> '"$LOGDIR/debug.log" C-m
tmux send-keys -t $SESSION.5 'wscat -c ws://192.168.210.226:9000/ws/tetse_event/test_entity' C-m
tmux send-keys -t $SESSION.5 'sync' C-m

# Pane 6: psql (ParcoRTLSData)
tmux split-window -v -t $SESSION:0.5 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.6 'export PS1="\[\033[1;33m\][psql:ParcoRTLSData]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.6 'psql -U postgres -d ParcoRTLSData -h 127.0.0.1' C-m

# Balance layout
tmux select-layout -t $SESSION tiled

# Attach
tmux attach-session -t $SESSION