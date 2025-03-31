#!/bin/bash
# DESC: Interactive menu to stop dev stack, system services, or fully shut down and reboot

# VERSION 0P.1B.01
LOG_FILE="/home/parcoadmin/parco_fastapi/app/shutdown.log"

function stop_dev() {
    echo "[INFO] Stopping development environment..." | tee -a "$LOG_FILE"
    ~/parco_fastapi/app/devstop.sh
}

function stop_services() {
    echo "[INFO] Stopping ParcoRTLS system services..." | tee -a "$LOG_FILE"

    SERVICES=(parco_backend.service parco_frontend.service mosquitto postgresql)

    for service in "${SERVICES[@]}"; do
        if systemctl is-active --quiet "$service"; then
            echo "[INFO] Stopping $service..." | tee -a "$LOG_FILE"
            sudo systemctl stop "$service"
        else
            echo "[INFO] $service is already stopped." | tee -a "$LOG_FILE"
        fi
    done

    echo "[INFO] Syncing filesystem..." | tee -a "$LOG_FILE"
    sync
}

function menu() {
    clear
    echo "=============================="
    echo " ParcoRTLS Shutdown Menu"
    echo "=============================="
    echo "1) Stop dev environment only"
    echo "2) Stop system services and shut down"
    echo "3) Stop everything and reboot"
    echo "4) Cancel"
    echo
    read -p "Select an option [1-4]: " choice

    case $choice in
        1)
            stop_dev
            ;;
        2)
            stop_services
            echo "[INFO] System will shut down in 10 seconds. Press Ctrl+C to cancel." | tee -a "$LOG_FILE"
            sleep 10
            sudo shutdown -h now
            ;;
        3)
            stop_dev
            stop_services
            echo "[INFO] System will reboot in 10 seconds. Press Ctrl+C to cancel." | tee -a "$LOG_FILE"
            sleep 10
            sudo reboot
            ;;
        4)
            echo "🟢 Cancelled. No action taken."
            ;;
        *)
            echo "❌ Invalid option. Exiting."
            ;;
    esac
}

menu
