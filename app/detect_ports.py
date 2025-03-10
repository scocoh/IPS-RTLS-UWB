#!/home/parcoadmin/parco_fastapi/venv/bin/python
import socket
import os
import psutil
import json
import paho.mqtt.publish as publish

MQTT_BROKER = "192.168.210.231"
MQTT_TOPIC = "homeassistant/sensor/rtls_ports"

def get_open_ports(host="192.168.210.231", port_range=(5000, 9000)):
    open_ports = {}
    
    for port in range(port_range[0], port_range[1]):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex((host, port)) == 0:
                service = get_service_name(port)
                open_ports[port] = service

    return open_ports

# Custom mapping of ports to friendly names
SERVICE_MAPPING = {
    5000: "Flask (Python)",
    5432: "PostgreSQL",
    8000: "FastAPI (Python3)",
    8123: "Home Assistant",
}

def get_service_name(port):
    """Finds the service running on a given port."""
    
    if port in SERVICE_MAPPING:
        print(f"Using custom mapping for port {port}: {SERVICE_MAPPING[port]}")
        return SERVICE_MAPPING[port]

    try:
        service = socket.getservbyport(port)
        print(f"Socket found service for port {port}: {service}")
        return service
    except OSError:
        print(f"Socket lookup failed for port {port}")

    # Match port to PID
    connections = psutil.net_connections(kind="inet")
    for conn in connections:
        if conn.laddr.port == port and conn.pid:
            try:
                process = psutil.Process(conn.pid)
                print(f"psutil found service for port {port}: {process.name()}")
                return process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"psutil failed for port {port}")
                return "Unknown Service"

    print(f"Returning 'Unknown Service' for port {port}")
    return "Unknown Service"

def publish_to_mqtt(open_ports):
    payload = json.dumps({"services": open_ports})
    publish.single(MQTT_TOPIC, payload, hostname=MQTT_BROKER)
    print("Published services:", payload)

if __name__ == "__main__":
    detected_ports = get_open_ports()
    publish_to_mqtt(detected_ports)
