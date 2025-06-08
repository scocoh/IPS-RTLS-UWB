#!/bin/bash
# Name: 24-logpane_tmux.sh
# Version: 0.1.4
# Created: Unknown
# Modified: 250607
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Enhanced tmux pane logging utility with auto-detection and bulk operations
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Note: Supports multiple sessions with session-specific tracking; fixed logging conflicts
# Usage: /home/parcoadmin/parco_fastapi/app/24-logpane_tmux.sh [start|stop|start-all|stop-all|list|tail|cleanup|status] [PANE_NUM] [SESSION]
# Changelog:
# - 0.1.4 (250607): Added session to tracking file; fixed is_logging for multi-session; enhanced error handling
# - 0.1.3 (250604): Added session name to log file names; fixed parameter handling
# - 0.1.2 (250604): Fixed session name display and ensured all 7 panes shown
# - 0.1.1 (250604): Added support for dynamic session names

ACTION=$1
shift
PANE_NUM=$1
SESSION_NAME=$2
SESSION=${SESSION_NAME:-parco-dev}
LOGDIR="$HOME/logs"
TRACKING_FILE="$LOGDIR/.active_logs"

# Redirect debug to a log file
echo "DEBUG: Received ACTION=$ACTION, PANE_NUM=$PANE_NUM, SESSION_NAME=$SESSION_NAME, using SESSION=$SESSION at $(date)" >> "$LOGDIR/debug.log"

# Ensure log directory and tracking file exist
mkdir -p "$LOGDIR"
touch "$TRACKING_FILE"

