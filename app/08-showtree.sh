#!/bin/bash
# DESC: Visual directory tree viewer with filtering, recent changes, and markdown export

TARGET_DIR=~/parco_fastapi
# Ask for depth
read -p "📐 Enter directory tree depth (default: 3): " USER_DEPTH
DEPTH=${USER_DEPTH:-3}

TREE_OUT="$TARGET_DIR/tree.md"

# Ensure tree is installed
if ! command -v tree &> /dev/null; then
  echo "🔧 Installing 'tree' utility..."
  sudo apt update && sudo apt install tree -y
fi

# Menu
clear
echo "🌲 ParcoRTLS Project Tree Utility"
echo "=================================="
echo "📁 Root directory: $TARGET_DIR"
echo "📐 Tree depth     : $DEPTH"
echo
echo "🛠️ Options:"
echo "  [1] View full tree"
echo "  [2] Filter by file type (*.py, *.js, etc.)"
echo "  [3] Show recently modified files"
echo "  [4] Export tree to Markdown"
echo "  [5] Cancel"
echo -ne "\nSelect an option [1-5]: "
read -r CHOICE

case "$CHOICE" in
  1)
    echo -e "\n📊 Full tree view:\n"
    tree -a -C -L $DEPTH "$TARGET_DIR" | less
    ;;

  2)
    echo -ne "🔍 Enter file extension (e.g., py, js, sh): "
    read -r EXT
    echo -e "\n📂 Showing only '*.$EXT' files (depth $DEPTH):\n"
    find "$TARGET_DIR" -maxdepth $DEPTH -type f -name "*.$EXT" | sort | less
    ;;

  3)
    echo -ne "📅 Show files modified in the last how many days? "
    read -r DAYS
    echo -e "\n🕒 Files modified in last $DAYS days:\n"
    find "$TARGET_DIR" -type f -mtime -"$DAYS" -exec ls -lt {} + | less
    ;;

  4)
    echo -e "\n📤 Exporting tree to $TREE_OUT...\n"
    tree -a -L $DEPTH "$TARGET_DIR" > "$TREE_OUT"
    echo "✅ Export complete. View it with:"
    echo "   less $TREE_OUT"
    ;;

  5)
    echo "🚪 Exiting."
    exit 0
    ;;

  *)
    echo "❌ Invalid choice."
    exit 1
    ;;
esac
