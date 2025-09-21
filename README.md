# Interactive Art Installation Monitoring with InfluxDB and Grafana

An example of a real-time monitoring system for an interactive art installation that combines physical sensors, data visualization, and responsive audio/lighting experiences.

## Table of Contents
1. [Guide](#guide)
2. [Use Cases](#use-case)
3. [Quick Start](#quick-start)
4. [System Overview](#system-overview)
5. [System Architecture](#system-architecture)
6. [Installation & Setup](#installation--setup)
7. [Configuration](#configuration)
8. [Data Models](#data-models)

## Guide
You can follow the [guide](guide/GUIDE.md) in this repo for an in-depth tutorial on how to set up InfluxDB and Grafana in seconds.

## Use cases

Data monitoring in interactive installations with InfluxDB can be useful for:

<details>
    <summary>Operational Management</summary>

- Real-time System Health:
    - Monitor equipment failures before they impact visitors (sensor failures, speaker network issues)
    - Track power consumption to prevent electrical overloads in remote locations
    - Alert staff when devices go offline or sensors produce anomalous readings

- Predictive Maintenance:
    - Historical data reveals equipment degradation patterns
    - Schedule maintenance during low-visitor periods
    - Reduce unexpected downtime that disrupts the experience
    - Track environmental wear on sensitive electronics exposed to weather
</details>

<details>
    <summary>Artistic Enhancement</summary>

- Data-Driven Creative Decisions:
    - Understand which environmental conditions produce the most engaging responses
    - Correlate visitor engagement with specific audio/visual combinations
    - Optimize the relationship between sensors and audiovisual realtime generated content

- Performance Optimization:
  - Identify dead zones where sensors aren't detecting visitors effectively
  - Balance audio levels for optimal sound propagation
  - Adjust sensitivity thresholds based on seasonal changes (temperature, weather patterns, etc.)
</details>

<details>
    <summary>Visitor Experience Insights</summary>

- Engagement Analytics:
  - Track dwell times in different zones to understand visitor preferences
  - Identify peak interaction periods for staffing and maintenance planning
  - Measure how weather conditions affect visitor behavior and system responsiveness
  - Document successful artistic moments for replication

- Safety and Accessibility:
  - Monitor visitor density
  - Ensure emergency systems remain functional
</details>

<details>
    <summary>Documentation and Research</summary>

- Artistic Documentation:
  - Create a permanent record of how the installation evolves
  - Build a dataset for future impact studies, installations or academic research

- Technical Knowledge Base:
  - Build expertise for scaling to other locations
  - Document what works in specific environmental conditions
  - Create templates for similar installations
</details>

<details>
    <summary>Business Value</summary>

- Operational Efficiency:
  - Reduce site visits through remote monitoring
  - Optimize energy consumption
  - Demonstrate system reliability to stakeholders and funders
  - Support insurance requirements for complex outdoor installations

- Scalability:
  - Proven monitoring architecture for multiple installations
  - Remote management capabilities for distributed sites
  - Data-driven proposals for expansion or improvements
</details>

## Quick Start

```bash
# Start the complete monitoring system
./start_monitoring.sh

# Or run components individually:
python installation_sim.py --demo                    # Simulator with visual dashboard
python influx_bridge.py --simulator-api --interval 5  # Real-time data bridge
telegraf --config telegraf.conf                     # System metrics collection
```

## System Overview

This system simulates and monitors an installation with:
- **3 zones**: entrance_clearing, deep_forest, riverside
- **27 trees** with strain gauge sensors
- **15 visitor detection sensors** (LiDAR)
- **Audio/lighting systems** LED fixtures and speakers with light and audio responsive to environmental data
- **Real-time InfluxDB monitoring** with ~204k daily data points

## System Architecture

### Physical Deployment
```
Installation Layout:
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
                           │
                     Control PC
                           │
                    InfluxDB Server
```

### Data Flow Architecture
```
[Sensors + A/V devices] → [Zone Hubs] → [Control PC + Telegraf] → Server w/ InfluxDB → Grafana
                               ↓                    |                      ↓              |
                    (RPi/microcontrollers)          |               (Ubuntu/Docker)       |
                                                    ↓                                     ↓
                              (Windows w/ installation control software)      (Data viz/Monitoring/Alerts)
```

### Component Responsibilities

**Zone Hubs (Raspberry Pi or microcontroller)**
- Collect data from local sensors
- Pre-process and validate sensor readings
- Forward data via LAN to control center
- Manage local audio/lighting responses

**Control PC (Windows/Linux)**
- Aggregates data from all zones
- Runs Telegraf for system metrics collection
- Hosts TouchDesigner/Max or other software for real-time audio processing
- Manages overall installation state

**InfluxDB Server**
- Stores time-series data from all sources
- Provides high-availability data storage
- Enables real-time and historical queries


## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Instances of InfluxDB and Grafana (Docker recommended for testing)
- Telegraf

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

See the [data_structure.md](data_structure.md) file for detailed info on the data model.