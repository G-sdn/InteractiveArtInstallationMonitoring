# Interactive Installation - Data Points Documentation

This document provides a comprehensive overview of all data points collected by the Interactive Forest Art Installation simulator.

## Overview

The system monitors **189+ artistic data points every 30 seconds** plus **39+ system metrics every 30 seconds** across multiple categories:

### Artistic Data (installations bucket)
- Environmental sensors (weather monitoring)
- Tree biometric sensors (strain gauges, accelerometers)
- Visitor detection sensors (TF-Mini LiDAR)
- Audio system monitoring (Dante network speakers)
- Lighting system monitoring (LED fixtures)

### System Metrics (system_metrics bucket)
- Zone Hub system monitoring (3 microcontrollers)
- Control PC system monitoring (Windows + creative software)
- Network and infrastructure monitoring

## Data Categories

### 1. Environmental Data (EnvironmentalReading)
**Purpose**: Weather and environmental conditions monitoring across zones  
**Frequency**: 3 readings per cycle (one per zone)

| Field Name | Data Type | Units | Range/Typical Values | Description |
|------------|-----------|-------|---------------------|-------------|
| `timestamp` | str | ISO format | 2025-09-16T14:30:00... | Measurement timestamp in ISO format |
| `zone` | str | - | entrance_clearing, deep_forest, riverside | Zone identifier within the installation |
| `temperature_c` | float | °C | 5-30°C | Air temperature with micro-climate variations |
| `humidity_percent` | float | % | 20-95% | Relative humidity percentage |

### 2. Tree Biometrics Data (TreeBiometrics)
**Purpose**: Physical strain and movement monitoring using strain gauges and accelerometers  
**Frequency**: 9 readings per cycle (9 total trees across zones)

| Field Name | Data Type | Units | Range/Typical Values | Description |
|------------|-----------|-------|---------------------|-------------|
| `timestamp` | str | ISO format | 2025-09-16T14:30:00... | Measurement timestamp |
| `tree_id` | str | - | {zone}_tree_{01-15} | Unique tree identifier |
| `strain_x_mm` | float | mm | -2.0 to +2.0 | Horizontal strain measurement (X-axis) |
| `strain_y_mm` | float | mm | -1.5 to +1.5 | Horizontal strain measurement (Y-axis) |

### 3. Visitor Detection Data (VisitorDetection)
**Purpose**: Human presence detection using TF-Mini LiDAR sensors  
**Frequency**: 15 readings per cycle (15 LiDAR sensors across zones)

| Field Name | Data Type | Units | Range/Typical Values | Description |
|------------|-----------|-------|---------------------|-------------|
| `timestamp` | str | ISO format | 2025-09-16T14:30:00... | Measurement timestamp |
| `sensor_id` | str | - | {zone}_lidar_{01-05} | LiDAR sensor identifier |
| `zone` | str | - | entrance_clearing, deep_forest, riverside | Zone location |
| `signal_strength` | float | % | 15-100% | LiDAR signal strength |
| `confidence_level` | float | % | 10-95% | Detection confidence percentage |
| `detection_active` | bool | - | true/false | Active detection status |
| `visitor_count_estimate` | int | people | 0-3 | Estimated number of visitors per sensor |

**Detection Patterns**:
- **Engaged visitors**: 500-2500mm distance (high interaction)
- **Passing visitors**: 2500-6000mm distance (transit)
- **Background noise**: 7500-8000mm distance (no detection)

### 4. Audio System Data (AudioSystem - Minimal)
**Purpose**: Basic audio monitoring for installation response  
**Frequency**: 9 readings per cycle (3 speakers per zone, 1 per zone)
**Assumption**: Single speaker/indicator per zone

| Field Name | Data Type | Units | Range/Typical Values | Description |
|------------|-----------|-------|---------------------|-------------|
| `timestamp` | str | ISO format | 2025-09-16T14:30:00... | Measurement timestamp |
| `speaker_id` | str | - | {zone}_speaker_main | Main speaker identifier per zone |
| `zone` | str | - | entrance_clearing, deep_forest, riverside | Zone location |
| `volume_db` | float | dB | 0-80 dB | Audio output volume level |

### 5. Lighting System Data (LightingSystem - Minimal)
**Purpose**: Basic LED status monitoring for visual indication  
**Frequency**: 9 readings per cycle (3 LED indicators per zone, 1 per zone)
**Assumption**: Single RGB LED indicator per zone

