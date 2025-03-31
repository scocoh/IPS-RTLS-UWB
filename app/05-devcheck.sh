#!/bin/bash
# VERSION 0P.2B.01 — Dev Process Inspector
# Created: 2025-03-30 21:08:03
# DESC: Checks for running processes on ports 3000, 8000, 8001 and identifies zombies or conflicts

echo "🩺 ParcoRTLS Dev Health Check"
echo "============================"

PORTS=(3000 8000 8001)
PROBLEMS=0

for PORT in "${PORTS[@]}"; do
  echo -e "\n🔎 Checking port $PORT..."
  PID=$(lsof -ti tcp:$PORT)

  if [ -z "$PID" ]; then
    echo "✅ Port $PORT is free."
  else
    STATE=$(ps -o state= -p $PID | awk '{print $1}')
    USER=$(ps -o user= -p $PID)
    CMD=$(ps -o cmd= -p $PID)

    echo "⚠️  Port $PORT is in use by PID $PID"
    echo "    User: $USER"
    echo "    State: $STATE"
    echo "    Command: $CMD"

    case "$STATE" in
      D)
        echo "🛑 WARNING: PID $PID is stuck in uninterruptible sleep (D)."
        echo "   This may be a zombie Node.js process. A hard reboot may be required."
        PROBLEMS=1
        ;;
      Z)
        echo "☠️  WARNING: PID $PID is a zombie (Z). Should be reaped by parent."
        PROBLEMS=1
        ;;
      *)
        echo "ℹ️  Process appears normal."
        ;;
    esac
  fi
done

echo -e "\n📋 Summary:"

if [ $PROBLEMS -eq 0 ]; then
  echo "✅ All development ports are healthy and ready."
else
  echo "⚠️  Issues were detected. Review the output above and take action."
fi

exit $PROBLEMS
