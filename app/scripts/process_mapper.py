"""
Version: 250226 process_mapper.py Version 0P.1B.03

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import subprocess
import psutil
import json
import logging
import paho.mqtt.publish as publish

# Version
VERSION = "0P.1B.03"

# MQTT Settings
MQTT_BROKER = "localhost"
MQTT_TOPIC = "parco/process_mapper/status"

# Configure Logging
logging.basicConfig(
    filename="process_mapper.log",
    level=logging.INFO,
    format="%(asctime)s - INFO - [Version: " + VERSION + "] Port: %(message)s"
)

def send_mqtt_status(port, service_name):
    """Publishes an MQTT message with detected service name."""
    try:
        payload = json.dumps({
            "version": VERSION,
            "port": port,
            "service": service_name
        })
        publish.single(MQTT_TOPIC, payload, hostname=MQTT_BROKER, qos=1, retain=False)
        logging.info(f"{port} | Service: {service_name}")
        print(f"MQTT message sent: {payload}")
    except Exception as e:
        logging.error(f"Failed to send MQTT message: {e}")
        print(f"Failed to send MQTT message: {e}")

def get_pid_for_port(port):
    """Find the process ID (PID) associated with a given port using lsof."""
    try:
        result = subprocess.run(["sudo", "lsof", "-i", f":{port}", "-t"], stdout=subprocess.PIPE, text=True)
        output = result.stdout.strip()
        if output:
            return int(output.split("\n")[0])  # Use first PID
    except Exception as e:
        logging.error(f"Error using lsof for port {port}: {e}")
    return None

def get_process_name(pid):
    """Get process name from PID using psutil and detect Flask or FastAPI apps."""
    try:
        process = psutil.Process(pid)
        cmdline = " ".join(process.cmdline())

        if "map_upload" in cmdline:
            return "Map Upload (Python)"
        elif "zonebuilder_api" in cmdline:
            return "Zone Builder (Python)"
        elif "app" in cmdline or "uvicorn" in cmdline:
            return "App (FastAPI)"
        return process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown Service"

def check_docker_proxy(port):
    """If docker-proxy is detected, find the actual container running on that port."""
    try:
        result = subprocess.run(
            ["sudo", "docker", "ps", "--format", "{{.ID}}\t{{.Image}}\t{{.Ports}}"],
            stdout=subprocess.PIPE, text=True
        )
        lines = result.stdout.split("\n")
        for line in lines:
            if f"0.0.0.0:{port}" in line or f"::{port}" in line:
                container_info = line.split("\t")
                if len(container_info) > 1:
                    return f"Parco RTLS Backend ({container_info[1]})"
    except Exception as e:
        logging.error(f"Error checking Docker for port {port}: {e}")
    return "docker-proxy"

def get_service_name(port):
    """Finds which process is using the port and handles special cases."""
    pid = get_pid_for_port(port)
    if pid:
        service_name = get_process_name(pid)
        if service_name == "docker-proxy":
            service_name = check_docker_proxy(port)
        return service_name
    return "Unknown Service"

if __name__ == "__main__":
    logging.info(f"Starting process_mapper.py Version {VERSION}")
    
    test_ports = [5000, 5001, 5002, 5004, 5432, 8000, 8123]
    detected_services = {}

    for port in test_ports:
        service = get_service_name(port)
        detected_services[port] = service
        print(f"Port {port}: {service}")

    # Send MQTT messages **only once per port** (prevents duplicate messages)
    for port, service in detected_services.items():
        send_mqtt_status(port, service)

    logging.info(f"Completed process_mapper.py Version {VERSION}")
