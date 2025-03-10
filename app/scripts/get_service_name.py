"""
Version: 250226 get_service_name.py Version 0P.1B.05

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import subprocess
import psutil
import logging

# ✅ Configure Logging
log_file = "/home/parcoadmin/parco_fastapi/app/scripts/get_service_name.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_pid_for_port(port):
    """Find the process ID (PID) associated with a given port using lsof."""
    try:
        result = subprocess.run(["sudo", "lsof", "-i", f":{port}", "-t"], stdout=subprocess.PIPE, text=True)
        output = result.stdout.strip()
        logging.info(f"lsof output for port {port} -> {output}")

        if output:
            pids = output.split("\n")
            logging.info(f"Found PIDs {pids} for port {port}")
            return int(pids[0])  # Use first PID
    except Exception as e:
        logging.error(f"Error using lsof: {e}")

    logging.info(f"No PID found for port {port}")
    return None

def get_process_name(pid):
    """Get process name from PID using psutil and detect Flask or FastAPI apps."""
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        cmdline = " ".join(process.cmdline())

        if "map_upload" in cmdline:
            return "Map Upload (Python)"
        elif "zonebuilder_api" in cmdline:
            return "Zone Builder (Python)"
        elif "app" in cmdline or "uvicorn" in cmdline:
            return "App (FastAPI)"
        
        return process_name
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        logging.warning(f"psutil could not get process name for PID {pid}, trying ps command...")

    try:
        result = subprocess.run(["ps", "-p", str(pid), "-o", "comm="], stdout=subprocess.PIPE, text=True)
        process_name = result.stdout.strip()
        logging.info(f"ps found process name for PID {pid} -> {process_name}")
        return process_name if process_name else "Unknown Service"
    except Exception as e:
        logging.error(f"Failed to get process name for PID {pid} -> {e}")
        return "Unknown Service"

def get_service_name(port):
    """Finds which process is using the port and checks for Docker containers if necessary."""
    pid = get_pid_for_port(port)
    if pid:
        service_name = get_process_name(pid)

        if service_name == "docker-proxy":
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
                logging.error(f"Error checking Docker: {e}")

        logging.info(f"Service for port {port} -> {service_name}")
        return service_name

    logging.info(f"No process found for port {port}")
    return "Unknown Service"

if __name__ == "__main__":
    test_ports = [5000, 5001, 5002, 5432, 8000, 8123]
    for port in test_ports:
        service = get_service_name(port)
        print(f"Port {port}: {service}")
        logging.info(f"Port {port}: {service}")
