```markdown
# ParcoRTLS Installation and Deployment Manual
**VERSION 0P.1B.01**

## Table of Contents
1. [System Requirements](#1-system-requirements)
2. [Installation Steps](#2-installation-steps)
   - [Native Automated Setup](#native-automated-setup)
   - [Docker Setup (Optional)](#docker-setup-optional)
3. [Systemd Services for Auto-Start](#3-systemd-services-for-auto-start)
4. [Managing the System](#4-managing-the-system)
5. [GitHub Setup for Development](#5-github-setup-for-development)
6. [Full Source Code for Configuration Files](#6-full-source-code-for-configuration-files)
7. [Instructions to Add to Visual Studio Code](#7-instructions-to-add-to-visual-studio-code)
8. [Verification](#8-verification)

---

## 1. System Requirements
- Ubuntu **24.04+** VM with **2 CPU cores, 4GB RAM**
- **Python 3.12+**
- **Node.js 18+** (via [NodeSource](https://nodesource.com))
- **PostgreSQL 16+**
- **Mosquitto MQTT broker**
- **Git**
- **Docker and Docker Compose** (optional)
- Additional: `libopencv-dev` for OpenCV support

---

## 2. Installation Steps

### Native Automated Setup
1. Run the following commands:
   ```bash
   curl -O https://raw.githubusercontent.com/scocoh/IPS-RTLS-UWB/main/parco_fastapi/Linux/scripts/setup.sh
   chmod +x setup.sh
   sudo ./setup.sh
   ```
2. Follow prompts to restore `parco_fastapi/Linux/db/PostgresQL_ALLDBs_backup.sql` or a custom backup.

3. Access the services:
   - **Backend:** `http://<server-ip>:8000`
   - **Frontend:** `http://<server-ip>:3000`

### Docker Setup (Optional) (it’s a placeholder for the user’s root directory.)
1. Start services using:
   ```bash
    cd /path/to/project_root
    docker-compose up -d
   ```
    Note: Replace /path/to/project_root with the actual root directory on the user’s system (e.g., /home/parcoadmin/PARCO_RTLS_VM).
---

## 3. Systemd Services for Auto-Start
- **`parco_backend.service`**: Runs FastAPI on port `8000`
- **`parco_frontend.service`**: Runs React on port `3000`
- Configured automatically by `setup.sh` for native deployment.

---

## 4. Managing the System

### Native Deployment:
- **Check status:**  
  ```bash
  sudo systemctl status parco_backend.service
  ```
- **Restart service:**  
  ```bash
  sudo systemctl restart parco_backend.service
  ```
- **Shutdown system:**  
  ```bash
  sudo /home/parcoadmin/PARCO_RTLS_VM/parco_fastapi/Linux/scripts/shutdown.sh
  ```

### Docker Deployment:
- **Stop services:**  
  ```bash
  docker-compose down
  ```
- **Start services:**  
  ```bash
  docker-compose up -d
  ```

---

## 5. GitHub Setup for Development

### Clone Repository:
```bash
git clone https://github.com/scocoh/IPS-RTLS-UWB.git
cd PARCO_RTLS_VM
```

### Commit and Push Changes:
```bash
git add .
git commit -m "Your message"
git push origin main
```

---

## 6. Full Source Code for Configuration Files
- **Configuration files:** `parco_fastapi/Linux/app/config.py`
- **Scripts:** `parco_fastapi/Linux/scripts/`
- **Docker files:** `docker/`
- **Database backup:** `parco_fastapi/Linux/db/PostgresQL_ALLDBs_backup.sql`

---

## 7. Instructions to Add to Visual Studio Code
1. Open **Visual Studio Code** on your development workstation.
2. Navigate to the directory:
   - Click `File` > `Open Folder` > `/home/parcoadmin/github_upload/`
   - If connected via **Remote SSH**, you should see `/home/parcoadmin/github_upload/` in the **File Explorer**.
3. Create a new file:
   - Right-click in **File Explorer** > `New File`
   - Name it **ParcoRTLS_Manual.md**
4. Copy the formatted content above.
5. Paste it into **ParcoRTLS_Manual.md** in VS Code.
6. Save the file (`Ctrl+S` or `Cmd+S` on Mac).

---

## 8. Verification
After saving, verify the file’s presence and contents on the command line:
```bash
ls -l /home/parcoadmin/github_upload/ParcoRTLS_Manual.md
head -n 10 /home/parcoadmin/github_upload/ParcoRTLS_Manual.md
```
This should confirm the file exists and starts with the title and version.

---

### **Documentation Summary**
- **File:** `ParcoRTLS_Manual.md`
- **Location:** `/home/parcoadmin/github_upload/`
- **Version:** `0P.1B.01`
- **Purpose:** User manual for **Linux deployment**, including installation and management instructions.


# VERSION 250317 /home/parcoadmin/parco_fastapi/app/ParcoRTLS_Manual.md 0P.1B.01
#  
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
# This information must be included in the remarks to be able use under the AGPL-3.0 license.
# Available in VB.NET & IIS and Linux
# More information available at https://asproj.com/github-rtls