# Function to get all active panes
get_active_panes() {
    local panes=($(tmux list-panes -t $SESSION:0 -F "#{pane_index}" 2>/dev/null | sort -n))
    if [ ${#panes[@]} -lt 7 ]; then
        echo "⚠️  Warning: Only ${#panes[@]} panes detected in $SESSION (expected 7)" >&2
    fi
    echo "${panes[@]}"
}

# Function to check if a pane exists
pane_exists() {
    local pane=$1
    tmux list-panes -t $SESSION:0 2>/dev/null | grep -q "^$pane:"
}

# Function to check if pane is already being logged
is_logging() {
    local pane=$1
    # Original: grep -q "^$pane:" "$TRACKING_FILE"
    grep -q "^$SESSION:$pane:" "$TRACKING_FILE"
}

# Function to add log entry to tracking file
add_log_entry() {
    local pane=$1
    local logfile=$2
    # Original: echo "$pane:$logfile:$(date +%s)" >> "$TRACKING_FILE"
    echo "$SESSION:$pane:$logfile:$(date +%s)" >> "$TRACKING_FILE"
}

# Function to remove log entry from tracking file
remove_log_entry() {
    local pane=$1
    # Original: grep -v "^$pane:" "$TRACKING_FILE" > "$TRACKING_FILE.tmp" 2>/dev/null
    grep -v "^$SESSION:$pane:" "$TRACKING_FILE" > "$TRACKING_FILE.tmp" 2>/dev/null
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
        echo "⚠️  Pane $pane is already being logged in session $SESSION"
        return 1
    fi
    
    local logfile="$LOGDIR/pane-${pane}-${SESSION}-$(date +%Y%m%d-%H%M%S).log"
    tmux pipe-pane -o -t $SESSION:0.$pane "cat >> $logfile" 2>> "$LOGDIR/debug.log"
    if [ $? -ne 0 ]; then
        echo "❗ Failed to start logging for pane $pane in session $SESSION" >&2
        echo "DEBUG: tmux pipe-pane failed for pane $pane in session $SESSION" >> "$LOGDIR/debug.log"
        return 1
    fi
    add_log_entry "$pane" "$logfile"
    echo "✅ Logging started for pane $pane in session $SESSION → $logfile"
    return 0
}

# Function to stop logging for a single pane
stop_logging() {
    local pane=$1
    
    if ! pane_exists "$pane"; then
        echo "❗ Pane $pane does not exist in session $SESSION"
        return 1
    fi
    
    if ! is_logging "$pane"; then
        echo "⚠️  Pane $pane is not currently being logged in session $SESSION"
        return 1
    fi
    
    tmux pipe-pane -t $SESSION:0.$pane 2>> "$LOGDIR/debug.log"
    remove_log_entry "$pane"
    echo "🛑 Logging stopped for pane $pane in session $SESSION"
}

# Function to start logging for all active panes
start_all_logging() {
    echo "🚀 Starting logging for all active panes in session $SESSION..."
    local panes=($(get_active_panes))
    local started=0
    
    if [ ${#panes[@]} -eq 0 ]; then
        echo "❗ No active panes found in session $SESSION"
        return 1
    fi
    
    for pane in "${panes[@]}"; do
        if ! is_logging "$pane"; then
            if start_logging "$pane"; then
                ((started++))
            else
                echo "DEBUG: Failed to start logging for pane $pane in session $SESSION" >> "$LOGDIR/debug.log"
            fi
        else
            echo "⚠️  Pane $pane already logging in session $SESSION - skipped"
        fi
    done
    
    echo "✅ Started logging for $started pane(s) in session $SESSION"
}

# Function to stop logging for all active panes
stop_all_logging() {
    echo "🛑 Stopping logging for all active panes in session $SESSION..."
    local stopped=0
    
    while IFS=: read -r session pane logfile timestamp; do
        if [[ "$session" == "$SESSION" && -n "$pane" ]] && pane_exists "$pane"; then
            tmux pipe-pane -t $SESSION:0.$pane 2>> "$LOGDIR/debug.log"
            echo "🛑 Stopped logging for pane $pane in session $SESSION"
            ((stopped++))
        fi
    done < "$TRACKING_FILE"
    
    # Original: > "$TRACKING_FILE"
    grep -v "^$SESSION:" "$TRACKING_FILE" > "$TRACKING_FILE.tmp"
    mv "$TRACKING_FILE.tmp" "$TRACKING_FILE"
    echo "✅ Stopped logging for $stopped pane(s) in session $SESSION"
}

# Function to list active logs
list_logs() {
    echo "📋 Active Log Sessions for $SESSION"
    echo "================================="
    
    if ! grep -q "^$SESSION:" "$TRACKING_FILE"; then
        echo "📭 No active logging sessions for $SESSION"
        return 0
    fi
    
    printf "%-4s %-50s %-12s %-8s\n" "Pane" "Log File" "Started" "Size"
    echo "--------------------------------------------------------------------"
    
    while IFS=: read -r session pane logfile timestamp; do
        if [[ "$session" == "$SESSION" && -n "$pane" && -f "$logfile" ]]; then
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
        echo "📋 Available logs to tail for $SESSION:"
        list_logs
        echo
        read -p "Enter pane number to tail: " pane
    fi
    
    local logfile=$(grep "^$SESSION:$pane:" "$TRACKING_FILE" | cut -d: -f3)
    
    if [[ -z "$logfile" ]]; then
        echo "❗ No active log found for pane $pane in session $SESSION"
        return 1
    fi
    
    if [[ ! -f "$logfile" ]]; then
        echo "❗ Log file not found: $logfile"
        return 1
    fi
    
    echo "📖 Tailing log for pane $pane in session $SESSION (Ctrl+C to exit):"
    echo "File: $logfile"
    echo "----------------------------------------"
    tail -f "$logfile"
}

# Function to cleanup old logs
cleanup_logs() {
    echo "🧹 Log Cleanup Utility for $SESSION"
    echo "=================================="
    
    local total_logs=$(find "$LOGDIR" -name "pane-*-$SESSION-*.log" | wc -l)
    echo "📊 Found $total_logs log file(s) for $SESSION in $LOGDIR"
    
    if [ $total_logs -eq 0 ]; then
        echo "✅ No log files to clean up for $SESSION"
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
    echo "🗑️  Deleting logs older than $days days for $SESSION..."
    
    local deleted=0
    while IFS= read -r -d '' logfile; do
        echo "Deleting: $(basename "$logfile")"
        rm "$logfile"
        ((deleted++))
    done < <(find "$LOGDIR" -name "pane-*-$SESSION-*.log" -mtime +$days -print0)
    echo "✅ Deleted $deleted old log file(s)"
    
    cleanup_tracking_file
}

# Function for interactive cleanup
interactive_cleanup() {
    echo "📁 Log Files for $SESSION (sorted by size):"
    echo "========================================"
    
    find "$LOGDIR" -name "pane-*-$SESSION-*.log" -exec du -h {} + | sort -rh | nl
    
    echo
    echo "Enter file numbers to delete (space-separated), or 'all' for all files:"
    read -p "Files to delete: " selection
    
    if [[ "$selection" == "all" ]]; then
        read -p "⚠️  Delete ALL log files for $SESSION? (y/N): " confirm
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            rm "$LOGDIR"/pane-*-$SESSION-*.log
            grep -v "^$SESSION:" "$TRACKING_FILE" > "$TRACKING_FILE.tmp"
            mv "$TRACKING_FILE.tmp" "$TRACKING_FILE"
            echo "✅ All log files deleted for $SESSION"
        fi
    else
        echo "❗ Specific file deletion not implemented yet"
    fi
}

# Function to cleanup tracking file
cleanup_tracking_file() {
    local temp_file="$TRACKING_FILE.cleanup"
    > "$temp_file"
    
    while IFS=: read -r session pane logfile timestamp; do
        if [[ -n "$pane" && -f "$logfile" ]]; then
            echo "$session:$pane:$logfile:$timestamp" >> "$temp_file"
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
    else
        echo "⚠️  No active panes detected"
    fi
    echo
    
    for pane in {0..6}; do
        if [[ " ${active_panes[*]} " =~ " $pane " ]]; then
            if is_logging "$pane"; then
                echo "  Pane $pane: 🟢 Logging"
            else
                echo "  Pane $pane: 🔴 Not logging"
            fi
        else
            echo "  Pane $pane: ⚪ Not active"
        fi
    done
    
    echo
    list_logs
}

# Main logic
case "$ACTION" in
    "start")
        if [[ -z "$PANE_NUM" ]]; then
            echo "❗ Usage: $0 start <pane_number> [session]"
            exit 1
        fi
        start_logging "$PANE_NUM"
        ;;
    "stop")
        if [[ -z "$PANE_NUM" ]]; then
            echo "❗ Usage: $0 stop <pane_number> [session]"
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
        echo "❗ Usage: $0 {start|stop|start-all|stop-all|list|tail|cleanup|status} [pane_number] [session]"
        echo
        echo "Commands:"
        echo "  start <pane> [session]    - Start logging for specific pane"
        echo "  stop <pane> [session]     - Stop logging for specific pane"
        echo "  start-all [session]       - Start logging for all active panes"
        echo "  stop-all [session]        - Stop logging for all active panes"
        echo "  list [session]            - List active logging sessions"
        echo "  tail [pane] [session]     - Tail log file for pane"
        echo "  cleanup [session]         - Clean up old log files"
        echo "  status [session]          - Show current logging status"
        exit 1
        ;;
esac