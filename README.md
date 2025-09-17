# Interactive Art Installation Monitoring with InfluxDB and Grafana

An example of a real-time monitoring system for an interactive art installation that combines physical sensors, data visualization, and responsive audio/lighting experiences.

## Use cases

Data monitoring in interactive installations with InfluxDB can be useful for:

### Operational Management

- Real-time System Health:
    - Monitor equipment failures before they impact visitors (sensor failures, speaker network issues)
    - Track power consumption to prevent electrical overloads in remote locations
    - Alert staff when devices go offline or sensors produce anomalous readings

- Predictive Maintenance:
    - Historical data reveals equipment degradation patterns
    - Schedule maintenance during low-visitor periods
    - Reduce unexpected downtime that disrupts the experience
    - Track environmental wear on sensitive electronics exposed to weather
  
### Artistic Enhancement
- Data-Driven Creative Decisions:
    - Understand which environmental conditions produce the most engaging responses
    - Correlate visitor engagement with specific audio/visual combinations
    - Optimize the relationship between sensors and audiovisual realtime generated content

- Performance Optimization:
  - Identify dead zones where sensors aren't detecting visitors effectively
  - Balance audio levels for optimal sound propagation
  - Adjust sensitivity thresholds based on seasonal changes (temperature, weather patterns, etc.)

### Visitor Experience Insights
- Engagement Analytics:
  - Track dwell times in different zones to understand visitor preferences
  - Identify peak interaction periods for staffing and maintenance planning
  - Measure how weather conditions affect visitor behavior and system responsiveness
  - Document successful artistic moments for replication

- Safety and Accessibility:
  - Monitor visitor density
  - Ensure emergency systems remain functional

### Documentation and Research
- Artistic Documentation:
  - Create a permanent record of how the installation evolves
  - Build a dataset for future impact studies, installations or academic research

- Technical Knowledge Base:
  - Build expertise for scaling to other locations
  - Document what works in specific environmental conditions
  - Create templates for similar installations

### Business Value
- Operational Efficiency:
  - Reduce site visits through remote monitoring
  - Optimize energy consumption
  - Demonstrate system reliability to stakeholders and funders
  - Support insurance requirements for complex outdoor installations

- Scalability:
  - Proven monitoring architecture for multiple installations
  - Remote management capabilities for distributed sites
  - Data-driven proposals for expansion or improvements

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

This system simulates and monitors a installation with:
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

- [**Detailed Documentation**](docs/DOCUMENTATION.md) - In-depth technical documentation and deployment guide
- [**API Reference**](docs/API_REFERENCE.md) - Complete API documentation with examples
- [**Testing Procedures**](docs/TESTING.md) - Comprehensive testing guide and validation procedures
- [**Data Structure**](docs/data_structure.md) - Detailed data point documentation