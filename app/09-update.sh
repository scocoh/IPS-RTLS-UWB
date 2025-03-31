#!/bin/bash
# DESC: Updates system packages, Python venv packages, and optionally reboots after upgrade
# VERSION 0P.2B.01

PROJECT_DIR="/home/parcoadmin/parco_fastapi/app"
GIT_REPO="https://github.com/scocoh/IPS-RTLS-UWB.git"
BRANCH="main"
AUTO_UPDATE_FILE="$PROJECT_DIR/.auto_update"
LOG_FILE="$HOME/parco_fastapi/logs/update_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "📦 Updating ParcoRTLS deployment..."
echo "⏱️  $(date)" | tee -a "$LOG_FILE"
cd "$PROJECT_DIR" || exit 1

# Prompt or use existing auto-update preference
if [ -f "$AUTO_UPDATE_FILE" ]; then
  AUTO_UPDATE=$(cat "$AUTO_UPDATE_FILE")
else
  echo "🔄 Would you like automatic updates in the future? (yes/no)" | tee -a "$LOG_FILE"
  read -r AUTO_UPDATE
  echo "$AUTO_UPDATE" > "$AUTO_UPDATE_FILE"
fi

# Function to show update diff
show_update_summary() {
  echo "🔍 Checking for remote changes..." | tee -a "$LOG_FILE"
  git fetch origin $BRANCH
  git log HEAD..origin/$BRANCH --oneline | tee -a "$LOG_FILE"
}

# Function to apply updates
apply_updates() {
  echo "📥 Pulling latest updates..." | tee -a "$LOG_FILE"
  git reset --hard origin/$BRANCH >> "$LOG_FILE" 2>&1
  git pull origin $BRANCH >> "$LOG_FILE" 2>&1
  echo "✅ Codebase updated." | tee -a "$LOG_FILE"

  # Optional: Update PostgreSQL functions
  if [ -f "$PROJECT_DIR/sql/update_functions.sql" ]; then
    echo "🧠 Found database function update script. Apply to PostgreSQL? (yes/no)"
    read -r CONFIRM_SQL
    if [ "$CONFIRM_SQL" == "yes" ]; then
      echo "📡 Applying SQL updates to PostgreSQL..." | tee -a "$LOG_FILE"
      psql -U postgres -f "$PROJECT_DIR/sql/update_functions.sql" >> "$LOG_FILE" 2>&1
      echo "✅ PostgreSQL functions updated." | tee -a "$LOG_FILE"
    else
      echo "⚠️  Skipped database function update." | tee -a "$LOG_FILE"
    fi
  fi

  # Restart backend/frontend if services exist
  if systemctl list-units --full -all | grep -q "parco_backend.service"; then
    echo "🔁 Restarting backend..." | tee -a "$LOG_FILE"
    sudo systemctl restart parco_backend.service
  fi
  if systemctl list-units --full -all | grep -q "parco_frontend.service"; then
    echo "🔁 Restarting frontend..." | tee -a "$LOG_FILE"
    sudo systemctl restart parco_frontend.service
  fi
}

# Main update logic
if [ "$AUTO_UPDATE" == "yes" ]; then
  apply_updates
else
  show_update_summary
  echo "🛠️  Apply these updates? (yes/no)"
  read -r PROCEED
  if [ "$PROCEED" == "yes" ]; then
    apply_updates
  else
    echo "🚫 Update canceled." | tee -a "$LOG_FILE"
    exit 0
  fi
fi

# Optional reboot
echo "🔄 Would you like to reboot now? (yes/no)"
read -r REBOOT
if [ "$REBOOT" == "yes" ]; then
  echo "🚨 Rebooting system in 5 seconds..." | tee -a "$LOG_FILE"
  sleep 5
  sudo reboot
else
  echo "✅ Update complete. Reboot skipped." | tee -a "$LOG_FILE"
fi
