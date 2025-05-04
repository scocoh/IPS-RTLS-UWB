# Name: config.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

MQTT_BROKER = "127.0.0.1"

DB_CONFIGS_ASYNC = {
    "maint": {
        "database": "ParcoRTLSMaint",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    },
    "data": {
        "database": "ParcoRTLSData",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    },
    "hist_r": {
        "database": "ParcoRTLSHistR",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    },
    "hist_p": {
        "database": "ParcoRTLSHistP",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    },
    "hist_o": {
        "database": "ParcoRTLSHistO",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    }
}