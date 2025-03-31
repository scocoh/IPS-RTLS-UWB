#!/bin/bash
# DESC: Launches a tmux session with 3 panes: backend (8000), websocket (8001), and frontend (npm start)
# VERSION 0P.2B.03

SESSION="parco-dev"

# Kill any previous session with the same name
tmux kill-session -t $SESSION 2>/dev/null

# Start new session in ~/parco_fastapi/app
tmux new-session -d -s $SESSION -c ~/parco_fastapi/app

# Pane 1: Backend app server (port 8000)
tmux send-keys -t $SESSION.0 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.0 'cd ~/parco_fastapi/app' C-m
tmux send-keys -t $SESSION.0 'uvicorn app:app --host 0.0.0.0 --port 8000 --reload --log-level debug' C-m

# Pane 2: Split vertically for WebSocket backend (port 8001)
tmux split-window -v -t $SESSION -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.1 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.1 'cd ~/parco_fastapi/app' C-m
tmux send-keys -t $SESSION.1 'uvicorn manager.websocket:app --reload --host 0.0.0.0 --port 8001 --log-level debug' C-m

# Pane 3: Split horizontally from Pane 1 to run React frontend on port 3000 (with logging)
#tmux select-pane -t $SESSION.0
#tmux split-window -h -t $SESSION -c ~/parco_fastapi/app
#tmux send-keys -t $SESSION.2 './start_frontend.sh' C-m


# Arrange layout and attach
tmux select-layout -t $SESSION even-horizontal
tmux attach-session -t $SESSION
