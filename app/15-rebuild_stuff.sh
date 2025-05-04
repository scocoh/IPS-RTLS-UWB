# Name: 15-rebuild_stuff.sh
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Shell script for ParcoRTLS utilities
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Dependent: TRUE

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

# SUMMARY OF WORK THREAD (parcoadmin and Grok, March 31, 2025):
#
# Introduction:
# On March 31, 2025, parcoadmin (with assistance from Grok) initiated a task to secure the local Git setup on the development server parcortlsserver in the directory /home/parcoadmin/parco_fastapi/app. The goal was to prevent a repeat of an issue where a faulty operation deleted the node_modules directory, leading to an 11-hour recovery. The project directory is used for local Git development and alpha/beta testing before pushing to GitHub (https://github.com/scocoh/IPS-RTLS-UWB.git, linux branch). The initial prompt requested a step-by-step plan to review and secure the Git configuration, .gitignore, and workflow, ensuring critical files like node_modules are protected, with a preference for a slow, methodical approach.
#
# Accomplishments and Fixes:
# 1. Identified the Cause of node_modules Deletion: Analyzed cron jobs and scripts (09-update.sh, 14-gitdiff.sh, 15-rebuild_stuff.sh) and found that 15-rebuild_stuff.sh was deleting node_modules with rm -rf. Added a confirmation prompt to prevent accidental deletion.
# 2. Secured Git Workflow: Added Git status checks to 15-rebuild_stuff.sh to detect uncommitted changes, with options to save them to a backup branch (e.g., backup-20250331_171016) and either proceed or stop.
# 3. Added Stop-at-Any-Step Functionality: Modified 15-rebuild_stuff.sh to allow stopping after any step (e.g., after stopping npm processes, installing Node.js), giving more control during the rebuild process.
# 4. Merged Branches into master: Successfully merged backup-20250331_171016 and feature-new-development into master, resolving a merge conflict in 15-rebuild_stuff.sh by keeping the updated version from master.
# 5. Created Local linux Branch: Set up a local linux branch to match the intended workflow, without pushing to GitHub as requested.
# 6. Added Documentation: Included tips, keywords, and a detailed note in 15-rebuild_stuff.sh for future reference.
#
# Milestones:
# - Initial Diagnosis: Confirmed cron jobs weren’t deleting node_modules; identified 15-rebuild_stuff.sh as the culprit.
# - First Fix: Added a confirmation prompt to 15-rebuild_stuff.sh to protect node_modules.
# - Git Integration: Added Git status checks and backup branch functionality to 15-rebuild_stuff.sh.
# - Enhanced Control: Implemented stop-at-any-step feature in 15-rebuild_stuff.sh.
# - Branch Consolidation: Merged backup-20250331_171016 and feature-new-development into master.
# - Final Documentation: Added a comprehensive note to 15-rebuild_stuff.sh summarizing the thread.
#
# Failures and Roadblocks Encountered:
# - Script Disappearance: 15-rebuild_stuff.sh disappeared from the working directory because it was untracked and got committed to a backup branch (backup-20250331_171016). Resolved by recovering the file and committing it to master, then modifying the script to exclude itself from backups.
# - Missing linux Branch: Attempted to checkout and push to a linux branch, but it didn’t exist locally or on GitHub. Created a local linux branch but didn’t push as requested.
# - Merge Conflict: Encountered a conflict in 15-rebuild_stuff.sh when merging backup-20250331_171016 into master. Resolved by keeping the master version.
# - Path Error: Incorrectly used app/15-rebuild_stuff.sh instead of 15-rebuild_stuff.sh during conflict resolution, due to a misunderstanding of the repository structure. Corrected the path and proceeded.
#
# Steps We Should Have Started With (But Did Last):
# - Commit 15-rebuild_stuff.sh Early: Should have committed 15-rebuild_stuff.sh to master at the start to avoid it being untracked and moved to a backup branch.
# - Check for linux Branch: Should have run git branch -r early to confirm the existence of the linux branch on GitHub before attempting to merge and push.
# - Verify Repository Structure: Should have confirmed the correct path for 15-rebuild_stuff.sh (not app/15-rebuild_stuff.sh) earlier to avoid path errors during conflict resolution.
#
# Final Conclusion:
# The Git setup is now secure: node_modules is protected by a confirmation prompt in 15-rebuild_stuff.sh, uncommitted changes can be saved to a backup branch, and the rebuild process can be stopped at any step. The master branch contains all changes from backup-20250331_171016 and feature-new-development. A local linux branch was created but not pushed to GitHub, keeping changes private as requested. The script includes tips, keywords, and a detailed note for future reference, ensuring parcoadmin can use it safely and troubleshoot effectively.
#
# Instructions for the Future (Prompt):
# If you encounter issues with this setup in the future, use this prompt to ask for help:
# "I’m working on parcortlsserver in /home/parcoadmin/parco_fastapi/app. I need help with 15-rebuild_stuff.sh, which rebuilds my Node.js frontend. The script should protect node_modules, save uncommitted Git changes, and allow stopping at any step. I’m seeing [describe issue, e.g., 'an error when stopping at Step 2', 'a merge conflict', 'node_modules deleted']. Here’s the output: [paste output]. Keywords: 15-rebuild_stuff.sh, node_modules deletion, Git uncommitted changes, stop at step. Please help me troubleshoot and fix this."
#
# List of File Names Uploaded or Pasted:
# - Screenshots: 15-rebuild_stuff.sh (initial version with rm -rf node_modules), Merge conflict commit message in nano (showing additional changes from backup-20250331_171016).
# - Text Outputs: crontab -l output, /etc/crontab and /etc/cron.* output, /var/log/syslog and /var/log/cron grep results, ls -la output for .sh and .py files, history | grep -i crontab output, cat 09-update.sh | grep -E 'git|node_modules' output, cat 14-gitdiff.sh | grep -E 'git|node_modules' output, cat 15-rebuild_stuff.sh | grep -E 'git|node_modules' output, .gitignore | grep node_modules output, Various git status, git branch, and script execution outputs.
#
# List of Files Created or Modified:
# - Modified: 15-rebuild_stuff.sh (updated with node_modules prompt, Git checks, stop-at-any-step, documentation), .gitignore (verified to include node_modules/), README.md (added script usage and updates).
# - Created (as part of merges): 16-htop.sh, 17-top.sh, 18-ps.sh, gitdiff.sh, package.backup.json (merged from backup-20250331_171016 into master).
# - Modified (as part of merges): 10-utilitymenu.sh, 14-gitdiff.sh, package-lock.json, package.json (merged from backup-20250331_171016 into master).

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