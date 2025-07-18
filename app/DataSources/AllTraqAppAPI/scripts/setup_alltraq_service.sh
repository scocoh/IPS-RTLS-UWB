#!/bin/bash
# Name: setup_alltraq_service.sh
# Version: 0.1.0
# Created: 250712
# Modified: 250712
# Creator: ParcoAdmin + Claude
# Description: Setup and management script for AllTraq Service
# Location: /home/parcoadmin/parco_fastapi/app/scripts
# Role: Service Management
# Status: Active
# Dependent: FALSE

# AllTraq is a registered trademark of ABG Tag and Traq Inc (Oklahoma) Serial Num 87037989 for Goods & Service IC 009

echo "========================================"
echo "AllTraq Service Setup and Management"
echo "========================================"

# Configuration
ALLTRAQ_SERVICE_DIR="/home/parcoadmin/parco_fastapi/app/services"
ALLTRAQ_SERVICE_FILE="alltraq_service.py"
ALLTRAQ_LOG_FILE="/home/parcoadmin/parco_fastapi/app/logs/alltraq_service.log"

# Ensure services directory exists
mkdir -p "$ALLTRAQ_SERVICE_DIR"

show_menu() {
    echo
    echo "AllTraq Service Management Menu:"
    echo "1. Install AllTraq Service"
    echo "2. Start AllTraq Service"
    echo "3. Stop AllTraq Service"
    echo "4. Check Service Status"
    echo "5. View Service Logs"
    echo "6. Test AllTraq API Connection"
    echo "7. Register in Database (Optional)"
    echo "8. Remove AllTraq Service"
    echo "9. Exit"
    echo
}

install_service() {
    echo "Installing AllTraq Service..."
    
    # Check if file exists
    if [ -f "$ALLTRAQ_SERVICE_DIR/$ALLTRAQ_SERVICE_FILE" ]; then
        echo "✅ AllTraq service file found at $ALLTRAQ_SERVICE_DIR/$ALLTRAQ_SERVICE_FILE"
    else
        echo "❌ AllTraq service file not found!"
        echo "Please copy alltraq_service.py to $ALLTRAQ_SERVICE_DIR/"
        return 1
    fi
    
    # Test Python imports
    echo "Testing Python dependencies..."
    cd /home/parcoadmin/parco_fastapi/app
    
    if python3 -c "import aiohttp, websockets, asyncio; print('✅ Dependencies OK')" 2>/dev/null; then
        echo "✅ All dependencies available"
    else
        echo "❌ Missing dependencies. Installing..."
        pip3 install aiohttp websockets
    fi
    
    echo "✅ AllTraq Service installation complete"
}

start_service() {
    echo "Starting AllTraq Service..."
    
    # Check if already running
    if pgrep -f "alltraq_service.py" > /dev/null; then
        echo "⚠️  AllTraq Service already running (PID: $(pgrep -f alltraq_service.py))"
        return 0
    fi
    
    # Start service in background
    cd /home/parcoadmin/parco_fastapi/app
    nohup python3 services/alltraq_service.py > "$ALLTRAQ_LOG_FILE" 2>&1 &
    
    sleep 2
    
    if pgrep -f "alltraq_service.py" > /dev/null; then
        echo "✅ AllTraq Service started (PID: $(pgrep -f alltraq_service.py))"
        echo "📄 Logs: $ALLTRAQ_LOG_FILE"
    else
        echo "❌ Failed to start AllTraq Service"
        echo "Check logs: tail -f $ALLTRAQ_LOG_FILE"
    fi
}

stop_service() {
    echo "Stopping AllTraq Service..."
    
    if pgrep -f "alltraq_service.py" > /dev/null; then
        pkill -f "alltraq_service.py"
        sleep 2
        
        if ! pgrep -f "alltraq_service.py" > /dev/null; then
            echo "✅ AllTraq Service stopped"
        else
            echo "⚠️  Force killing AllTraq Service..."
            pkill -9 -f "alltraq_service.py"
            echo "✅ AllTraq Service force stopped"
        fi
    else
        echo "ℹ️  AllTraq Service not running"
    fi
}

check_status() {
    echo "AllTraq Service Status:"
    echo "======================"
    
    if pgrep -f "alltraq_service.py" > /dev/null; then
        PID=$(pgrep -f "alltraq_service.py")
        echo "✅ Status: RUNNING"
        echo "📋 PID: $PID"
        echo "⏰ Started: $(ps -o lstart= -p $PID)"
        echo "💾 Memory: $(ps -o rss= -p $PID | awk '{print $1/1024 " MB"}')"
    else
        echo "❌ Status: STOPPED"
    fi
    
    echo
    echo "Log file: $ALLTRAQ_LOG_FILE"
    if [ -f "$ALLTRAQ_LOG_FILE" ]; then
        echo "📊 Log size: $(du -h "$ALLTRAQ_LOG_FILE" | cut -f1)"
        echo "📅 Last modified: $(stat -c %y "$ALLTRAQ_LOG_FILE")"
    else
        echo "📄 No log file found"
    fi
}

