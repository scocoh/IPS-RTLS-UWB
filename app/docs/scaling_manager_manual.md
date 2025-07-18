# ParcoRTLS Conductor Scaling Management - User Manual

**Version:** 1.0  
**Last Updated:** July 16, 2025  
**System:** Conductor Systems Thread 3 Manual Scaling  
**Port Range:** 8200-8299  

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Getting Started](#getting-started)
3. [Interface Guide](#interface-guide)
4. [Port Management](#port-management)
5. [Scaling Operations](#scaling-operations)
6. [Monitoring & Health](#monitoring--health)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## 🎯 System Overview

The **Conductor Scaling Management** system provides real-time monitoring and manual scaling capabilities for ParcoRTLS WebSocket managers. It enables administrators to:

- Monitor port health and activity in real-time
- Create scaling ports dynamically (8200-8299 range)
- Manage port configurations through database integration
- Track scaling operations and port performance

### Key Components

- **Frontend UI:** React-based dashboard at `http://192.168.210.226:3000`
- **Backend API:** FastAPI server at `http://192.168.210.226:8000`
- **Database:** PostgreSQL ParcoRTLSMaint with `tlkresources` table
- **Port Range:** 8200-8299 for RealTimeManager scaling

---

## 🚀 Getting Started

### Prerequisites

1. **FastAPI Server Running:** Port 8000
2. **React Frontend Running:** Port 3000  
3. **Database Access:** ParcoRTLSMaint with proper credentials
4. **Network Access:** Between frontend (192.168.210.248) and backend (192.168.210.226)

### Quick Start

1. **Access the Interface:**
   ```
   http://192.168.210.226:3000
   ```

2. **Navigate to Scaling Management:**
   - Click on the **Conductor Scaling Management** tab
   - You'll see 5 main tabs: Scaling Status, Port Health, Manual Scaling, Port Monitoring, Real-Time Display

3. **Check System Status:**
   - **Green "Real-Time" badge:** System connected
   - **Yellow "Health" badge:** Health monitoring active
   - **Blue "Refresh" button:** Manual refresh capability

---

## 🖥️ Interface Guide

### Main Dashboard

#### Status Indicators
- **🟢 Real-Time:** Backend API connected
- **🟡 Health:** Port health monitoring active  
- **🔄 Refresh:** Manual data refresh

#### Navigation Tabs

| Tab | Purpose | Key Features |
|-----|---------|--------------|
| **📊 Scaling Status** | Overview of scaling operations | Candidates, available ports, active instances |
| **💚 Port Health** | Real-time port monitoring | Health status, response times, failure tracking |
| **⚡ Manual Scaling** | Create/remove scaling ports | Port creation, deletion, configuration |
| **👁️ Port Monitoring** | Configuration management | Monitor settings, thresholds, intervals |
| **📺 Real-Time Display** | Live activity feed | Real-time logs, operations, updates |

### Real-Time Port Monitoring Section

#### Metrics Display
- **Total Ports:** Currently monitored ports
- **Active Now:** Ports currently active  
- **Healthy:** Ports responding normally
- **Avg Response:** Average response time

#### Filter Options
- **Display Mode:** Grid View, List View
- **Filter Status:** All Ports, Active Only, Healthy Only
- **Sort By:** Port Number, Response Time, Status

#### Live Activity Log
Real-time feed showing:
- Scaling port creation/deletion
- Port monitoring threshold updates
- Health status changes
- System operations

---

## 🔧 Port Management

### Understanding Port Types

#### Base Ports (Cannot be scaled)
- **8001:** ControlManager
- **8002:** RealTimeManager ⭐ (Primary scaling target)
- **8003:** HistoricalManager  
- **8004:** AveragedManager
- **8005-8008:** Other managers

#### Scaling Ports (Dynamic)
- **8200-8299:** Available for RealTimeManager scaling
- **Automatically configured** based on port 8002 template
- **Inherits monitoring settings** from base port

#### Inbound Ports (Monitoring only)
- **18000+:** Message filters, APIs, stream processors

### Port Configuration

Each port has these key properties:

| Property | Description | Example |
|----------|-------------|---------|
| `i_prt` | Port number | 8200 |
| `x_nm_res` | Resource name | RealTimeManager_Scale_8200 |
| `i_typ_res` | Resource type | 1 (RealTime) |
| `f_monitor_enabled` | Health monitoring | true/false |
| `f_auto_expand` | Auto-scaling candidate | true/false |
| `i_monitor_interval` | Check interval (seconds) | 30 |
| `i_monitor_timeout` | Timeout (seconds) | 5 |
| `i_monitor_threshold` | Failure threshold | 2 |

---

## ⚖️ Scaling Operations

### Manual Port Creation

#### Via UI (Recommended)
1. Go to **Manual Scaling** tab
2. Click **"Create New Port"**
3. Select target port (8200-8299)
4. Confirm creation
5. Monitor in **Live Activity Log**

#### Via API
```bash
# Create scaling port 8200
curl -X POST http://192.168.210.226:8000/api/components/scaling/create/8200

# Response
{
  "message": "Scaling port 8200 created successfully",
  "base_port": 8002,
  "new_port": 8200,
  "resource_name": "RealTimeManager_Scale_8200",
  "scaling_range": "8200-8299"
}
```

### Port Removal

#### Via UI
1. Go to **Manual Scaling** tab  
2. Find active scaling port
3. Click **"Remove Port"**
4. Confirm deletion

#### Via API  
```bash
# Remove scaling port 8200
curl -X DELETE http://192.168.210.226:8000/api/components/scaling/remove/8200

# Response
{
  "message": "Scaling port 8200 removed successfully",
  "removed_port": 8200,
  "resource_name": "RealTimeManager_Scale_8200"
}
```

### Finding Available Ports

#### Check Next Available
```bash
curl http://192.168.210.226:8000/api/components/scaling/next-port/8002

# Response
{
  "base_port": 8002,
  "next_available_port": 8200,
  "scaling_range": "8200-8299",
  "existing_ports": []
}
```

---

## 💊 Monitoring & Health

### Health Status Levels

| Status | Description | Action Required |
|--------|-------------|----------------|
| **🟢 Healthy** | Normal operation | None |
| **🟡 Warning** | Slow response (200-750ms) | Monitor |
| **🔴 Unhealthy** | Failed/timeout (>750ms) | Investigate |
| **⚫ Disabled** | Monitoring disabled | Configure |

### Monitoring Configuration

#### Database Settings
- **f_monitor_enabled:** Enable/disable health checks
- **i_monitor_interval:** How often to check (default: 30s)
- **i_monitor_timeout:** Connection timeout (default: 5s)  
- **i_monitor_threshold:** Failures before unhealthy (default: 2)

#### Response Time Thresholds
- **< 200ms:** Excellent (Green)
- **200-750ms:** Warning (Yellow)  
- **> 750ms:** Unhealthy (Red)
- **Timeout:** Failed (Black)

### Health Check Process

1. **TCP Connection Test:** Attempt socket connection
2. **Response Time Measurement:** Track connection speed
3. **Threshold Evaluation:** Compare against configured limits
4. **Status Update:** Update database and UI
5. **Alert Generation:** Log significant changes

---

## 🔗 API Reference

### Core Endpoints

#### Scaling Management
```bash
# Get scaling status overview
GET /api/components/scaling/status

# Get scaling candidates (auto_expand=true)
GET /api/components/scaling-candidates

# Create scaling port (simple)
POST /api/components/scaling/create/{port}

# Remove scaling port  
DELETE /api/components/scaling/remove/{port}

# Get next available port
GET /api/components/scaling/next-port/{base_port}
```

#### Port Health
```bash
# Get port health status
GET /api/components/port-health

# Get unhealthy ports
GET /api/components/unhealthy-ports

# Refresh monitoring config
POST /api/components/port-health/refresh
```

#### Port Monitoring
```bash
# Get all port configurations
GET /api/components/port-monitoring

# Get specific port details
GET /api/components/port-monitoring/{port}

# Update port configuration
PUT /api/components/port-monitoring/{port}
```

#### System Information
```bash
# Get scaling menu/operations
GET /api/components/menu/scaling

# Get component versions
GET /api/components/
```

### Response Formats

#### Scaling Status Response
```json
{
  "port_health": {
    "status": "database_only",
    "total_ports": 17,
    "monitored_ports": 3,
    "auto_expand_ports": 8
  },
  "scaling_candidates": [8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008],
  "available_scaling_ports": [8200, 8201, 8202, ...],
  "active_scaling_ports": [],
  "scaling_status": {
    "total_scaling_candidates": 8,
    "available_slots": 100,
    "active_scaling_instances": 0,
    "mode": "database_only"
  }
}
```

#### Port Health Response
```json
{
  "status": "database_only",
  "total_monitored_ports": 3,
  "healthy_ports": 3,
  "unhealthy_ports": 0,
  "port_health_stats": {
    "8001": {
      "resource_name": "ControlManager",
      "is_healthy": true,
      "monitor_enabled": true,
      "status": "database_config_only"
    }
  }
}
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. "No ports match current filter"
**Cause:** Filter settings exclude all ports  
**Solution:** 
- Change **Filter Status** to "All Ports"
- Verify ports exist in database
- Check monitoring configuration

#### 2. "500 Internal Server Error"  
**Cause:** Database connection or API issues
**Solution:**
- Check FastAPI server logs
- Verify database credentials in `config.py`
- Restart backend server: `uvicorn app:app --host 0.0.0.0 --port 8000 --reload`

#### 3. "Port already exists" (409 error)
**Cause:** Attempting to create existing port
**Solution:**
- Check active scaling ports first
- Use `/scaling/next-port/8002` to find available ports
- Remove existing port before recreating

#### 4. Frontend shows "0 ports" everywhere
**Cause:** API connectivity issues
**Solution:**
- Verify backend server running on port 8000
- Check network connectivity: `curl http://192.168.210.226:8000/api/components/port-monitoring`
- Check browser console for CORS errors

#### 5. "Database error" messages
**Cause:** Database configuration or permissions
**Solution:**
- Verify PostgreSQL running
- Check `tlkresources` table exists
- Verify `parcoadmin` user permissions
- Check `db_config_helper.py` settings

### Diagnostic Commands

#### Backend Health Check
```bash
# Test basic API connectivity
curl http://192.168.210.226:8000/api/components/

# Test database integration  
curl http://192.168.210.226:8000/api/components/port-monitoring

# Test scaling functionality
curl http://192.168.210.226:8000/api/components/scaling/status
```

#### Database Verification
```bash
# Connect to database
psql -U parcoadmin -h 192.168.210.226 -d ParcoRTLSMaint

# Check tlkresources table
SELECT COUNT(*) FROM tlkresources WHERE i_prt > 0;

# Check scaling candidates
SELECT i_prt, x_nm_res, f_auto_expand FROM tlkresources WHERE f_auto_expand = true;

# Check monitoring configuration
SELECT i_prt, x_nm_res, f_monitor_enabled FROM tlkresources WHERE i_prt > 0;
```

#### Log Analysis
```bash
# FastAPI server logs
tail -f /var/log/fastapi.log

# Check for specific errors
grep "ERROR" /var/log/fastapi.log | tail -20

# Monitor API requests
grep "GET\|POST\|DELETE" /var/log/fastapi.log | tail -20
```

---

## ✅ Best Practices

### Scaling Management

#### Planning
- **Monitor before scaling:** Check port health before creating new instances
- **Use next-available:** Always use `/scaling/next-port/8002` to find available ports
- **Document changes:** Record scaling operations in change management
- **Test incrementally:** Create one scaling port at a time

#### Port Creation
- **Validate need:** Ensure scaling is actually required
- **Check resources:** Verify system resources can handle additional ports
- **Monitor immediately:** Watch new ports in real-time monitoring
- **Have rollback plan:** Know how to remove ports if issues arise

#### Port Removal
- **Graceful shutdown:** Stop services before removing ports
- **Verify no connections:** Ensure no active clients before deletion
- **Remove in reverse order:** Remove highest port numbers first
- **Update documentation:** Record removal in system documentation

### Monitoring Configuration

#### Health Check Settings
- **Appropriate intervals:** 30s for most cases, 10s for critical ports
- **Reasonable timeouts:** 5s default, 10s for slow networks
- **Sensible thresholds:** 2-3 failures before marking unhealthy
- **Enable selectively:** Only monitor ports that need it

#### Performance Optimization  
- **Limit concurrent checks:** Avoid overloading network
- **Adjust thresholds:** Tune based on actual network performance
- **Use database-only mode:** For initial setup and testing
- **Regular maintenance:** Clean up old monitoring data

### Database Management

#### Configuration Updates
- **Use transactions:** Wrap multiple changes in database transactions
- **Backup before changes:** Always backup before major configuration changes
- **Test in staging:** Validate changes in test environment first
- **Monitor after changes:** Watch for issues after configuration updates

#### Performance
- **Index monitoring:** Ensure proper indexes on `i_prt` column
- **Clean up old data:** Archive old monitoring data regularly
- **Monitor connections:** Watch database connection usage
- **Regular maintenance:** Run VACUUM and ANALYZE regularly

### Security Considerations

#### Access Control
- **Limit API access:** Restrict access to scaling APIs
- **Use authentication:** Implement proper authentication for production
- **Log operations:** Keep audit trail of all scaling operations
- **Network security:** Use VPN or secure networks for management

#### Data Protection
- **Secure credentials:** Store database credentials securely
- **Encrypt connections:** Use SSL for database connections
- **Regular backups:** Backup configuration data regularly
- **Access logging:** Log all configuration changes

---

## 📚 Additional Resources

### Configuration Files
- **components.py:** `/home/parcoadmin/parco_fastapi/app/routes/components.py`
- **config.py:** `/home/parcoadmin/parco_fastapi/app/config.py`
- **db_config_helper.py:** `/home/parcoadmin/parco_fastapi/app/db_config_helper.py`

### Database Schema
- **Main table:** `ParcoRTLSMaint.tlkresources`
- **Key columns:** `i_prt`, `x_nm_res`, `f_monitor_enabled`, `f_auto_expand`
- **Monitoring columns:** `i_monitor_*` settings

### Network Configuration
- **Backend:** 192.168.210.226:8000
- **Frontend:** 192.168.210.226:3000 (accessed from 192.168.210.248)
- **Database:** 192.168.210.226:5432
- **Scaling Range:** 8200-8299

### Support Information
- **Version:** components.py v0.1.9
- **Last Update:** July 16, 2025
- **System:** ParcoRTLS Conductor Thread 3
- **Contact:** ParcoAdmin

---

**End of Manual** | *For technical support, check system logs and API responses first*