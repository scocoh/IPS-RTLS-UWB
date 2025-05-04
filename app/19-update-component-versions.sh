#!/bin/bash
# Name: 19-update-component-versions.sh
# Version: 0.1.80
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Scans ParcoRTLS components and populates component_versions table
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Dependent: FALSE
# Changelog:
# - 0.1.80 (250502): Shortened description for better readability in psql output
# - 0.1.79 (250502): Automated updates to existing entries without prompting
# - 0.1.78 (250502): Fixed metadata extraction to properly apply defaults, fixed boolean handling in INSERT, improved debug output
# - 0.1.77 (250502): Fixed permission issue warning, ensured all fields have defaults, fixed output format
# - 0.1.76 (250502): Fixed multi-line metadata extraction with grep -m 1, added debugging, deleted __init__.py entries, automated adding missing files

# Base directory
BASE_DIR="/home/parcoadmin/parco_fastapi/app"

# Directories to exclude
EXCLUDE_DIRS=("backups" "and" "__pycache__" "uploaded_maps" "uploads" "templates_backup_2025-02-11_16-30-34" "archives" "node_modules" ".pytest_cache" "logs" "build")

# Global variable to store prompt choice
PROMPT_CHOICE=""

# Function to check if a directory should be excluded
should_exclude_dir() {
    local dir="$1"
    local dir_name=$(basename "$dir")
    for exclude in "${EXCLUDE_DIRS[@]}"; do
        if [ "$dir_name" = "$exclude" ]; then
            return 0 # Exclude
        fi
    done
    return 1 # Do not exclude
}

# Function to check if a file should be excluded
should_exclude_file() {
    local file="$1"
    local file_name=$(basename "$file")
    # Exclude __init__.py files
    if [ "$file_name" = "__init__.py" ]; then
        return 0 # Exclude
    fi
    # Exclude .json files
    if [[ "$file_name" == *.json ]]; then
        return 0 # Exclude
    fi
    return 1 # Do not exclude
}

# Function to add a comment block to a file
add_comment_block() {
    local file="$1"
    local name="$2"
    local ext="${file##*.}"
    local temp_file=$(mktemp)
    local added=false

    # Define comment block based on file type
    case "$ext" in
        sh|py|txt)
            cat <<EOL > "$temp_file"
# Name: $name
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: $(get_default_description "$file")
# Location: $(dirname "$file")
# Role: $(get_default_role "$file")
# Status: Active
# Dependent: TRUE

EOL
            cat "$file" >> "$temp_file"
            mv "$temp_file" "$file"
            added=true
            ;;
        html)
            cat <<EOL > "$temp_file"
<!-- Name: $name -->
<!-- Version: 0.1.0 -->
<!-- Created: 971201 -->
<!-- Modified: 250502 -->
<!-- Creator: ParcoAdmin -->
<!-- Modified By: ParcoAdmin -->
<!-- Description: $(get_default_description "$file") -->
<!-- Location: $(dirname "$file") -->
<!-- Role: $(get_default_role "$file") -->
<!-- Status: Active -->
<!-- Dependent: TRUE -->

EOL
            cat "$file" >> "$temp_file"
            mv "$temp_file" "$file"
            added=true
            ;;
        css|js|jsx)
            cat <<EOL > "$temp_file"
/* Name: $name */
/* Version: 0.1.0 */
/* Created: 971201 */
/* Modified: 250502 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: $(get_default_description "$file") */
/* Location: $(dirname "$file") */
/* Role: $(get_default_role "$file") */
/* Status: Active */
/* Dependent: TRUE */

EOL
            cat "$file" >> "$temp_file"
            mv "$temp_file" "$file"
            added=true
            ;;
        json)
            # Skip for .json; metadata stored in component_versions
            return 1
            ;;
        *)
            return 1
            ;;
    esac

    if [ "$added" = true ]; then
        return 0
    else
        return 1
    fi
}