view_logs() {
    echo "AllTraq Service Logs:"
    echo "===================="
    
    if [ -f "$ALLTRAQ_LOG_FILE" ]; then
        echo "Last 50 lines (press 'q' to quit, 'f' to follow):"
        echo
        tail -50 "$ALLTRAQ_LOG_FILE"
        echo
        read -p "Follow live logs? (y/n): " follow
        if [ "$follow" = "y" ] || [ "$follow" = "Y" ]; then
            tail -f "$ALLTRAQ_LOG_FILE"
        fi
    else
        echo "❌ Log file not found: $ALLTRAQ_LOG_FILE"
    fi
}

test_api() {
    echo "Testing AllTraq API Connection..."
    echo "==============================="
    
    cd /home/parcoadmin/parco_fastapi/app
    
    # Create test script
    cat > test_alltraq_api.py << 'EOF'
import asyncio
import aiohttp
import sys

async def test_alltraq():
    bearer_token = "YmVjYmNhNDktOGQzZi00MWI0LTg2NmQtOWU1NTFiZTM0MzA3"
    api_url = "https://app.alltraq.com/api/TagStatus/GetByList/26010"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Accept": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ AllTraq API connection successful!")
                    print(f"Sample data keys: {list(data.keys()) if isinstance(data, dict) else 'List response'}")
                elif response.status == 401:
                    print("❌ Authentication failed - check bearer token")
                else:
                    text = await response.text()
                    print(f"❌ API error: {text[:200]}")
                    
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")

asyncio.run(test_alltraq())
EOF
    
    python3 test_alltraq_api.py
    rm test_alltraq_api.py
}

register_database() {
    echo "Registering AllTraq Service in Database (Optional):"
    echo "=================================================="
    
    read -p "Register AllTraq Service in tlkresources table? (y/n): " register
    if [ "$register" != "y" ] && [ "$register" != "Y" ]; then
        echo "Skipped database registration"
        return 0
    fi
    
    echo "Creating SQL registration script..."
    
    cat > register_alltraq.sql << 'EOF'
-- Register AllTraq Service as external data source
-- Resource Type: 2101 (Inbound AllTraq GeoTraqr)
-- Port: 0 (external service, no port needed)

INSERT INTO tlkresources (
    i_res, x_nm_res, x_ip, i_prt, i_rnk, f_fs, f_avg, i_typ_res
) VALUES (
    220, 'AllTraqService', '192.168.210.226', 0, 120, false, false, 2101
) ON CONFLICT (i_res) DO UPDATE SET
    x_nm_res = EXCLUDED.x_nm_res,
    x_ip = EXCLUDED.x_ip,
    i_prt = EXCLUDED.i_prt,
    i_rnk = EXCLUDED.i_rnk,
    f_fs = EXCLUDED.f_fs,
    f_avg = EXCLUDED.f_avg,
    i_typ_res = EXCLUDED.i_typ_res;

-- Verify registration
SELECT i_res, x_nm_res, x_ip, i_prt, i_typ_res 
FROM tlkresources 
WHERE x_nm_res = 'AllTraqService';
EOF
    
    echo "SQL script created: register_alltraq.sql"
    echo
    echo "To register, run:"
    echo "psql -U parcoadmin -d ParcoRTLSMaint -f register_alltraq.sql"
    echo
    read -p "Run registration now? (y/n): " run_now
    if [ "$run_now" = "y" ] || [ "$run_now" = "Y" ]; then
        psql -U parcoadmin -d ParcoRTLSMaint -f register_alltraq.sql
        rm register_alltraq.sql
        echo "✅ AllTraq Service registered in database"
    fi
}

remove_service() {
    echo "Removing AllTraq Service..."
    
    read -p "Are you sure you want to remove AllTraq Service? (y/n): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Removal cancelled"
        return 0
    fi
    
    # Stop service
    stop_service
    
    # Remove files
    if [ -f "$ALLTRAQ_SERVICE_DIR/$ALLTRAQ_SERVICE_FILE" ]; then
        rm "$ALLTRAQ_SERVICE_DIR/$ALLTRAQ_SERVICE_FILE"
        echo "✅ Removed service file"
    fi
    
    # Ask about logs
    read -p "Remove log files? (y/n): " remove_logs
    if [ "$remove_logs" = "y" ] || [ "$remove_logs" = "Y" ]; then
        rm -f "$ALLTRAQ_LOG_FILE"
        echo "✅ Removed log files"
    fi
    
    echo "✅ AllTraq Service removal complete"
}

# Main menu loop
while true; do
    show_menu
    read -p "Select option (1-9): " choice
    
    case $choice in
        1)
            install_service
            ;;
        2)
            start_service
            ;;
        3)
            stop_service
            ;;
        4)
            check_status
            ;;
        5)
            view_logs
            ;;
        6)
            test_api
            ;;
        7)
            register_database
            ;;
        8)
            remove_service
            ;;
        9)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid option. Please select 1-9."
            ;;
    esac
    
    echo
    read -p "Press Enter to continue..."
done