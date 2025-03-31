#!/bin/bash
# DESC: Checks port usage for 3000, 8000, 8001 with PID, owner, and command info

PORTS=(3000 8000 8001)
echo "🔍 Checking critical dev ports: ${PORTS[*]}"
echo "---------------------------------------------"

for PORT in "${PORTS[@]}"; do
  PID=$(lsof -ti tcp:$PORT)
  
  if [ -z "$PID" ]; then
    echo "✅ Port $PORT is free."
  else
    OWNER=$(ps -o user= -p $PID | tail -n 1)
    CMD=$(ps -p $PID -o cmd=)
    echo "⚠️  Port $PORT is in use!"
    echo "    ├─ PID   : $PID"
    echo "    ├─ User  : $OWNER"
    echo "    └─ Cmd   : $CMD"
    echo
  fi
done

echo "🧩 Suggestion: If ports are stuck, run: devstop"
