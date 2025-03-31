#!/bin/bash
# DESC: Rebuilds Node.js environment and dependencies for ParcoRTLS frontend
# VERSION: 1.0.0

# Stop the script if any command fails
set -e

echo "Starting ParcoRTLS frontend rebuild..."

# Step 1: Check for uncommitted Git changes
echo "Step 1: Checking for uncommitted Git changes..."
if ! git status --porcelain | grep -q .; then
    echo "No uncommitted changes found. Proceeding..."
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
    elif [ "$choice" = "2" ]; then
        # Save changes to a new branch and proceed
        CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        NEW_BRANCH="backup-$TIMESTAMP"
        echo "Saving changes to branch: $NEW_BRANCH"
        git checkout -b "$NEW_BRANCH"
        git add .
        git commit -m "Saved changes before rebuild on $TIMESTAMP"
        git checkout "$CURRENT_BRANCH"
        echo "Changes saved to $NEW_BRANCH. Proceeding with rebuild..."
    elif [ "$choice" = "4" ]; then
        # Save changes to a new branch and stop
        CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        NEW_BRANCH="backup-$TIMESTAMP"
        echo "Saving changes to branch: $NEW_BRANCH"
        git checkout -b "$NEW_BRANCH"
        git add .
        git commit -m "Saved changes before stopping on $TIMESTAMP"
        git checkout "$CURRENT_BRANCH"
        echo "Changes saved to $NEW_BRANCH. Stopping the script."
        exit 0
    else
        echo "Stopping the script."
        exit 1
    fi
fi

# Step 2: Stop any running npm processes
echo "Step 2: Stopping npm processes..."
sudo pkill -9 npm || echo "No npm processes to stop."
sleep 2
ps aux | grep npm || echo "No npm processes running."

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

# Step 5: Install dependencies
echo "Step 5: Installing dependencies..."
npm install --legacy-peer-deps

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