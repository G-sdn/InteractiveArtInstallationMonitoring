# Interactive Forest Art Installation

A real-time monitoring system for an interactive forest art installation that combines physical sensors, data visualization, and responsive audio/lighting experiences.

## Quick Start

```bash
# Start the complete monitoring system
./start_monitoring.sh

# Or run components individually:
python installation_sim.py --demo                    # Simulator with visual dashboard
python influx_bridge.py --simulator-api --interval 30  # Real-time data bridge
telegraf --config telegraf.conf                     # System metrics collection
```

## System Overview

This system simulates and monitors a forest installation with:
- **3 zones**: entrance_clearing, deep_forest, riverside
- **27 trees** with strain gauge sensors
- **15 visitor detection sensors** (LiDAR)
- **Audio/lighting systems** LED fixtures and speakers with light and audio responsive to environmental data
- **Real-time InfluxDB monitoring** with ~204k daily data points

## Architecture

```
[Sensors + A/V devices] → [Zone Hubs] → [Control PC + Telegraf] → Server w/ InfluxDB → Grafana
                               ↓                    |                      ↓              |
                    (RPi/microcontrollers)          |               (Ubuntu/Docker)       |
                                                    ↓                                     ↓
                              (Windows w/ installation control software)      (Data viz/Monitoring/Alerts)
```

## Data Output

- **Installation data**: Environmental sensors, tree biometrics, visitor detection, audio/lighting
- **System metrics**: CPU/memory usage, network performance, power consumption
- **Cloud storage**: InfluxDB instance at `https://influx.g-sdn.com`

## Development

Built with Python 3.10, requires `influxdb-client`, `numpy`, and `watchdog`. See documentation links below for comprehensive setup and development guidance.

## Documentation

- [**System Overview**](CLAUDE.md) - Complete project guide with architecture and commands
- [**Detailed Documentation**](docs/DOCUMENTATION.md) - In-depth technical documentation and deployment guide
- [**API Reference**](docs/API_REFERENCE.md) - Complete API documentation with examples
- [**Testing Procedures**](docs/TESTING.md) - Comprehensive testing guide and validation procedures
- [**Data Structure**](docs/data_structure.md) - Detailed data point documentation
- [**Configuration Files**](code/) - Telegraf, Grafana, and startup scripts