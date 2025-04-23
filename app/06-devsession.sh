#!/bin/bash
# DESC: Launches a tmux session with 4 panes:
#        Pane 0: Backend (8000, green, top-left)
#        Pane 1: WebSocket (8001, blue, top-middle)
#        Pane 2: Frontend (3000, cyan, top-right)
#        Pane 3: Simulator (python script, yellow, bottom-right)
# VERSION: 0P.2B.05

SESSION="parco-dev"

# Kill any previous session with the same name
tmux kill-session -t $SESSION 2>/dev/null

# Start new tmux session (Pane 0 - Backend)
tmux new-session -d -s $SESSION -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.0 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.0 'export PS1="\[\033[1;32m\][Backend:8000]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.0 'uvicorn app:app --host 0.0.0.0 --port 8000 --reload --log-level debug' C-m

# Split horizontally from Pane 0 → Pane 1 (WebSocket backend)
tmux split-window -h -t $SESSION:0.0 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.1 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.1 'export PS1="\[\033[1;34m\][WebSocket:8001]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.1 'uvicorn manager.websocket:app --host 0.0.0.0 --port 8001 --reload --log-level debug' C-m

# Split horizontally from Pane 1 → Pane 2 (Frontend React app)
tmux split-window -h -t $SESSION:0.1 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.2 'export PS1="\[\033[1;36m\][Frontend:3000]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.2 'npm start' C-m

# Split vertically under Pane 2 → Pane 3 (Simulator)
tmux split-window -v -t $SESSION:0.2 -c ~/parco_fastapi/app
tmux send-keys -t $SESSION.3 'source ~/parco_fastapi/venv/bin/activate' C-m
tmux send-keys -t $SESSION.3 'export PS1="\[\033[1;33m\][Simulator]\[\033[0m\] \w $ "' C-m
tmux send-keys -t $SESSION.3 'python /home/parcoadmin/parco_fastapi/app/manager/simulator.py' C-m

# Balance layout
tmux select-layout -t $SESSION tiled

# Attach session
tmux attach-session -t $SESSION