# Function to get default role based on extension
get_default_role() {
    local file="$1"
    case "${file##*.}" in
        sh) echo "Utility" ;;
        py) echo "Backend" ;;
        json) echo "Configuration" ;;
        html) echo "Frontend" ;;
        css) echo "Frontend" ;;
        txt) echo "Utility" ;;
        js|jsx) echo "Frontend" ;;
        *) echo "Unknown" ;;
    esac
}

# Function to get default description based on extension
get_default_description() {
    local file="$1"
    case "${file##*.}" in
        sh) echo "ParcoRTLS utility script" ;;
        py) echo "ParcoRTLS backend script" ;;
        json) echo "ParcoRTLS config file" ;;
        html) echo "ParcoRTLS frontend template" ;;
        css) echo "ParcoRTLS frontend stylesheet" ;;
        txt) echo "ParcoRTLS config text file" ;;
        js|jsx) echo "ParcoRTLS frontend script" ;;
        *) echo "ParcoRTLS unknown file type" ;;
    esac
}

# Function to extract metadata from a file's comment block
extract_metadata_from_file() {
    local file="$1"
    local name version created modified creator modified_by description location role status dependent

    # Initialize with defaults
    name=$(basename "$file")
    location=$(dirname "$file")
    version="0.1.0"
    created="971201"
    modified="250502"
    creator="ParcoAdmin"
    modified_by="ParcoAdmin"
    description=$(get_default_description "$file")
    role=$(get_default_role "$file")
    status="Active"
    dependent="TRUE"

    # Extract metadata if comment block exists
    if grep -q "^# Name:\|^<!-- Name:\|^/\* Name:" "$file" 2>/dev/null; then
        case "${file##*.}" in
            sh|py|txt)
                name=$(grep -m 1 "^# Name:" "$file" | sed 's/# Name: //')
                version=$(grep -m 1 "^# Version:" "$file" | sed 's/# Version: //')
                created=$(grep -m 1 "^# Created:" "$file" | sed 's/# Created: //')
                modified=$(grep -m 1 "^# Modified:" "$file" | sed 's/# Modified: //')
                creator=$(grep -m 1 "^# Creator:" "$file" | sed 's/# Creator: //')
                modified_by=$(grep -m 1 "^# Modified By:" "$file" | sed 's/# Modified By: //')
                description=$(grep -m 1 "^# Description:" "$file" | sed 's/# Description: //')
                location=$(grep -m 1 "^# Location:" "$file" | sed 's/# Location: //')
                role=$(grep -m 1 "^# Role:" "$file" | sed 's/# Role: //')
                status=$(grep -m 1 "^# Status:" "$file" | sed 's/# Status: //')
                dependent=$(grep -m 1 "^# Dependent:" "$file" | sed 's/# Dependent: //')
                ;;
            html)
                name=$(grep -m 1 "^<!-- Name:" "$file" | sed 's/<!-- Name: //; s/ -->//')
                version=$(grep -m 1 "^<!-- Version:" "$file" | sed 's/<!-- Version: //; s/ -->//')
                created=$(grep -m 1 "^<!-- Created:" "$file" | sed 's/<!-- Created: //; s/ -->//')
                modified=$(grep -m 1 "^<!-- Modified:" "$file" | sed 's/<!-- Modified: //; s/ -->//')
                creator=$(grep -m 1 "^<!-- Creator:" "$file" | sed 's/<!-- Creator: //; s/ -->//')
                modified_by=$(grep -m 1 "^<!-- Modified By:" "$file" | sed 's/<!-- Modified By: //; s/ -->//')
                description=$(grep -m 1 "^<!-- Description:" "$file" | sed 's/<!-- Description: //; s/ -->//')
                location=$(grep -m 1 "^<!-- Location:" "$file" | sed 's/<!-- Location: //; s/ -->//')
                role=$(grep -m 1 "^<!-- Role:" "$file" | sed 's/<!-- Role: //; s/ -->//')
                status=$(grep -m 1 "^<!-- Status:" "$file" | sed 's/<!-- Status: //; s/ -->//')
                dependent=$(grep -m 1 "^<!-- Dependent:" "$file" | sed 's/<!-- Dependent: //; s/ -->//')
                ;;
            css|js|jsx)
                name=$(grep -m 1 "^/\* Name:" "$file" | sed 's/\/\* Name: //; s/ \*\///')
                version=$(grep -m 1 "^/\* Version:" "$file" | sed 's/\/\* Version: //; s/ \*\///')
                created=$(grep -m 1 "^/\* Created:" "$file" | sed 's/\/\* Created: //; s/ \*\///')
                modified=$(grep -m 1 "^/\* Modified:" "$file" | sed 's/\/\* Modified: //; s/ \*\///')
                creator=$(grep -m 1 "^/\* Creator:" "$file" | sed 's/\/\* Creator: //; s/ \*\///')
                modified_by=$(grep -m 1 "^/\* Modified By:" "$file" | sed 's/\/\* Modified By: //; s/ \*\///')
                description=$(grep -m 1 "^/\* Description:" "$file" | sed 's/\/\* Description: //; s/ \*\///')
                location=$(grep -m 1 "^/\* Location:" "$file" | sed 's/\/\* Location: //; s/ \*\///')
                role=$(grep -m 1 "^/\* Role:" "$file" | sed 's/\/\* Role: //; s/ \*\///')
                status=$(grep -m 1 "^/\* Status:" "$file" | sed 's/\/\* Status: //; s/ \*\///')
                dependent=$(grep -m 1 "^/\* Dependent:" "$file" | sed 's/\/\* Dependent: //; s/ \*\///')
                ;;
        esac
    fi

    # Apply defaults for any unset fields
    name=${name:-$(basename "$file")}
    version=${version:-0.1.0}
    created=${created:-971201}
    modified=${modified:-250502}
    creator=${creator:-ParcoAdmin}
    modified_by=${modified_by:-ParcoAdmin}
    description=${description:-$(get_default_description "$file")}
    location=${location:-$(dirname "$file")}
    role=${role:-$(get_default_role "$file")}
    status=${status:-Active}
    dependent=${dependent:-TRUE}

    # Debug output to stderr to separate from return value
    >&2 echo "Debug: Extracted metadata for $file:"
    >&2 echo "  name=$name"
    >&2 echo "  version=$version"
    >&2 echo "  created=$created"
    >&2 echo "  modified=$modified"
    >&2 echo "  creator=$creator"
    >&2 echo "  modified_by=$modified_by"
    >&2 echo "  description=$description"
    >&2 echo "  location=$location"
    >&2 echo "  role=$role"
    >&2 echo "  status=$status"
    >&2 echo "  dependent=$dependent"

    if [ -n "$name" ] && [ -n "$version" ] && [ -n "$location" ] && [ -n "$role" ]; then
        echo "$name|$version|$created|$modified|$creator|$modified_by|$description|$location|$role|$status|$dependent"
    else
        >&2 echo "Debug: Skipping $file: name=$name, version=$version, location=$location, role=$role"
        echo ""
    fi
}

