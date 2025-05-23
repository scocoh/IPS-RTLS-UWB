#!/bin/bash
# Name: 24-logpane_tmux.sh
# Usage: /home/parcoadmin/parco_fastapi/app/24-logpane_tmux.sh [start|stop|start-all|stop-all|list|tail|cleanup|status] [PANE_NUM]
# DESC: Enhanced tmux pane logging utility with auto-detection and bulk operations

SESSION="parco-dev"
ACTION=$1
PANE_NUM=$2
LOGDIR="$HOME/logs"
TRACKING_FILE="$LOGDIR/.active_logs"

# Ensure log directory and tracking file exist
mkdir -p "$LOGDIR"
touch "$TRACKING_FILE"

# Function to get all active panes
get_active_panes() {
    tmux list-panes -t $SESSION:0 -F "#{pane_index}" 2>/dev/null | sort -n
}

# Function to check if a pane exists
pane_exists() {
    local pane=$1
    tmux list-panes -t $SESSION:0 2>/dev/null | grep -q "^$pane:"
}

# Function to check if pane is already being logged
is_logging() {
    local pane=$1
    grep -q "^$pane:" "$TRACKING_FILE" 2>/dev/null
}

# Function to add log entry to tracking file
add_log_entry() {
    local pane=$1
    local logfile=$2
    echo "$pane:$logfile:$(date +%s)" >> "$TRACKING_FILE"
}

# Function to remove log entry from tracking file
remove_log_entry() {
    local pane=$1
    grep -v "^$pane:" "$TRACKING_FILE" > "$TRACKING_FILE.tmp" 2>/dev/null
    mv "$TRACKING_FILE.tmp" "$TRACKING_FILE"
}

# Function to start logging for a single pane
start_logging() {
    local pane=$1
    
    if ! pane_exists "$pane"; then
        echo "❗ Pane $pane does not exist in session $SESSION"
        return 1
    fi
    
    if is_logging "$pane"; then
        echo "⚠️  Pane $pane is already being logged"
        return 1
    fi
    
    local logfile="$LOGDIR/pane-${pane}-$(date +%Y%m%d-%H%M%S).log"
    tmux pipe-pane -o -t $SESSION:0.$pane "cat >> $logfile"
    add_log_entry "$pane" "$logfile"
    echo "✅ Logging started for pane $pane → $logfile"
}

# Function to stop logging for a single pane
stop_logging() {
    local pane=$1
    
    if ! pane_exists "$pane"; then
        echo "❗ Pane $pane does not exist in session $SESSION"
        return 1
    fi
    
    if ! is_logging "$pane"; then
        echo "⚠️  Pane $pane is not currently being logged"
        return 1
    fi
    
    tmux pipe-pane -t $SESSION:0.$pane
    remove_log_entry "$pane"
    echo "🛑 Logging stopped for pane $pane"
}

# Function to start logging for all active panes
start_all_logging() {
    echo "🚀 Starting logging for all active panes..."
    local panes=($(get_active_panes))
    local started=0
    
    if [ ${#panes[@]} -eq 0 ]; then
        echo "❗ No active panes found in session $SESSION"
        return 1
    fi
    
    for pane in "${panes[@]}"; do
        if ! is_logging "$pane"; then
            start_logging "$pane"
            ((started++))
        else
            echo "⚠️  Pane $pane already logging - skipped"
        fi
    done
    
    echo "✅ Started logging for $started pane(s)"
}

# Function to stop logging for all active panes
stop_all_logging() {
    echo "🛑 Stopping logging for all active panes..."
    local stopped=0
    
    # Read from tracking file and stop each logged pane
    while IFS=: read -r pane logfile timestamp; do
        if [[ -n "$pane" ]] && pane_exists "$pane"; then
            tmux pipe-pane -t $SESSION:0.$pane
            echo "🛑 Stopped logging for pane $pane"
            ((stopped++))
        fi
    done < "$TRACKING_FILE"
    
    # Clear tracking file
    > "$TRACKING_FILE"
    echo "✅ Stopped logging for $stopped pane(s)"
}

# Function to list active logs
list_logs() {
    echo "📋 Active Log Sessions"
    echo "====================="
    
    if [ ! -s "$TRACKING_FILE" ]; then
        echo "📭 No active logging sessions"
        return 0
    fi
    
    printf "%-4s %-50s %-12s %-8s\n" "Pane" "Log File" "Started" "Size"
    echo "--------------------------------------------------------------------"
    
    while IFS=: read -r pane logfile timestamp; do
        if [[ -n "$pane" && -f "$logfile" ]]; then
            local started_time=$(date -d "@$timestamp" "+%H:%M:%S" 2>/dev/null || echo "Unknown")
            local file_size=$(du -h "$logfile" 2>/dev/null | cut -f1 || echo "N/A")
            printf "%-4s %-50s %-12s %-8s\n" "$pane" "$(basename "$logfile")" "$started_time" "$file_size"
        fi
    done < "$TRACKING_FILE"
}

# Function to tail a specific log
tail_log() {
    local pane=$1
    
    if [[ -z "$pane" ]]; then
        echo "📋 Available logs to tail:"
        list_logs
        echo
        read -p "Enter pane number to tail: " pane
    fi
    
    local logfile=$(grep "^$pane:" "$TRACKING_FILE" | cut -d: -f2)
    
    if [[ -z "$logfile" ]]; then
        echo "❗ No active log found for pane $pane"
        return 1
    fi
    
    if [[ ! -f "$logfile" ]]; then
        echo "❗ Log file not found: $logfile"
        return 1
    fi
    
    echo "📖 Tailing log for pane $pane (Ctrl+C to exit):"
    echo "File: $logfile"
    echo "----------------------------------------"
    tail -f "$logfile"
}

# Function to cleanup old logs
cleanup_logs() {
    echo "🧹 Log Cleanup Utility"
    echo "======================"
    
    # Count total log files
    local total_logs=$(find "$LOGDIR" -name "pane-*.log" | wc -l)
    echo "📊 Found $total_logs log file(s) in $LOGDIR"
    
    if [ $total_logs -eq 0 ]; then
        echo "✅ No log files to clean up"
        return 0
    fi
    
    echo
    echo "Cleanup options:"
    echo " [1] Delete logs older than 7 days"
    echo " [2] Delete logs older than 30 days"
    echo " [3] Delete logs older than custom days"
    echo " [4] Show log file sizes and let me choose"
    echo " [5] Cancel"
    echo
    read -p "Select cleanup option: " cleanup_choice
    
    case "$cleanup_choice" in
        1) cleanup_by_age 7 ;;
        2) cleanup_by_age 30 ;;
        3) 
            read -p "Enter number of days: " custom_days
            if [[ "$custom_days" =~ ^[0-9]+$ ]]; then
                cleanup_by_age "$custom_days"
            else
                echo "❗ Invalid number of days"
            fi
            ;;
        4) interactive_cleanup ;;
        5) echo "❌ Cleanup cancelled" ;;
        *) echo "❗ Invalid option" ;;
    esac
}

