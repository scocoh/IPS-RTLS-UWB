# Name: 22-fix_log_permissions.sh
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS utility script
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Utility
# Status: Active
# Dependent: TRUE

#!/bin/bash
chmod -R 775 /home/parcoadmin/parco_fastapi/app/logs
chown -R parcoadmin:parcoadmin /home/parcoadmin/parco_fastapi/app/logs
echo "Permissions and ownership updated for /home/parcoadmin/parco_fastapi/app/logs"