# Function to prompt for component update/insert (now automated)
prompt_component() {
    local name="$1" version="$2" created="$3" modified="$4" creator="$5" modified_by="$6" description="$7" location="$8" role="$9" status="${10}" dependent="${11}"
    local existing current_version current_modified current_modified_by

    existing=$($PSQL -t -c "SELECT version, modified, modified_by FROM component_versions WHERE name = '$name' AND role = '$role' AND location = '$location';" 2>/dev/null) || true
    if [ -n "$existing" ]; then
        IFS='|' read -r current_version current_modified current_modified_by <<< "$existing"
        echo "Updating $name ($role in $location):"
        echo "Version: $version (current: $current_version)"
        echo "Modified: $modified (current: $current_modified)"
        echo "Modified By: $modified_by (current: $current_modified_by)"
        $PSQL -c "UPDATE component_versions SET version = '$version', modified = '$modified', modified_by = '$modified_by', description = '$description', status = '$status', dependent = '$dependent'::boolean WHERE name = '$name' AND role = '$role' AND location = '$location';" || true
        echo "Automatically updated $name in component_versions table."
    else
        $PSQL -c "INSERT INTO component_versions (name, version, created, modified, creator, modified_by, description, location, role, status, dependent) VALUES ('$name', '$version', '$created', '$modified', '$creator', '$modified_by', '$description', '$location', '$role', '$status', '$dependent'::boolean);" || true
        echo "Automatically added $name to component_versions table."
    fi
}