| Field Name | Data Type | Units | Range/Typical Values | Description |
|------------|-----------|-------|---------------------|-------------|
| `timestamp` | str | ISO format | 2025-09-16T14:30:00... | Measurement timestamp |
| `led_id` | str | - | {zone}_led_main | Main LED identifier per zone |
| `zone` | str | - | entrance_clearing, deep_forest, riverside | Zone location |
| `red_intensity` | int | 8-bit | 0-255 | Red color channel intensity |
| `green_intensity` | int | 8-bit | 0-255 | Green color channel intensity |
| `blue_intensity` | int | 8-bit | 0-255 | Blue color channel intensity |

### 6. System Metadata
**Purpose**: Simulation session information and real-time statistics  
**Frequency**: 1 per cycle (global statistics)

| Field Name | Data Type | Units | Range/Typical Values | Description |
|------------|-----------|-------|---------------------|-------------|
| `timestamp` | str | ISO format | 2025-09-16T14:30:00... | Dataset generation timestamp |
| `simulation_time` | str | datetime | 2025-09-16 14:30:00+00:00 | Current simulation time |
| `weather_pattern` | str | - | stable, variable, stormy | Session weather pattern type |
| `stats.total_visitors_detected` | int | people | 0-45 | Total visitors across all sensors |
| `stats.active_audio_channels` | int | channels | 0-50 | Number of active audio channels |
| `stats.total_power_consumption` | float | W | 500-2500 W | Total system power consumption |
| `stats.average_tree_movement` | float | ratio | 0.0-1.0 | Average tree movement intensity |
| `user_engagement[].zone` | str | - | entrance_clearing, deep_forest, riverside | Zone identifier for engagement metrics |
| `user_engagement[].average_engagement_duration_sec` | float | seconds | 5-300 | Average time visitors spend in detection range |
| `user_engagement[].engagement_score` | float | ratio | 0.0-1.0 | Calculated engagement level (duration-based) |



## System Metrics Data (system_metrics bucket)

### 8. Zone Microcontroller System Metrics
**Purpose**: Basic system health monitoring for 3 microcontrollers (ESP32/Arduino)  
**Frequency**: 9 readings per cycle (3 metrics × 3 microcontrollers)  
**Collection Method**: Simple HTTP endpoints or serial monitoring

| Field Name | Data Type | Units | Range/Typical Values | Description |
|------------|-----------|-------|---------------------|-------------|
| `timestamp` | str | ISO format | 2025-09-16T14:30:00... | Measurement timestamp |
| `device_id` | str | - | mcu-entrance, mcu-forest, mcu-riverside | Microcontroller identifier |
| `cpu_usage_percent` | float | % | 10-90% | CPU utilization percentage |
| `memory_usage_percent` | float | % | 20-80% | RAM utilization percentage |
| `system_temperature_c` | float | °C | 25-75°C | Microcontroller temperature |

### 9. Control PC System Metrics  
**Purpose**: Windows PC system monitoring (main control station)  
**Frequency**: ~8 readings per cycle  
**Collection Method**: Telegraf agent

| Field Name | Data Type | Units | Range/Typical Values | Description |
|------------|-----------|-------|---------------------|-------------|
| `timestamp` | str | ISO format | 2025-09-16T14:30:00... | Measurement timestamp |
| `host` | str | - | control-pc-windows | Control PC identifier |
| `cpu_usage_percent` | float | % | 10-90% | CPU utilization percentage |
| `memory_usage_percent` | float | % | 40-85% | RAM utilization percentage |
| `disk_usage_percent` | float | % | 25-80% | Storage utilization percentage |
| `gpu_usage_percent` | float | % | 0-95% | GPU utilization (creative software) |
| `gpu_temperature_c` | float | °C | 25-80°C | Graphics card temperature |
| `uptime_seconds` | int | seconds | 0-604800 | System uptime |

### 10. Network & Power Infrastructure Metrics
**Purpose**: Combined network health and power infrastructure monitoring  
**Frequency**: 5 readings per cycle (essential metrics only)  
**Collection Method**: SNMP polling, smart PDU monitoring

