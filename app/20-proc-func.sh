# Name: 20-proc-func.sh
# Version: 0.1.1
# Created: 971201
# Modified: 250503
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Shell script to list stored procedures and functions in ParcoRTLSMaint database
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Dependent: TRUE

#!/bin/bash
# DESC: Lists stored procedures and functions in ParcoRTLSMaint database, generating proc_func_lbn.md and proc_func_details.md
# VERSION 0.1.1
# Changelog:
# - 0.1.1 (250503): Improved database connection error handling to exit early on failure
# - 0.1.0 (250503): Initial version

SCRIPT_DIR="/home/parcoadmin/parco_fastapi/app"
TITLE="🛠️  ParcoRTLS Procedures and Functions Utility"

# Reset terminal settings on exit
trap 'stty echo; tput reset; clear' EXIT

# Function to test database connection
test_db_connection() {
  psql -U menu19 -h localhost -d ParcoRTLSMaint -t -c "SELECT 1;" >/dev/null 2>&1 || {
    echo "❗ Failed to connect to database. Please check credentials in ~/.pgpass and try again."
    echo "📥 Press ENTER to return to the menu..."
    read
    return 1
  }
  return 0
}

# Function to display the menu
print_menu() {
  clear
  echo -e "$TITLE"
  echo "==========================="
  echo -e "📂 Directory: $SCRIPT_DIR"
  echo
  echo " [L] List Procs/Funcs (Save to proc_func_lbn.md)"
  echo " [D] Procs/Funcs Details (Save to proc_func_details.md)"
  echo " [E] Exit"
  echo
}

# Function to list procedures and functions in a Markdown file
save_procedures_functions_list() {
  local output_file="$SCRIPT_DIR/proc_func_lbn.md"
  echo -e "\n📝 Saving procedures and functions list to $output_file...\n"

  # Test database connection
  test_db_connection || return 1

  # Query for list of procedures and functions, including routine_type, and avoid duplicates
  psql -U menu19 -h localhost -d ParcoRTLSMaint --tuples-only -c "SELECT DISTINCT routine_schema, routine_name, routine_type FROM information_schema.routines WHERE routine_type IN ('PROCEDURE', 'FUNCTION') AND specific_schema = 'public' ORDER BY routine_schema, routine_name;" > "$output_file.temp" 2>/dev/null || {
    echo "❗ Failed to connect to database. Please check credentials in ~/.pgpass and try again."
    rm -f "$output_file.temp"
    echo "📥 Press ENTER to continue..."
    read
    return 1
  }

  # Convert to Markdown table format
  echo "# Stored Procedures and Functions in ParcoRTLSMaint" > "$output_file"
  echo "" >> "$output_file"
  echo "> **Note**: Routines with the \`usp_\` prefix are labeled as \`PROCEDURE\` in this output but are defined as \`FUNCTION\` in the database, based on naming convention." >> "$output_file"
  echo "" >> "$output_file"
  echo "| Schema           | Name             | Type             |" >> "$output_file"
  echo "|------------------|------------------|------------------|" >> "$output_file"
  while IFS='|' read -r schema name routine_type; do
    schema=$(echo "$schema" | xargs)
    name=$(echo "$name" | xargs)
    routine_type=$(echo "$routine_type" | xargs)
    if [ -n "$schema" ] && [ -n "$name" ] && [ -n "$routine_type" ]; then
      # Override type for usp_ routines
      if [[ "$name" =~ ^usp_ ]]; then
        routine_type="PROCEDURE"
      fi
      echo "| $schema              | $name              | $routine_type            |" >> "$output_file"
    fi
  done < "$output_file.temp"

  # Clean up temporary file
  rm "$output_file.temp"

  echo "✅ Saved to $output_file"
  echo -e "\n📥 Press ENTER to continue..."
  read
}

# Function to list procedures and functions with source code in a Markdown file
save_procedures_functions_details() {
  local output_file="$SCRIPT_DIR/proc_func_details.md"
  echo -e "\n📝 Saving procedures and functions with details to $output_file...\n"

  # Test database connection
  test_db_connection || return 1

  # Query for list of procedures and functions with their OIDs, including routine_type
  psql -U menu19 -h localhost -d ParcoRTLSMaint --tuples-only -c "SELECT DISTINCT r.routine_schema, r.routine_name, r.routine_type, p.oid FROM information_schema.routines r JOIN pg_proc p ON r.specific_name = p.proname || '_' || p.oid WHERE r.routine_type IN ('PROCEDURE', 'FUNCTION') AND r.specific_schema = 'public' ORDER BY r.routine_schema, r.routine_name;" > "$output_file.temp" 2>/dev/null || {
    echo "❗ Failed to connect to database. Please check credentials in ~/.pgpass and try again."
    rm -f "$output_file.temp"
    echo "📥 Press ENTER to continue..."
    read
    return 1
  }

  # Start the Markdown file
  echo "# Stored Procedures and Functions in ParcoRTLSMaint" > "$output_file"
  echo "" >> "$output_file"
  echo "> **Note**: Routines with the \`usp_\` prefix are labeled as \`PROCEDURE\` in this output but are defined as \`FUNCTION\` in the database, based on naming convention." >> "$output_file"
  echo "" >> "$output_file"

  # Process each procedure/function
  while IFS='|' read -r schema name routine_type oid; do
    # Clean up whitespace
    schema=$(echo "$schema" | xargs)
    name=$(echo "$name" | xargs)
    routine_type=$(echo "$routine_type" | xargs)
    oid=$(echo "$oid" | xargs)

    if [ -n "$schema" ] && [ -n "$name" ] && [ -n "$routine_type" ] && [ -n "$oid" ]; then
      # Override type for usp_ routines
      display_type="$routine_type"
      if [[ "$name" =~ ^usp_ ]]; then
        display_type="PROCEDURE"
      fi

      # Get the full definition
      definition=$(psql -U menu19 -h localhost -d ParcoRTLSMaint -t -c "SELECT pg_get_functiondef('$oid'::oid);" 2>/dev/null) || {
        echo "❗ Failed to retrieve definition for $schema.$name. Skipping..."
        continue
      }

      # Extract metadata if present in the definition (assuming comments at the top)
      metadata=$(echo "$definition" | grep -E "^-- (Name|Version|Created|Modified|Creator|Modified By|Description|Location|Role|Status|Dependent):" | sed 's/^-- //')
      if [ -z "$metadata" ]; then
        # Default metadata if not present
        metadata="Name: $name\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: $display_type in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE"
      fi

      # Write to Markdown file
      echo "$definition" >> "$output_file"
      echo "" >> "$output_file"
      echo "$metadata" >> "$output_file"
      echo "" >> "$output_file"
    fi
  done < "$output_file.temp"

  # Clean up temporary file
  rm "$output_file.temp"

  echo "✅ Saved to $output_file"
  echo -e "\n📥 Press ENTER to continue..."
  read
}

# Main loop
while true; do
  print_menu
  read -p "Select an option: " choice

  case "$choice" in
    [Ll])
      save_procedures_functions_list
      ;;
    [Dd])
      save_procedures_functions_details
      ;;
    [Ee])
      echo "👋 Goodbye!"
      break
      ;;
    *)
      echo "❗ Invalid selection. Enter L, D, or E."
      echo "Press ENTER to continue..."
      read
      ;;
  esac
done