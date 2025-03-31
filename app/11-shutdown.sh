#!/bin/bash
# DESC: Stops backend, frontend, Mosquitto, and PostgreSQL services, syncs filesystem, and shuts down server
# VERSION 0P.1B.01

# Define log file
LOG_FILE="/home/parcoadmin/parco_fastapi/app/shutdown.log"

echo "[INFO] Shutting down ParcoRTLS services..." | tee -a "$LOG_FILE"

# Stop the ParcoRTLS backend service
if systemctl is-active --quiet parco_backend.service; then
    echo "[INFO] Stopping parco_backend.service..." | tee -a "$LOG_FILE"
    sudo systemctl stop parco_backend.service
else
    echo "[INFO] parco_backend.service is already stopped." | tee -a "$LOG_FILE"
fi

# Stop the ParcoRTLS frontend service
if systemctl is-active --quiet parco_frontend.service; then
    echo "[INFO] Stopping parco_frontend.service..." | tee -a "$LOG_FILE"
    sudo systemctl stop parco_frontend.service
else
    echo "[INFO] parco_frontend.service is already stopped." | tee -a "$LOG_FILE"
fi

# Stop the MQTT broker (Mosquitto) if running
if systemctl is-active --quiet mosquitto; then
    echo "[INFO] Stopping Mosquitto MQTT Broker..." | tee -a "$LOG_FILE"
    sudo systemctl stop mosquitto
else
    echo "[INFO] Mosquitto service is already stopped." | tee -a "$LOG_FILE"
fi

# Stop the PostgreSQL database service
if systemctl is-active --quiet postgresql; then
    echo "[INFO] Stopping PostgreSQL database..." | tee -a "$LOG_FILE"
    sudo systemctl stop postgresql
else
    echo "[INFO] PostgreSQL database is already stopped." | tee -a "$LOG_FILE"
fi

# Sync filesystem to prevent data loss
echo "[INFO] Syncing filesystem..." | tee -a "$LOG_FILE"
sync

# Confirm shutdown
echo "[INFO] System will shut down in 10 seconds. Press Ctrl+C to cancel." | tee -a "$LOG_FILE"
sleep 10

# Shut down the system
echo "[INFO] Shutting down now..." | tee -a "$LOG_FILE"
sudo shutdown -h now