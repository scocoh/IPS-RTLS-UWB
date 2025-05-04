# Name: 10-utilitymenu.sh
# Version: 0.1.57
# Created: 971201
# Modified: 250503
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Shell script for ParcoRTLS utilities
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Dependent: TRUE

#!/bin/bash
# DESC: Displays an interactive menu of available .sh scripts with options to run or edit them, plus a Components submenu
# VERSION 0P.3B.08
# Changelog:
# - 0P.3B.08 (250503): Added chmod +x for all *.sh scripts in print_menu to ensure they are executable
# - 0P.3B.07 (250503): Added option to run 20-proc-func.sh from Components submenu
# - 0P.3B.06 (250502): Added option to save component_versions table to list_components.md in Components submenu
# - 0P.3B.05 (250502): Added Components submenu with summary and full table view using less
# - 0P.3B.04 (250502): Added [C] Components option to display component_versions table

SCRIPT_DIR="/home/parcoadmin/parco_fastapi/app"
TITLE="🛠️  ParcoRTLS Utility Menu"
DESC_PREFIX="# DESC:"

# Reset terminal settings on exit
trap 'stty echo; tput reset; clear' EXIT

# Function to display the main menu
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

  # Ensure all scripts are executable
  chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null

  local i=1
  for script_path in "${scripts[@]}"; do
    script_name=$(basename "$script_path")
    desc_line=$(grep -m1 "$DESC_PREFIX" "$script_path" | sed "s/$DESC_PREFIX//" | sed 's/^ *//')
    printf " [%2d] %-20s - %s\n" "$i" "$script_name" "$desc_line"
    ((i++))
  done

  echo " [C] Components (View component_versions table)"
  echo " [M] Redisplay Menu"
  echo " [E] Exit"
  echo
}

# Function to display a summary of the component_versions table
show_components_summary() {
  echo -e "\n📊 Component Versions Summary\n"
  echo "Total Components by Role:"
  psql -U menu19 -h localhost -d ParcoRTLSMaint -c "SELECT role, COUNT(*) as count FROM component_versions GROUP BY role ORDER BY count DESC;" || {
    echo "❗ Failed to connect to database. Please check credentials and try again."
    echo "📥 Press ENTER to return to the Components menu..."
    read
    return 1
  }
  echo -e "\nTotal Components by Location:"
  psql -U menu19 -h localhost -d ParcoRTLSMaint -c "SELECT location, COUNT(*) as count FROM component_versions GROUP BY location ORDER BY count DESC;" || {
    echo "❗ Failed to connect to database. Please check credentials and try again."
    echo "📥 Press ENTER to return to the Components menu..."
    read
    return 1
  }
  echo -e "\n📥 Press ENTER to return to the Components menu..."
  read
}

# Function to display the full component_versions table
show_components_full() {
  echo -e "\n📋 Displaying component_versions table (use arrow keys to scroll, q to quit)...\n"
  psql -U menu19 -h localhost -d ParcoRTLSMaint -c "SELECT * FROM component_versions ORDER BY location, name;" | less -S || {
    echo "❗ Failed to connect to database. Please check credentials and try again."
    echo "📥 Press ENTER to return to the Components menu..."
    read
    return 1
  }
  echo -e "\n📥 Press ENTER to return to the Components menu..."
  read
}

# Function to save the component_versions table to a Markdown file
save_components_to_markdown() {
  local output_file="$SCRIPT_DIR/list_components.md"
  echo -e "\n📝 Saving component_versions table to $output_file...\n"

  # Run psql with --tuples-only to get clean table output
  psql -U menu19 -h localhost -d ParcoRTLSMaint --tuples-only -c "SELECT * FROM component_versions ORDER BY location, name;" > "$output_file.temp" || {
    echo "❗ Failed to connect to database. Please check credentials and try again."
    rm -f "$output_file.temp"
    echo "📥 Press ENTER to return to the Components menu..."
    read
    return 1
  }

  # Convert the psql output to Markdown table format
  echo "| name                          | version | created | modified | creator    | modified_by | description                          | location                                | role        | status | dependent |" > "$output_file"
  echo "|------------------------------|---------|---------|----------|------------|-------------|--------------------------------------|----------------------------------------|------------|--------|-----------|" >> "$output_file"
  cat "$output_file.temp" | sed 's/^[ \t]*//;s/[ \t]*$//;s/[ \t]*|[ \t]*/ | /g' >> "$output_file"

  # Clean up temporary file
  rm "$output_file.temp"

  echo "✅ Saved to $output_file"
  echo -e "\n📥 Press ENTER to return to the Components menu..."
  read
}

# Function to run the procedures and functions utility
run_procedures_functions_utility() {
  echo -e "\n▶️  Running 20-proc-func.sh...\n"
  ./20-proc-func.sh
  echo -e "\n📥 Press ENTER to return to the Components menu..."
  read
}

# Function to display the Components submenu
components_menu() {
  while true; do
    clear
    echo -e "📋 Components Menu"
    echo "==================="
    echo " [S] Summary (Counts by role and location)"
    echo " [F] Full Table (All components, on-screen)"
    echo " [M] Markdown (Save to list_components.md)"
    echo " [P] Procs/Funcs Utility (Run 20-proc-func.sh)"
    echo " [R] Return to Main Menu"
    echo
    read -p "Select an option: " choice

    case "$choice" in
      [Ss])
        show_components_summary
        ;;
      [Ff])
        show_components_full
        ;;
      [Mm])
        save_components_to_markdown
        ;;
      [Pp])
        run_procedures_functions_utility
        ;;
      [Rr])
        break
        ;;
      *)
        echo "❗ Invalid selection. Enter S, F, M, P, or R."
        echo "Press ENTER to continue..."
        read
        ;;
    esac
  done
}

# Main loop
while true; do
  print_menu
  read -p "Select a script by number to edit/run, [C]omponents, [M]enu, or [E]xit: " choice

  if [[ "$choice" =~ ^[Ee]$ ]]; then
    echo "👋 Goodbye!"
    break
  elif [[ "$choice" =~ ^[Mm]$ ]]; then
    continue
  elif [[ "$choice" =~ ^[Cc]$ ]]; then
    components_menu
  elif [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#scripts[@]} )); then
    script_name=$(basename "${scripts[choice-1]}")
    script_path="${scripts[choice-1]}"
    echo -e "\n📄 Selected: $script_name"
    echo "What would you like to do?"
    select action in "Run" "Edit" "Cancel"; do
      case $REPLY in
        1) 
          echo -e "▶️  Executing $script_path...\n"
          bash "$script_path"
          echo -e "\n📥 Press ENTER to return to the menu..."
          read
          break
          ;;
        2) echo -e "✏️  Opening $script_path in nano...\n"; nano "$script_path"; break ;;
        3) echo "❌ Cancelled."; break ;;
        *) echo "Invalid option." ;;
      esac
    done
  else
    echo "❗ Invalid selection. Enter a valid number, C for Components, M to redisplay, or E to exit."
  fi
done