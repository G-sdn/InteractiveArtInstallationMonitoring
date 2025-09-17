# Interactive Forest Art Installation - Detailed Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Data Models](#data-models)
6. [Monitoring & Metrics](#monitoring--metrics)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

## Project Overview

### Purpose
The Interactive Forest Art Installation is a real-time monitoring system that combines physical sensors, data visualization, and responsive audio/lighting experiences in a forest environment. The system monitors environmental conditions, visitor interactions, and tree biometrics to create an immersive artistic experience.

### Key Features
- **Real-time data collection** from 100+ sensors across 3 forest zones
- **Responsive audio/lighting** that reacts to environmental changes and visitor presence
- **Time-series data storage** with InfluxDB for historical analysis
- **Live monitoring dashboards** with Grafana visualization
- **Predictive maintenance** capabilities for installation hardware

### Target Audience
- IoT developers and engineers
- DevOps professionals working with time-series data
- Art technologists and interactive installation creators
- System administrators managing distributed sensor networks

## System Architecture

### Physical Deployment
```
Forest Installation Layout:
┌─────────────────┬─────────────────┬─────────────────┐
│  ENTRANCE       │  DEEP FOREST    │  RIVERSIDE      │
│  CLEARING       │                 │                 │
├─────────────────┼─────────────────┼─────────────────┤
│ 9 trees         │ 9 trees         │ 9 trees         │
│ 5 LiDAR sensors │ 5 LiDAR sensors │ 5 LiDAR sensors │
│ 1 audio speaker │ 1 audio speaker │ 1 audio speaker │
│ 1 LED fixture   │ 1 LED fixture   │ 1 LED fixture   │
│ Weather station │ Weather station │ Weather station │
└─────────────────┴─────────────────┴─────────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    Zone Hub Network
                           │
                     Control Center
                           │
                    InfluxDB Cloud
```

### Data Flow Architecture
```
Sensors -> Zone Hubs -> Control PC -> InfluxDB -> Grafana
  (IoT)      (Pi)      (Telegraf)   (Cloud)    (Dashboards)
```

### Component Responsibilities

**Zone Hubs (Raspberry Pi)**
- Collect data from local sensors
- Pre-process and validate sensor readings
- Forward data via WiFi to control center
- Manage local audio/lighting responses

**Control PC (Windows/Linux)**
- Aggregates data from all zones
- Runs Telegraf for system metrics collection
- Hosts TouchDesigner/Max for real-time audio processing
- Manages overall installation state

**InfluxDB Cloud**
- Stores time-series data from all sources
- Provides high-availability data storage
- Enables real-time and historical queries
- Supports data retention policies

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git for version control
- InfluxDB Cloud account (or local Docker instance)
- Network connectivity for all zone hubs

### Environment Setup
```bash
# Clone repository
git clone [repository-url]
cd InteractiveArtInstallation

# Create and activate virtual environment
python -m venv .
source bin/activate  # Linux/Mac
# or
Scripts\activate     # Windows

# Install dependencies
pip install influxdb-client numpy watchdog
```

### Configuration Files
Create and configure the following files:

**InfluxDB Configuration**
```python
# influxdb/config.py
INFLUX_URL = "https://your-influx-instance.com"
INFLUX_TOKEN = "your-api-token"
INFLUX_ORG = "your-organization"
BUCKETS = {
    "installations": "artistic_data",
    "system_metrics": "system_health"
}
```

**Telegraf Configuration**
```toml
# telegraf.conf
[global_tags]
  installation = "forest_interactive"
  location = "primary_site"

[[outputs.influxdb_v2]]
  urls = ["https://your-influx-instance.com"]
  token = "your-api-token"
  organization = "your-organization"
  bucket = "system_metrics"
```

## Configuration

### Simulator Configuration
The installation simulator supports multiple configuration modes:

**Real-time Mode (Default)**
```bash
python installation_sim.py
# Updates every 30 seconds with realistic timing
```

**Development Mode**
```bash
python installation_sim.py --interval 10 --demo
# Fast updates with exaggerated changes for testing
```

**Snapshot Mode**
```bash
python installation_sim.py --snapshot --output test_data
# Single data capture for validation
```

### Zone-Specific Settings
Each forest zone has unique characteristics:

**Entrance Clearing**
- Higher visitor traffic (peak 9-18h)
- 8 connected sensors per zone hub
- Better WiFi signal strength (-45 to -75 dBm)
- More responsive lighting due to visibility

**Deep Forest**
- Lower visitor traffic but longer stay times
- 6 connected sensors per zone hub
- Weaker WiFi signal (-65 to -85 dBm)
- More ambient audio focus

**Riverside**
- Variable visitor patterns based on weather
- 6 connected sensors per zone hub
- Good WiFi signal (-45 to -75 dBm)
- Water-themed audio and cooler lighting

## Data Models

### Primary Data Types

**Environmental Data**
```json
{
  "measurement": "environmental",
  "tags": {
    "zone": "entrance_clearing",
    "measurement_type": "weather"
  },
  "fields": {
    "temperature_c": 22.5,
    "humidity_percent": 65.2,
    "wind_speed_kmh": 8.3,
    "atmospheric_pressure_hpa": 1013.2
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Tree Biometrics**
```json
{
  "measurement": "tree_biometrics",
  "tags": {
    "tree_id": "OAK_001",
    "zone": "deep_forest",
    "species": "oak"
  },
  "fields": {
    "strain_gauge_reading": 0.0023,
    "movement_amplitude_mm": 3.2,
    "natural_frequency_hz": 0.8,
    "health_score": 0.92
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Visitor Detection**
```json
{
  "measurement": "visitor_detection",
  "tags": {
    "sensor_id": "LIDAR_ENT_001",
    "zone": "entrance_clearing"
  },
  "fields": {
    "distance_cm": 150,
    "movement_detected": true,
    "confidence_score": 0.95,
    "duration_seconds": 45
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Data Relationships
- **Environmental -> Tree Movement**: Wind affects tree strain readings
- **Tree Movement -> Audio**: Strain triggers audio volume changes
- **Visitor Presence -> Lighting**: Proximity activates zone lighting
- **Zone Activity -> Power**: Higher activity increases power consumption

## Monitoring & Metrics

### System Health Metrics
**Zone Hub Performance**
- CPU usage (10-85% range)
- Memory usage (20-80% range)
- System temperature (25-75°C)
- WiFi signal strength
- Connected sensor count
- Uptime tracking

**Network Performance**
- Packet loss percentage (0-5%)
- Latency measurements
- Connection stability
- Data transfer rates

**Power Management**
- Battery levels (50-100%)
- Power consumption (2-8W per hub)
- Charging status
- Solar panel efficiency (if applicable)

### Performance Benchmarks
**Data Volume Expectations**
- Artistic data: ~135,000 points/day
- System metrics: ~69,000 points/day
- Combined: ~204,000 points/day
- Peak rate: ~2.4 points/second

**Resource Requirements**
- RAM: Minimum 4GB, recommended 8GB
- Storage: 1GB/month for data retention
- Network: 1Mbps sustained, 5Mbps peak
- CPU: Dual-core minimum for real-time processing

## Deployment

### Production Deployment Checklist

**Pre-deployment**
- [ ] Test all sensor connections
- [ ] Verify InfluxDB connectivity
- [ ] Validate Telegraf configuration
- [ ] Check network connectivity at all zones
- [ ] Test audio/lighting response systems

**Deployment Steps**
1. Deploy zone hubs with sensor arrays
2. Configure network connectivity
3. Install control PC with monitoring software
4. Start data collection services
5. Verify data flow to InfluxDB
6. Configure Grafana dashboards
7. Set up alerting for critical metrics

**Post-deployment**
- [ ] Monitor system for 24 hours
- [ ] Verify data quality and completeness
- [ ] Test emergency shutdown procedures
- [ ] Document any configuration changes
- [ ] Train operators on monitoring procedures

### High Availability Setup
**Redundancy Measures**
- Dual network connections for critical zones
- Battery backup for 4-8 hours of operation
- Local data buffering during network outages
- Automatic restart procedures for failed services

**Backup Procedures**
- Daily automated backups of configuration
- Weekly full system backups
- InfluxDB data retention policies
- Off-site backup storage for critical data

## Troubleshooting

### Common Issues

**Data Not Appearing in InfluxDB**
1. Check network connectivity: `ping influx.g-sdn.com`
2. Verify API token: `python influx_test.py`
3. Check service status: `systemctl status telegraf`
4. Review logs: `tail -f logs/bridge.log`

**Zone Hub Connection Issues**
1. Check WiFi signal strength on hub
2. Verify sensor connections and power
3. Test network connectivity from hub location
4. Review hub logs for error messages

**Performance Degradation**
1. Monitor CPU and memory usage on control PC
2. Check InfluxDB write performance
3. Verify network bandwidth utilization
4. Review data volume and optimize if needed

**Audio/Lighting Not Responding**
1. Check sensor data quality and ranges
2. Verify audio/lighting controller connections
3. Test manual override procedures
4. Review correlation algorithms for proper thresholds

### Diagnostic Commands
```bash
# System status overview
./start_monitoring.sh

# Test individual components
python installation_sim.py --snapshot
python influx_bridge.py --test-connection
telegraf --config telegraf.conf --test

# Monitor logs in real-time
tail -f logs/simulator.log
tail -f logs/bridge.log
tail -f logs/telegraf.log

# Check process status
ps aux | grep -E "(python|telegraf)"
pgrep -f "installation_sim|influx_bridge|telegraf"
```

### Support Resources
- **Documentation**: Full system documentation in `CLAUDE.md`
- **API Reference**: Detailed API documentation in `API_REFERENCE.md`
- **Testing Procedures**: Comprehensive testing guide in `TESTING.md`
- **Community**: Project GitHub repository for issues and discussions