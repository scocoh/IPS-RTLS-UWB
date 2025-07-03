# Name: server_config.py
# Version: 0.1.0
# Created: 250702
# Modified: 250702
# Creator: ParcoAdmin & TC
# Modified By: ParcoAdmin
# Description: Centralized server configuration for ParcoRTLS
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Configuration
# Status: Active
# Dependent: TRUE

# Central server configuration
SERVER_IP = "192.168.210.226"
SERVER_PORT_MAIN = 8000
SERVER_PORT_MANAGER = 8001
SERVER_PORT_HISTORICAL = 8003
DB_PORT = 5432

# Database credentials
DB_USER = "parcoadmin"
DB_PASSWORD = "parcoMCSE04106!"

# MQTT Configuration
MQTT_BROKER_LOCAL = "127.0.0.1"