| Field Name | Data Type | Units | Range/Typical Values | Description |
|------------|-----------|-------|---------------------|-------------|
| `timestamp` | str | ISO format | 2025-09-16T14:30:00... | Measurement timestamp |
| `network_latency_ms` | float | ms | 0.5-100 | Network latency to InfluxDB |
| `packet_loss_percent` | float | % | 0-5% | Network packet loss percentage |
| `connected_devices` | int | - | 5-60 | Number of connected devices |
| `total_power_consumption_w` | float | W | 100-3000 | Total installation power consumption |
| `ups_battery_percent` | float | % | 50-100% | UPS battery level |

## Zone Configuration

The installation operates across 3 distinct zones with different characteristics:

| Zone | Trees | LiDAR Sensors | Audio/LED | Environment |
|------|-------|---------------|-----------|-------------|
| **entrance_clearing** | 3 | 5 | 1 each | Open, welcoming area |
| **deep_forest** | 3 | 5 | 1 each | Dense, mysterious forest |
| **riverside** | 3 | 5 | 1 each | Water environment, flowing sounds |

## Data Relationships

### Environmental Influences
- **Temperature** influences equipment thermal behavior and tree movement patterns
- **Humidity** affects sensor performance and visitor comfort levels

### Tree Physics
- **Tree strain (X/Y axes)** directly indicates movement intensity
- **Strain measurements** drive audio volume levels and RGB color intensity
- **Movement patterns** create realistic oscillation data for artistic response

### Visitor Engagement
- **LiDAR signal strength & confidence** determine detection quality
- **Visitor count estimates** drive audio volume amplification
- **Engagement duration** calculated from sensor activation patterns
- **Engagement score** influences lighting brightness and color saturation

### Artistic Responses (Simplified)
- **Tree movement intensity** (from strain) drives **audio volume** (simple correlation)
- **Visitor presence** amplifies **audio volume** and increases **LED brightness**
- **Zone characteristics** influence **RGB color schemes**:
  - **Entrance**: Warm colors (higher red/yellow)
  - **Forest**: Green/earth tones (higher green)
  - **Riverside**: Cool colors (higher blue/cyan)
- **Engagement score** modulates **RGB intensity** (higher engagement = brighter colors)

### System Performance
- **Microcontroller temperature** affects sensor reliability and processing
- **CPU/Memory usage** on control PC impacts creative software performance
- **Network metrics** affect data transmission reliability to InfluxDB
- **Power consumption** correlates with LED brightness and audio volume levels

## Data Volume Summary

### Artistic Data (installations bucket)
- **Environmental**: 4 fields × 3 zones = 12 points
- **Tree Biometrics**: 4 fields × 9 trees = 36 points
- **Visitor Detection**: 7 fields × 15 sensors = 105 points
- **Audio System**: 4 fields × 3 zones = 12 points
- **Lighting System**: 6 fields × 3 zones = 18 points
- **System Metadata**: 7 global stats + 9 user engagement points = 16 points
- **Artistic measurements per cycle**: **199 data points**
- **Daily artistic data volume**: ~688,320 points at standard intervals

### System Metrics (system_metrics bucket)  
- **Zone Microcontrollers**: 3 fields × 3 devices = 9 points
- **Control PC metrics**: 6 points
- **Network & Power Infrastructure**: 5 points
- **System measurements per cycle**: **20 data points**
- **Daily system metrics volume**: ~69,120 points at standard intervals

### Combined Data Volume
- **Total measurements per cycle**: **219 data points**
- **Data frequency**: Every 30 seconds (configurable)
- **Combined daily data volume**: **~757,440 points at standard intervals**
- **Storage format**: InfluxDB time-series with separate buckets
- **Backup frequency**: Every 20 iterations in real-time mode
- **Estimated storage**: ~30-60MB per day (uncompressed JSON)

## Time-Based Behavior Patterns

### Hourly Patterns
- **9-18h**: Peak visitor hours (high activity)
- **19-22h**: Evening events (moderate activity, enhanced lighting)
- **23-8h**: Night mode (minimal activity, security lighting)

### Weather Impact
- **Stable weather**: Consistent visitor flow, predictable tree movement
- **Variable weather**: Fluctuating conditions, moderate activity changes
- **Stormy weather**: Reduced visitors (20% normal), increased tree movement

### Seasonal Considerations
- **Temperature cycles**: Day/night variations using sine wave patterns
- **Light cycles**: Sunrise/sunset timing affects lighting intensity
- **Weather patterns**: Storm probability varies by pattern type