#!/bin/bash
# DESC: Initial ParcoRTLS setup script — installs dependencies, creates config files, etc.

# VERSION 0P.1B.01

# ===================================
# ParcoRTLS Setup Script
# ===================================
# This script automates the setup of the ParcoRTLS environment, including:
# - Installing system dependencies
# - Configuring PostgreSQL
# - Setting up Mosquitto MQTT broker
# - Configuring Python virtual environment
# - Setting up systemd services for backend and frontend
# - Optionally enabling automatic GitHub updates
# ===================================

echo "Setup script for ParcoRTLS Linux deployment"
# Add installation logic here (to be filled in later)

# ----------------------------------
# Step 1: Prompt for IP Address
# ----------------------------------
read -p "Enter the IP address of this server (e.g., 10.0.0.134): " SERVER_IP
if [[ -z "$SERVER_IP" ]]; then
    echo "Error: IP address cannot be empty. Exiting."
    exit 1
fi
echo "Using IP address: $SERVER_IP"

# Define variables
INSTALL_DIR="/home/parcoadmin/parco_fastapi/app"
VENV_DIR="/home/parcoadmin/parco_fastapi/venv"
GITHUB_REPO="https://github.com/scocoh/IPS-RTLS-UWB.git"  # Change to the actual repo
GITHUB_BRANCH="linux"  # Use the Linux branch when uploading
DB_USER="parcoadmin"
DB_PASSWORD="parcoMCSE04106!"
DB_NAME="ParcoRTLSMaint"

# Ensure script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root. Try using: sudo ./setup.sh"
   exit 1
fi

# ----------------------------------
# Step 2: Update System & Install Dependencies
# ----------------------------------
echo "Updating system and installing dependencies..."
apt update && apt upgrade -y
apt install -y python3.12 python3.12-venv python3.12-dev python3-pip git unzip nano curl wget \
               postgresql postgresql-contrib libpq-dev mosquitto mosquitto-clients nodejs npm

# ----------------------------------
# Step 3: Configure PostgreSQL
# ----------------------------------
echo "Configuring PostgreSQL..."
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD' CREATEDB CREATEROLE;"
sudo -u postgres psql -c "ALTER USER $DB_USER WITH SUPERUSER;"

echo "Checking if database $DB_NAME exists..."
DB_EXIST=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")
if [[ "$DB_EXIST" == "1" ]]; then
    echo "Database $DB_NAME already exists. Skipping creation."
else
    echo "Creating database $DB_NAME..."
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
fi

# Enable remote access (change 0.0.0.0 to allow external access if needed)
echo "Configuring PostgreSQL to listen on all interfaces..."
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '0.0.0.0'/g" /etc/postgresql/16/main/postgresql.conf
echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/16/main/pg_hba.conf
systemctl restart postgresql

# ----------------------------------
# Step 4: Set Up Python Virtual Environment
# ----------------------------------
echo "Setting up Python virtual environment..."
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt  # Ensure requirements.txt is in the repo

# ----------------------------------
# Step 5: Clone Repository & Configure
# ----------------------------------
echo "Cloning ParcoRTLS repository..."
if [ ! -d "$INSTALL_DIR/.git" ]; then
    git clone --branch $GITHUB_BRANCH $GITHUB_REPO $INSTALL_DIR
else
    echo "Repository already cloned. Skipping."
fi

# Update configuration files with user-provided IP
echo "Updating configuration files..."
sed -i "s/192.168.210.226/$SERVER_IP/g" $(grep -rl "192.168.210.226" $INSTALL_DIR --exclude-dir=node_modules --exclude=*.log)

# ----------------------------------
# Step 6: Set Up Systemd Services
# ----------------------------------
echo "Setting up systemd services..."

# Backend service
cat <<EOF | tee /etc/systemd/system/parco_backend.service
[Unit]
Description=Parco RTLS Backend API
After=network.target postgresql.service mosquitto.service

[Service]
User=parcoadmin
WorkingDirectory=$INSTALL_DIR
ExecStart=$VENV_DIR/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --reload
Restart=always
RestartSec=5
StandardOutput=append:$INSTALL_DIR/uvicorn.log
StandardError=append:$INSTALL_DIR/uvicorn.log

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
cat <<EOF | tee /etc/systemd/system/parco_frontend.service
[Unit]
Description=Parco RTLS Frontend Service
After=network.target parco_backend.service

[Service]
User=parcoadmin
WorkingDirectory=$INSTALL_DIR
ExecStart=npm start
Restart=always
RestartSec=5
Environment=PORT=3000
StandardOutput=append:$INSTALL_DIR/frontend.log
StandardError=append:$INSTALL_DIR/frontend.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable services
echo "Enabling and starting systemd services..."
systemctl daemon-reload
systemctl enable parco_backend.service parco_frontend.service
systemctl start parco_backend.service parco_frontend.service

# ----------------------------------
# Step 7: MQTT Broker Configuration
# ----------------------------------
echo "Setting up Mosquitto MQTT Broker..."
systemctl enable mosquitto
systemctl start mosquitto

# ----------------------------------
# Step 8: Optional GitHub Auto-Update Setup
# ----------------------------------
read -p "Do you want to enable automatic updates from GitHub? (y/n) " update_choice
if [[ $update_choice == "y" || $update_choice == "Y" ]]; then
    cat <<EOF | tee /etc/systemd/system/parco_update.service
[Unit]
Description=ParcoRTLS Auto Update
After=network.target

[Service]
User=parcoadmin
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/update.sh
Restart=always
RestartSec=86400  # Check once a day

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable parco_update.service
    systemctl start parco_update.service
    echo "GitHub auto-update enabled."
else
    echo "GitHub auto-update is disabled. You can manually update using ./update.sh"
fi

# ----------------------------------
# Step 9: Final Check & Completion
# ----------------------------------
echo "Finalizing installation..."
echo "Backend status:"
systemctl status parco_backend.service --no-pager | tail -10
echo "Frontend status:"
systemctl status parco_frontend.service --no-pager | tail -10
echo "MQTT Broker status:"
systemctl status mosquitto --no-pager | tail -10
echo "PostgreSQL status:"
systemctl status postgresql --no-pager | tail -10

echo "Installation complete! You can access:"
echo "  Backend API: http://$SERVER_IP:8000/docs"
echo "  Frontend UI: http://$SERVER_IP:3000"

exit 0
