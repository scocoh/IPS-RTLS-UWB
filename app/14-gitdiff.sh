# Name: 14-gitdiff.sh
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
# DESC: Shows Git diff for .sql files, creates PostgreSQL backup, and optionally applies updated functions
# VERSION 0P.1B.01

PROJECT_DIR="/home/parcoadmin/parco_fastapi/app"
LOG_DIR="$HOME/parco_fastapi/logs"
LOG_FILE="$LOG_DIR/gitdiff_$(date +%Y%m%d_%H%M%S).log"
GIT_REPO="$PROJECT_DIR"
BRANCH_MAIN="main"
BRANCH_STAGE="staging"
PG_DB="maint"  # Adjust if needed
PG_USER="parcoadmin"
PG_BACKUP="$LOG_DIR/postgres_backup_$(date +%Y%m%d_%H%M%S).sql"

mkdir -p "$LOG_DIR"
cd "$GIT_REPO" || exit 1

echo "📦 Git diff utility for SQL function updates" | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"

# 1. Fetch latest changes and update the staging branch
echo "🔄 Fetching origin/$BRANCH_MAIN to $BRANCH_STAGE..." | tee -a "$LOG_FILE"
git fetch origin "$BRANCH_MAIN" >> "$LOG_FILE" 2>&1

# Create or reset staging branch
if git show-ref --quiet refs/heads/"$BRANCH_STAGE"; then
    git branch -f "$BRANCH_STAGE" origin/"$BRANCH_MAIN"
else
    git checkout -b "$BRANCH_STAGE" origin/"$BRANCH_MAIN"
    git checkout "$BRANCH_MAIN"
fi

# 2. Identify SQL files that have changed
echo "🔍 Checking for changed SQL files..." | tee -a "$LOG_FILE"
CHANGED_SQL=$(git diff "$BRANCH_MAIN" "$BRANCH_STAGE" --name-only | grep '\.sql$')

if [[ -z "$CHANGED_SQL" ]]; then
    echo "✅ No .sql files changed between $BRANCH_MAIN and $BRANCH_STAGE." | tee -a "$LOG_FILE"
    exit 0
fi

echo "📝 Changed SQL files:" | tee -a "$LOG_FILE"
echo "$CHANGED_SQL" | tee -a "$LOG_FILE"
echo

# 3. Show diff for user review
for file in $CHANGED_SQL; do
    echo "🔄 Diff for $file:" | tee -a "$LOG_FILE"
    git diff "$BRANCH_MAIN" "$BRANCH_STAGE" -- "$file" | tee -a "$LOG_FILE"
    echo -e "\n--------------------------\n" | tee -a "$LOG_FILE"
done

# 4. Ask whether to apply
echo
read -rp "❓ Apply updated .sql function definitions to PostgreSQL? (y/n): " confirm_apply

if [[ "$confirm_apply" =~ ^[Yy]$ ]]; then
    echo "🛡️  Backing up current PostgreSQL database to $PG_BACKUP..." | tee -a "$LOG_FILE"
    pg_dump -U "$PG_USER" -d "$PG_DB" > "$PG_BACKUP" 2>>"$LOG_FILE"

    echo "🚀 Applying SQL updates..." | tee -a "$LOG_FILE"
    for file in $CHANGED_SQL; do
        psql -U "$PG_USER" -d "$PG_DB" -f "$file" >>"$LOG_FILE" 2>&1
        echo "✅ Applied $file" | tee -a "$LOG_FILE"
    done
    echo "✅ All SQL updates applied successfully." | tee -a "$LOG_FILE"
else
    echo "🚫 No changes applied." | tee -a "$LOG_FILE"
fi

echo "📄 Log saved to $LOG_FILE"