# Function to cleanup logs by age
cleanup_by_age() {
    local days=$1
    echo "🗑️  Deleting logs older than $days days..."
    
    local deleted=0
    while IFS= read -r -d '' logfile; do
        echo "Deleting: $(basename "$logfile")"
        rm "$logfile"
        ((deleted++))
    done < <(find "$LOGDIR" -name "pane-*.log" -mtime +$days -print0)
    
    echo "✅ Deleted $deleted old log file(s)"
    
    # Clean up tracking file entries for deleted logs
    cleanup_tracking_file
}

# Function for interactive cleanup
interactive_cleanup() {
    echo "📁 Log Files (sorted by size):"
    echo "============================="
    
    find "$LOGDIR" -name "pane-*.log" -exec du -h {} + | sort -rh | nl
    
    echo
    echo "Enter file numbers to delete (space-separated), or 'all' for all files:"
    read -p "Files to delete: " selection
    
    if [[ "$selection" == "all" ]]; then
        read -p "⚠️  Delete ALL log files? (y/N): " confirm
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            rm "$LOGDIR"/pane-*.log
            > "$TRACKING_FILE"
            echo "✅ All log files deleted"
        fi
    else
        # Handle specific file numbers - simplified for this example
        echo "❗ Specific file deletion not implemented yet"
    fi
}

# Function to cleanup tracking file
cleanup_tracking_file() {
    local temp_file="$TRACKING_FILE.cleanup"
    > "$temp_file"
    
    while IFS=: read -r pane logfile timestamp; do
        if [[ -n "$pane" && -f "$logfile" ]]; then
            echo "$pane:$logfile:$timestamp" >> "$temp_file"
        fi
    done < "$TRACKING_FILE"
    
    mv "$temp_file" "$TRACKING_FILE"
}

# Function to show status
show_status() {
    echo "🔍 Tmux Logging Status"
    echo "======================"
    echo "Session: $SESSION"
    echo "Log Directory: $LOGDIR"
    echo
    
    local active_panes=($(get_active_panes))
    echo "📊 Active Panes: ${#active_panes[@]}"
    
    if [ ${#active_panes[@]} -gt 0 ]; then
        echo "Panes: ${active_panes[*]}"
        echo
        
        for pane in "${active_panes[@]}"; do
            if is_logging "$pane"; then
                echo "  Pane $pane: 🟢 Logging"
            else
                echo "  Pane $pane: 🔴 Not logging"
            fi
        done
    fi
    
    echo
    list_logs
}

# Main logic
case "$ACTION" in
    "start")
        if [[ -z "$PANE_NUM" ]]; then
            echo "❗ Usage: $0 start <pane_number>"
            exit 1
        fi
        start_logging "$PANE_NUM"
        ;;
    "stop")
        if [[ -z "$PANE_NUM" ]]; then
            echo "❗ Usage: $0 stop <pane_number>"
            exit 1
        fi
        stop_logging "$PANE_NUM"
        ;;
    "start-all")
        start_all_logging
        ;;
    "stop-all")
        stop_all_logging
        ;;
    "list")
        list_logs
        ;;
    "tail")
        tail_log "$PANE_NUM"
        ;;
    "cleanup")
        cleanup_logs
        ;;
    "status")
        show_status
        ;;
    *)
        echo "❗ Usage: $0 {start|stop|start-all|stop-all|list|tail|cleanup|status} [pane_number]"
        echo
        echo "Commands:"
        echo "  start <pane>    - Start logging for specific pane"
        echo "  stop <pane>     - Stop logging for specific pane"
        echo "  start-all       - Start logging for all active panes"
        echo "  stop-all        - Stop logging for all active panes"
        echo "  list            - List active logging sessions"
        echo "  tail [pane]     - Tail log file for pane"
        echo "  cleanup         - Clean up old log files"
        echo "  status          - Show current logging status"
        exit 1
        ;;
esac