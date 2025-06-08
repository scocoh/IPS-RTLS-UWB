#!/bin/bash
# Name: 10-utilitymenu.sh
# Version: 0.1.64
# Created: 971201
# Modified: 250607
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Shell script for ParcoRTLS utilities
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Dependent: TRUE
# DESC: Displays an interactive menu of available .sh scripts with options to run or edit them, plus a Components submenu
# VERSION 0P.3B.15
# Changelog:
# - 0P.3B.15 (250607): Fixed syntax error in script_path assignment; corrected select loop syntax; added debug logging to check_session_exists
# - 0P.3B.14 (250607): Added session existence check in log_manager_menu
# - 0P.3B.13 (250604): Fixed parameter passing to 24-logpane_tmux.sh
# - 0P.3B.12 (250604): Fixed Log Manager to display correct session name and all 7 panes
# - 0P.3B.11 (250604): Added support for logging both parco-dev and tetse-dev sessions in Log Manager
# - 0P.3B.10 (250523): Enhanced [L] Log Pane with submenu for advanced logging features
# - 0P.3B.09 (250523): Added [L] Log Pane Output option to start/stop logging for tmux panes
# - 0P.3B.08 (250503): Added chmod +x for all *.sh scripts in print_menu to ensure they are executable
# - 0P.3B.07 (250503): Added option to run 20-proc-func.sh from Components submenu
# - 0P.3B.06 (250502): Added option to save component_versions table to list_components.md in Components submenu
# - 0P.3B.05 (250502): Added Components submenu with summary and full table view using less
# - 0P.3B.04 (250502): Added [C] Components option to display component_versions table

SCRIPT_DIR="/home/parcoadmin/parco_fastapi/app"
TITLE="🛠️  ParcoRTLS Utility Menu"
DESC_PREFIX="# DESC:"
LOGDIR="/home/parcoadmin/logs"

# Ensure log directory exists
mkdir -p "$LOGDIR"

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
  echo " [L] Log Manager (Advanced tmux pane logging)"
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

# Function to check if a tmux session exists
check_session_exists() {
  local session=$1
  echo "DEBUG: Checking session $session at $(date)" >> "$LOGDIR/debug.log"
  if ! tmux has-session -t "$session" 2>/dev/null; then
    echo "DEBUG: Session $session does not exist" >> "$LOGDIR/debug.log"
    return 1
  fi
  echo "DEBUG: Session $session exists" >> "$LOGDIR/debug.log"
  return 0
}

