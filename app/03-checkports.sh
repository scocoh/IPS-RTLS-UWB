#!/bin/bash
# Name: 03-checkports.sh
# Version: 0.1.3
# Created: 240101
# Modified: 250604
# Creator: ParcoAdmin
# Description: Check if critical ParcoRTLS dev ports are in use
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active

echo -e "\n🔍 Checking critical dev ports: 3000 8000 8001 8002 8003 8004 8005 8006 8007 8998 9000"
echo "---------------------------------------------"

ports=(3000 8000 8001 8002 8003 8004 8005 8006 8007 8998 9000)

for port in "${ports[@]}"; do
  pid_info=$(sudo netstat -tulnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1)

  if [[ -n "$pid_info" ]]; then
    cmd_info=$(ps -p "$pid_info" -o user=,cmd= 2>/dev/null)
    user=$(echo "$cmd_info" | awk '{print $1}')
    cmd=$(echo "$cmd_info" | cut -d' ' -f2-)
    echo -e "⚠️  Port $port is in use!"
    echo -e "    ├─ PID   : $pid_info"
    echo -e "    ├─ User  : $user"
    echo -e "    └─ Cmd   : $cmd"
  else
    echo -e "✅ Port $port is available"
  fi
done

echo -e "\n🧩 Suggestion: If ports are stuck, run: devstop"
echo -e "\n📥 Press ENTER to return to the menu..."
read