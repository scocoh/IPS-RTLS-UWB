#!/bin/bash
# VERSION 0P.1B.01

echo "Updating ParcoRTLS deployment"
# Add update logic here (to be filled in later)
# Set project directory
PROJECT_DIR="/home/parcoadmin/parco_fastapi/app"
GIT_REPO="https://github.com/scocoh/IPS-RTLS-UWB.git"
BRANCH="main"

# Check if user wants manual or auto updates
AUTO_UPDATE_FILE="$PROJECT_DIR/.auto_update"

# Function to update the system
update_system() {
    echo "Pulling latest updates from GitHub..."
    cd "$PROJECT_DIR" || exit 1

    # Fetch latest changes
    git fetch origin $BRANCH

    # Check if there are updates
    if git diff --quiet HEAD origin/$BRANCH; then
        echo "No updates found. Already up to date."
        return 0
    fi

    # Apply updates
    git reset --hard origin/$BRANCH
    git pull origin $BRANCH

    echo "Update complete."

    # Restart services if backend/frontend files changed
    if [ -f "/etc/systemd/system/parco_backend.service" ] || [ -f "/etc/systemd/system/parco_frontend.service" ]; then
        echo "Restarting ParcoRTLS services..."
        sudo systemctl restart parco_backend.service
        sudo systemctl restart parco_frontend.service
    fi

    echo "Update applied successfully."
}

# Check if auto-update is enabled
if [ -f "$AUTO_UPDATE_FILE" ]; then
    AUTO_UPDATE=$(cat "$AUTO_UPDATE_FILE")
else
    echo "Would you like automatic updates? (yes/no)"
    read -r AUTO_UPDATE
    echo "$AUTO_UPDATE" > "$AUTO_UPDATE_FILE"
fi

# Perform update if auto-update is enabled
if [ "$AUTO_UPDATE" == "yes" ]; then
    update_system
else
    echo "Manual update mode selected. Run './update.sh' to check for updates."
fi