# Function to display the Log Manager submenu
log_manager_menu() {
  while true; do
    clear
    echo -e "📝 Log Manager"
    echo "==============="
    
    echo "Available tmux sessions:"
    echo " [1] parco-dev (06-devsession)"
    echo " [2] tetse-dev (25-devsession)"
    echo " [3] Both"
    echo " [R] Return to Main Menu"
    echo
    read -p "Select a tmux session to manage logs: " session_choice

    case "$session_choice" in
      1) SESSION_NAME="parco-dev" ;;
      2) SESSION_NAME="tetse-dev" ;;
      3) SESSION_NAME="both" ;;
      [Rr]) return ;;
      *) echo "❗ Invalid session choice. Press ENTER to retry..."; read; continue ;;
    esac

    # Check session existence
    if [[ "$SESSION_NAME" != "both" ]]; then
      if ! check_session_exists "$SESSION_NAME"; then
        echo "❗ Session $SESSION_NAME does not exist. Start it using the appropriate devsession script."
        echo "Press ENTER to retry..."
        read
        continue
      fi
    else
      if ! check_session_exists "parco-dev" || ! check_session_exists "tetse-dev"; then
        echo "❗ One or both sessions (parco-dev, tetse-dev) do not exist. Start the missing session(s)."
        echo "Press ENTER to retry..."
        read
        continue
      fi
    fi

    while true; do
      clear
      echo -e "📝 Log Manager - $SESSION_NAME"
      echo "=============================="

      if [[ "$SESSION_NAME" == "both" ]]; then
        echo "Status for parco-dev:"
        "$SCRIPT_DIR/24-logpane_tmux.sh" status "" parco-dev 2>/dev/null | head -20
        echo
        echo "Status for tetse-dev:"
        "$SCRIPT_DIR/24-logpane_tmux.sh" status "" tetse-dev 2>/dev/null | head -20
      else
        "$SCRIPT_DIR/24-logpane_tmux.sh" status "" "$SESSION_NAME" 2>/dev/null | head -20
      fi
      echo

      echo "Log Management Options for $SESSION_NAME:"
      echo " [1] Start Logging (Single Pane)"
      echo " [2] Stop Logging (Single Pane)"
      echo " [3] Start All Panes"
      echo " [4] Stop All Panes"
      echo " [5] List Active Logs"
      echo " [6] Tail Log File"
      echo " [7] Cleanup Old Logs"
      echo " [8] Show Full Status"
      echo " [R] Return to Session Selector"
      echo
      read -p "Select an option: " choice

      case "$choice" in
        1)
          echo -e "\n🚀 Start Logging for Single Pane"
          echo "================================="
          read -p "Enter pane number (0-6): " pane_num
          if [[ "$pane_num" =~ ^[0-6]$ ]]; then
            if [[ "$SESSION_NAME" == "both" ]]; then
              "$SCRIPT_DIR/24-logpane_tmux.sh" start "$pane_num" parco-dev
              "$SCRIPT_DIR/24-logpane_tmux.sh" start "$pane_num" tetse-dev
            else
              "$SCRIPT_DIR/24-logpane_tmux.sh" start "$pane_num" "$SESSION_NAME"
            fi
          else
            echo "❗ Invalid pane number. Must be 0-6."
          fi
          echo -e "\n📥 Press ENTER to continue..."
          read
          ;;
        2)
          echo -e "\n🛑 Stop Logging for Single Pane"
          echo "================================"
          read -p "Enter pane number (0-6): " pane_num
          if [[ "$pane_num" =~ ^[0-6]$ ]]; then
            if [[ "$SESSION_NAME" == "both" ]]; then
              "$SCRIPT_DIR/24-logpane_tmux.sh" stop "$pane_num" parco-dev
              "$SCRIPT_DIR/24-logpane_tmux.sh" stop "$pane_num" tetse-dev
            else
              "$SCRIPT_DIR/24-logpane_tmux.sh" stop "$pane_num" "$SESSION_NAME"
            fi
          else
            echo "❗ Invalid pane number. Must be 0-6."
          fi
          echo -e "\n📥 Press ENTER to continue..."
          read
          ;;
        3)
          echo -e "\n🚀 Starting Logging for All Active Panes"
          echo "========================================"
          if [[ "$SESSION_NAME" == "both" ]]; then
            "$SCRIPT_DIR/24-logpane_tmux.sh" start-all "" parco-dev
            "$SCRIPT_DIR/24-logpane_tmux.sh" start-all "" tetse-dev
          else
            "$SCRIPT_DIR/24-logpane_tmux.sh" start-all "" "$SESSION_NAME"
          fi
          echo -e "\n📥 Press ENTER to continue..."
          read
          ;;
        4)
          echo -e "\n🛑 Stopping Logging for All Panes"
          echo "=================================="
          read -p "⚠️  Stop logging for ALL panes? (y/N): " confirm
          if [[ "$confirm" =~ ^[Yy]$ ]]; then
            if [[ "$SESSION_NAME" == "both" ]]; then
              "$SCRIPT_DIR/24-logpane_tmux.sh" stop-all "" parco-dev
              "$SCRIPT_DIR/24-logpane_tmux.sh" stop-all "" tetse-dev
            else
              "$SCRIPT_DIR/24-logpane_tmux.sh" stop-all "" "$SESSION_NAME"
            fi
          else
            echo "❌ Cancelled"
          fi
          echo -e "\n📥 Press ENTER to continue..."
          read
          ;;
        5)
          echo -e "\n📋 Active Logging Sessions"
          echo "=========================="
          if [[ "$SESSION_NAME" == "both" ]]; then
            echo "Active logs for parco-dev:"
            "$SCRIPT_DIR/24-logpane_tmux.sh" list "" parco-dev
            echo
            echo "Active logs for tetse-dev:"
            "$SCRIPT_DIR/24-logpane_tmux.sh" list "" tetse-dev
          else
            "$SCRIPT_DIR/24-logpane_tmux.sh" list "" "$SESSION_NAME"
          fi
          echo -e "\n📥 Press ENTER to continue..."
          read
          ;;
        6)
          echo -e "\n📖 Tail Log File"
          echo "================"
          if [[ "$SESSION_NAME" == "both" ]]; then
            echo "Tailing logs for parco-dev:"
            "$SCRIPT_DIR/24-logpane_tmux.sh" tail "" parco-dev
            echo
            echo "Tailing logs for tetse-dev:"
            "$SCRIPT_DIR/24-logpane_tmux.sh" tail "" tetse-dev
          else
            "$SCRIPT_DIR/24-logpane_tmux.sh" tail "" "$SESSION_NAME"
          fi
          # Note: tail command handles its own user interaction
          ;;
        7)
          echo -e "\n🧹 Cleanup Old Logs"
          echo "==================="
          if [[ "$SESSION_NAME" == "both" ]]; then
            "$SCRIPT_DIR/24-logpane_tmux.sh" cleanup "" parco-dev
            "$SCRIPT_DIR/24-logpane_tmux.sh" cleanup "" tetse-dev
          else
            "$SCRIPT_DIR/24-logpane_tmux.sh" cleanup "" "$SESSION_NAME"
          fi
          echo -e "\n📥 Press ENTER to continue..."
          read
          ;;
        8)
          echo -e "\n🔍 Full Logging Status"
          echo "======================"
          if [[ "$SESSION_NAME" == "both" ]]; then
            echo "Full status for parco-dev:"
            "$SCRIPT_DIR/24-logpane_tmux.sh" status "" parco-dev
            echo
            echo "Full status for tetse-dev:"
            "$SCRIPT_DIR/24-logpane_tmux.sh" status "" tetse-dev
          else
            "$SCRIPT_DIR/24-logpane_tmux.sh" status "" "$SESSION_NAME"
          fi
          echo -e "\n📥 Press ENTER to continue..."
          read
          ;;
        [Rr])
          break
          ;;
        *)
          echo "❗ Invalid selection. Enter 1-8 or R."
          echo "Press ENTER to continue..."
          read
          ;;
      esac
    done
  done
}

# Main loop
while true; do
  print_menu
  read -p "Select a script by number to edit/run, [C]omponents, [L]og Manager, [M]enu, or [E]xit: " choice

  if [[ "$choice" =~ ^[Ee]$ ]]; then
    echo "👋 Goodbye!"
    break
  elif [[ "$choice" =~ ^[Mm]$ ]]; then
    continue
  elif [[ "$choice" =~ ^[Cc]$ ]]; then
    components_menu
  elif [[ "$choice" =~ ^[Ll]$ ]]; then
    log_manager_menu
  elif [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#scripts[@]} )); then
    script_name=$(basename "${scripts[choice-1]}")
    # Original (0.1.64): script_path="${scripts[choice-1]}")
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
    echo "❗ Invalid selection. Enter a valid number, C for Components, L for Log Manager, M to redisplay, or E to exit."
  fi
done