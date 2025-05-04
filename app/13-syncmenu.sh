# Name: 13-syncmenu.sh
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
# DESC: Reorders .sh scripts by core order + new scripts, updates all aliases including 'menu'
# VERSION 0P.2B.02

SCRIPT_DIR="/home/parcoadmin/parco_fastapi/app"
CORE_ORDER=(
    "devstop.sh"
    "shutdownmenu.sh"
    "checkports.sh"
    "cleanstart.sh"
    "devcheck.sh"
    "devsession.sh"
    "setup.sh"
    "showtree.sh"
    "update.sh"
    "utilitymenu.sh"
    "shutdown.sh"
    "start_frontend.sh"
    "syncmenu.sh"
)

echo "🔍 Scanning and syncing ParcoRTLS utility scripts..."

# Step 1: Strip existing numeric prefixes
cd "$SCRIPT_DIR" || exit 1
for f in [0-9][0-9]-*.sh; do
    newname=$(echo "$f" | sed -E 's/^[0-9]{2}-//')
    [ "$f" != "$newname" ] && mv "$f" "$newname" && echo "renamed '$f' -> '$newname'"
done

# Step 2: Rename based on core order
index=1
for name in "${CORE_ORDER[@]}"; do
    if [ -f "$name" ]; then
        num=$(printf "%02d" $index)
        mv "$name" "$num-$name"
        echo "renamed '$name' -> '$num-$name'"
        ((index++))
    fi
done

# Step 3: Update aliases in ~/.bashrc
echo "🔧 Updated 'menu' alias in .bashrc"
sed -i "s#^alias menu=.*#alias menu='/home/parcoadmin/parco_fastapi/app/10-utilitymenu.sh'#" ~/.bashrc

echo "🔁 Updating dynamic aliases for core scripts..."
for f in [0-9][0-9]-*.sh; do
    base=$(echo "$f" | sed -E 's/^[0-9]{2}-//' | sed 's/.sh$//')
    alias_line="alias $base='$SCRIPT_DIR/$f'"
    sed -i "s#^alias $base=.*#${alias_line}#" ~/.bashrc 2>/dev/null || echo "$alias_line" >> ~/.bashrc
done

echo "✅ All aliases synced and menu updated."
