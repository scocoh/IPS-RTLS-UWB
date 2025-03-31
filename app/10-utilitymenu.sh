#!/bin/bash
# DESC: Displays an interactive menu of available .sh scripts with options to run or edit them
# VERSION 0P.3B.03

SCRIPT_DIR="/home/parcoadmin/parco_fastapi/app"
TITLE="🛠️  ParcoRTLS Utility Menu"
DESC_PREFIX="# DESC:"

# Function to display the full menu
print_menu() {
  clear
  echo -e "$TITLE"
  echo "==========================="
  echo -e "📂 Directory: $SCRIPT_DIR"
  echo

  # Always refresh the list of scripts before displaying
  scripts=($(find "$SCRIPT_DIR" -maxdepth 1 -type f -name "[0-9][0-9]-*.sh" | sort))

  if [ ${#scripts[@]} -eq 0 ]; then
    echo "⚠️  No ordered .sh scripts found in $SCRIPT_DIR"
    exit 1
  fi

  local i=1
  for script_path in "${scripts[@]}"; do
    script_name=$(basename "$script_path")
    desc_line=$(grep -m1 "$DESC_PREFIX" "$script_path" | sed "s/$DESC_PREFIX//" | sed 's/^ *//')
    printf " [%2d] %-20s - %s\n" "$i" "$script_name" "$desc_line"
    ((i++))
  done

  echo " [M] Redisplay Menu"
  echo " [E] Exit"
  echo
}

# Main loop
while true; do
  print_menu
  read -p "Select a script by number to edit/run, [M]enu, or [E]xit: " choice

  if [[ "$choice" =~ ^[Ee]$ ]]; then
    echo "👋 Goodbye!"
    break
  elif [[ "$choice" =~ ^[Mm]$ ]]; then
    continue
  elif [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#scripts[@]} )); then
    script_name=$(basename "${scripts[choice-1]}")
    script_path="${scripts[choice-1]}"
    echo -e "\n📄 Selected: $script_name"
    echo "What would you like to do?"
    select action in "Run" "Edit" "Cancel"; do
      case $REPLY in
        1) echo -e "▶️  Executing $script_path...\n"; bash "$script_path"; break ;;
        2) echo -e "✏️  Opening $script_path in nano...\n"; nano "$script_path"; break ;;
        3) echo "❌ Cancelled."; break ;;
        *) echo "Invalid option." ;;
      esac
    done
  else
    echo "❗ Invalid selection. Enter a valid number, M to redisplay, or E to exit."
  fi
done
