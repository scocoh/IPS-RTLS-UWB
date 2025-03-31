#!/bin/bash
# DESC: Rebuilds Node.js environment and dependencies for ParcoRTLS frontend
# VERSION: 1.0.0

# TIPS FOR FUTURE SELF (parcoadmin):
# - This script rebuilds the frontend environment step-by-step.
# - At each step, you can choose to continue (y) or stop (n).
# - Step 1: Checks for uncommitted Git changes. You can save them to a new branch.
# - Step 3: Asks before deleting node_modules to prevent accidental loss.
# - If something goes wrong, check the output for errors and use these keywords to ask for help:
#   Keywords: "15-rebuild_stuff.sh", "node_modules", "Git uncommitted changes", "npm processes", "nvm install", "frontend start", "stop at step"
# - To see all branches (including backups), run: git branch
# - To switch to a backup branch, run: git checkout backup-<timestamp>

# Stop the script if any command fails
set -e

echo "Starting ParcoRTLS frontend rebuild..."

# Step 1: Check for uncommitted Git changes
echo "Step 1: Checking for uncommitted Git changes..."
if ! git status --porcelain | grep -q .; then
    echo "No uncommitted changes found."
else
    echo "Uncommitted changes found!"
    git status --short
    echo "Options:"
    echo "  1) Continue (may lose changes)"
    echo "  2) Save changes to a new branch and proceed"
    echo "  3) Stop the script"
    echo "  4) Save changes to a new branch and stop"
    read -p "Choose an option (1/2/3/4): " choice
    if [ "$choice" = "1" ]; then
        echo "Continuing... Changes may be lost."
    elif [ "$choice" = "2" ] || [ "$choice" = "4" ]; then
        # Save changes to a new branch
        CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        NEW_BRANCH="backup-$TIMESTAMP"
        echo "Saving changes to branch: $NEW_BRANCH"
        git checkout -b "$NEW_BRANCH"
        # Add all changes except this script
        git status --porcelain | grep -v "15-rebuild_stuff.sh" | while read -r line; do
            file=$(echo "$line" | awk '{print $2}')
            git add "$file"
        done
        # Check if there are changes to commit
        if git status --porcelain | grep -q .; then
            git commit -m "Saved changes on $TIMESTAMP"
        else
            echo "No changes to commit (excluding 15-rebuild_stuff.sh)."
        fi
        git checkout "$CURRENT_BRANCH"
        echo "Changes saved to $NEW_BRANCH."
        if [ "$choice" = "4" ]; then
            echo "Stopping the script."
            exit 0
        fi
    else
        echo "Stopping the script."
        exit 1
    fi
fi
read -p "Step 1 complete. Continue to next step? (y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Stopping the script after Step 1."
    exit 0
fi

# Step 2: Stop any running npm processes
echo "Step 2: Stopping npm processes..."
pkill -9 npm || echo "No npm processes to stop."
sleep 2
ps aux | grep npm || echo "No npm processes running."
read -p "Step 2 complete. Continue to next step? (y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Stopping the script after Step 2."
    exit 0
fi

# Step 3: Clear node_modules and lock files (with confirmation)
echo "Step 3: Clearing node_modules and lock files..."
if [ -d "node_modules" ] || [ -f "package-lock.json" ] || [ -f "yarn.lock" ]; then
    read -p "This will delete node_modules. Continue? (y/N): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        rm -rf node_modules package-lock.json yarn.lock
        echo "Cleared node_modules and lock files."
    else
        echo "Stopped the script."
        exit 1
    fi
else
    echo "No node_modules or lock files to clear."
fi
read -p "Step 3 complete. Continue to next step? (y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Stopping the script after Step 3."
    exit 0
fi

# Step 4: Install Node.js 20 using nvm
echo "Step 4: Setting up Node.js 20..."
if ! command -v nvm >/dev/null 2>&1; then
    echo "Installing nvm..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
fi
if [ -f "$HOME/.nvm/nvm.sh" ]; then
    source "$HOME/.nvm/nvm.sh"
else
    echo "Error: nvm not found. Please install it manually."
    exit 1
fi
nvm install 20
nvm use 20
node -v
read -p "Step 4 complete. Continue to next step? (y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Stopping the script after Step 4."
    exit 0
fi

# Step 5: Install dependencies
echo "Step 5: Installing dependencies..."
npm install --legacy-peer-deps
read -p "Step 5 complete. Continue to next step? (y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Stopping the script after Step 5."
    exit 0
fi

# Step 6: Start the frontend
echo "Step 6: Starting the frontend..."
npm start &
sleep 10
if curl -s http://localhost:3000 >/dev/null; then
    echo "Frontend started! Check http://<your-server-ip>:3000"
else
    echo "Frontend failed to start. Check npm logs."
    exit 1
fi

echo "Rebuild finished!"