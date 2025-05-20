#!/bin/bash
# Name: 21-start-servers.sh
# Version: 0.1.6
# Created: 250513
# Modified: 250516
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Shell script to start ParcoRTLS WebSocket servers with logging and port checking
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Dependent: FALSE
# Note: Do not run this script simultaneously with 06-devsession.sh, as they both use ports 8001-8007 and will conflict.

# Ensure we're in the correct directory
cd /home/parcoadmin/parco_fastapi/app

# Create logs directory if it doesn't exist
mkdir -p logs

# Activate the virtual environment
source ../venv/bin/activate

# Function to check if a port is in use
check_port() {
    local port=$1
    if netstat -tuln 2>/dev/null | grep -q ":${port}\b.*LISTEN"; then
        echo "Error: Port ${port} is already in use. Stop any processes using this port (e.g., kill tmux session 'parco-dev' if running 06-devsession.sh) and try again."
        return 1
    fi
    return 0
}

# Check ports before starting servers
ports=(8001 8002 8003 8004 8005 8006 8007)
for port in "${ports[@]}"; do
    if ! check_port $port; then
        exit 1
    fi
done

# Start WebSocket servers in the background with logging
echo "Starting WebSocket Control server on port 8001..."
nohup uvicorn manager.websocket_control:app --host 0.0.0.0 --port 8001 --log-config /home/parcoadmin/parco_fastapi/app/logging_config.ini >> /home/parcoadmin/parco_fastapi/app/logs/websocket_control.log 2>&1 &

echo "Starting WebSocket RealTimeData server on port 8002..."
nohup uvicorn manager.websocket_realtime:app --host 0.0.0.0 --port 8002 --log-config /home/parcoadmin/parco_fastapi/app/logging_config.ini >> /home/parcoadmin/parco_fastapi/app/logs/websocket_realtime.log 2>&1 &

echo "Starting WebSocket HistoricalData server on port 8003..."
nohup uvicorn manager.websocket_historical:app --host 0.0.0.0 --port 8003 --log-config /home/parcoadmin/parco_fastapi/app/logging_config.ini >> /home/parcoadmin/parco_fastapi/app/logs/websocket_historical.log 2>&1 &

echo "Starting WebSocket AveragedData server on port 8004..."
nohup uvicorn manager.websocket_averaged:app --host 0.0.0.0 --port 8004 --log-config /home/parcoadmin/parco_fastapi/app/logging_config.ini >> /home/parcoadmin/parco_fastapi/app/logs/websocket_averaged.log 2>&1 &

echo "Starting WebSocket Subscription server on port 8005..."
nohup uvicorn manager.websocket_subscription:app --host 0.0.0.0 --port 8005 --log-config /home/parcoadmin/parco_fastapi/app/logging_config.ini >> /home/parcoadmin/parco_fastapi/app/logs/websocket_subscription.log 2>&1 &

echo "Starting WebSocket OData server on port 8006..."
nohup uvicorn manager.websocket_odata:app --host 0.0.0.0 --port 8006 --log-config /home/parcoadmin/parco_fastapi/app/logging_config.ini >> /home/parcoadmin/parco_fastapi/app/logs/websocket_odata.log 2>&1 &

echo "Starting WebSocket SensorData server on port 8007..."
nohup uvicorn manager.websocket_sensordata:app --host 0.0.0.0 --port 8007 --log-config /home/parcoadmin/parco_fastapi/app/logging_config.ini >> /home/parcoadmin/parco_fastapi/app/logs/websocket_sensordata.log 2>&1 &

echo "All WebSocket servers started. Logs are in the 'logs' directory."