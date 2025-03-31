#!/bin/bash
# DESC: Cleanly stops any process on port 3000 and starts the React frontend (npm start)
# VERSION: 0P.2B.02

cd ~/parco_fastapi/app || exit 1

PORT="${1:-3000}"
AUTO_YES="$2"

echo "🔍 Checking for process using port $PORT..."

PID=$(lsof -ti tcp:$PORT)

if [ -z "$PID" ]; then
  echo "✅ Port $PORT is free."
else
  echo "⚠️  Port $PORT is in use by PID: $PID"
  OWNER=$(ps -o user= -p "$PID")
  echo "   Process owner: $OWNER"

  if [ "$OWNER" = "$USER" ]; then
    echo "🛑 Killing process $PID..."
    kill -9 "$PID"
    sleep 1
  else
    echo "⛔ You do not own this process. Try running with sudo or investigate further."
    exit 1
  fi
fi

# Export flag to prevent interactive prompt
if [ "$AUTO_YES" == "--yes" ]; then
  export BROWSER=none
  echo "✅ Auto mode: Suppressing browser launch and answering prompts."
  yes | npm start
else
  echo "🚀 Starting app with npm start..."
  npm start
fi
