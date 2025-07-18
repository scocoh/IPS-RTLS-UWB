# AllTraq DataSource Module

Self-contained module for integrating AllTraq App API with ParcoRTLS Dashboard.

## Directory Structure

```
AllTraqAppAPI/
├── config/
│   └── alltraq.conf          # Configuration file
├── logs/
│   └── alltraq_service.log   # Service logs
├── scripts/
│   ├── install.sh            # Installation script
│   ├── start.sh              # Start service
│   ├── stop.sh               # Stop service
│   └── status.sh             # Check status
├── docs/
│   └── API_Reference.md      # AllTraq API documentation
├── alltraq_service.py        # Main service
├── alltraq_connector.py      # API connector class
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Quick Start

1. **Install**: `./scripts/install.sh`
2. **Configure**: Edit `config/alltraq.conf`
3. **Start**: `./scripts/start.sh`
4. **Monitor**: `./scripts/status.sh`

## Configuration

Edit `config/alltraq.conf`:
- Set your AllTraq bearer token
- Configure tag serial numbers
- Adjust polling interval

## Integration

The service connects to ParcoRTLS Dashboard Manager via WebSocket and appears as "AllTraq Tags" category in the dashboard.

## Logs

Service logs are written to `logs/alltraq_service.log` with automatic rotation.

## Management

- Start: `./scripts/start.sh`
- Stop: `./scripts/stop.sh`  
- Status: `./scripts/status.sh`
- Logs: `tail -f logs/alltraq_service.log`

## Removal

To completely remove AllTraq integration:
1. `./scripts/stop.sh`
2. `rm -rf /home/parcoadmin/parco_fastapi/app/DataSources/AllTraqAppAPI`

No core ParcoRTLS files are modified.

Trademark notice: AllTraq is a registered trademark of ABG Tag and Traq Inc (Oklahoma) Serial Num 87037989 for Goods & Service IC 009