# Main script
echo "Scanning ParcoRTLS components to populate the component_versions table..."
echo "Automatically processing directories and files (excluding: ${EXCLUDE_DIRS[*]})."
echo "All components (new and existing) will be added/updated automatically."
echo

# Step 1: Set database credentials
password='menu19'
export PGPASSWORD="$password"
echo "Debug: PGPASSWORD exported"
PSQL="psql -U menu19 -h localhost -d ParcoRTLSMaint"
echo "Debug: PSQL command set"

# Check database connectivity
connect_output=$($PSQL -c "SELECT 1;" 2>&1)
if [ $? -ne 0 ]; then
    echo "Error: Cannot connect to database. Details:"
    echo "$connect_output"
    echo "Check password, server, port, or database configuration."
    exit 1
fi
echo "Debug: Database connection successful"

# Step 2: Delete __init__.py entries
echo "Deleting __init__.py entries from component_versions table..."
delete_output=$($PSQL -c "DELETE FROM component_versions WHERE name = '__init__.py';" 2>&1)
if [ $? -ne 0 ]; then
    echo "Error: Failed to delete __init__.py entries. Details:"
    echo "$delete_output"
    echo "This may indicate a permissions issue. Please ensure the user 'menu19' has DELETE privileges on the component_versions table."
    echo "You can grant permissions with: GRANT SELECT, INSERT, UPDATE, DELETE ON component_versions TO menu19;"
    exit 1
fi
echo "Deletion of __init__.py entries completed."

# Step 3: Scan directories
directories=$(find "$BASE_DIR" -type d -not -path "*/node_modules/*" | sort)
file_components=()
for dir in $directories; do
    if should_exclude_dir "$dir"; then
        echo "Debug: Skipping excluded directory: $dir"
        continue
    fi
    echo "Debug: Processing directory: $dir"
    files=$(find "$dir" -maxdepth 1 -type f -not -path "*/node_modules/*" \( -name "*.sh" -o -name "*.py" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.txt" -o -name "*.js" -o -name "*.jsx" \))
    for file in $files; do
        # Check if file exists
        if [ ! -f "$file" ]; then
            echo "Debug: Skipping non-existent file: $file"
            continue
        fi
        # Check if file should be excluded
        if should_exclude_file "$file"; then
            echo "Debug: Skipping excluded file: $file"
            continue
        fi
        echo "Debug: Processing file: $file"
        # Automatically add comment block if missing
        if ! grep -q "^# Name:\|^<!-- Name:\|^/\* Name:" "$file" 2>/dev/null; then
            if add_comment_block "$file" "$(basename "$file")"; then
                echo "Added comment block to $file."
            else
                echo "Skipped adding comment block to $file (unsupported type or .json)."
            fi
        fi
        metadata=$(extract_metadata_from_file "$file")
        if [ -n "$metadata" ]; then
            file_components+=("$metadata")
        else
            echo "No valid metadata in $file. Skipping."
        fi
    done
done

# Step 4: Process components
all_components=("${file_components[@]}")
for component in "${all_components[@]}"; do
    IFS='|' read -r name version created modified creator modified_by description location role status dependent <<< "$component"
    prompt_component "$name" "$version" "$created" "$modified" "$creator" "$modified_by" "$description" "$location" "$role" "$status" "$dependent"
    echo
done

echo "Population process completed."
unset PGPASSWORD