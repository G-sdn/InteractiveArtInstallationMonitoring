# API Reference - Interactive Forest Art Installation

## Table of Contents
1. [Overview](#overview)
2. [Installation Simulator API](#installation-simulator-api)
3. [InfluxDB Bridge API](#influxdb-bridge-api)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Usage Examples](#usage-examples)

## Overview

The Interactive Forest Art Installation provides several API interfaces for data generation, collection, and management. The system uses both internal APIs for component communication and external APIs for data storage and visualization.

### API Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Simulator API   │───▶│ Bridge API      │───▶│ InfluxDB API    │
│ (Data Gen)      │    │ (Processing)    │    │ (Storage)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Authentication
- **InfluxDB**: Token-based authentication
- **Internal APIs**: No authentication required (internal network)
- **Simulator**: Direct Python function calls

## Installation Simulator API

### Core Classes

#### `InstallationSimulator`
Main simulator class that generates realistic forest installation data.

```python
class InstallationSimulator:
    def __init__(self)
    def generate_single_dataset(self) -> Dict
    def get_stats(self) -> Dict
```

**Parameters:**
- None required

**Methods:**

##### `generate_single_dataset()`
Generates a complete dataset for all installation components.

**Returns:**
```python
{
    "timestamp": "2025-01-15T10:30:00Z",
    "environmental": [
        {
            "zone": "entrance_clearing",
            "temperature_c": 22.5,
            "humidity_percent": 65.2,
            "wind_speed_kmh": 8.3,
            "atmospheric_pressure_hpa": 1013.2,
            "timestamp": "2025-01-15T10:30:00Z"
        },
        # ... additional zones
    ],
    "tree_biometrics": [...],
    "visitor_detection": [...],
    "audio_system": [...],
    "lighting_system": [...],
    "metadata": {...}
}
```

##### `get_stats()`
Returns current simulation statistics.

**Returns:**
```python
{
    "total_visitors_today": 45,
    "average_zone_activity": 0.67,
    "system_uptime_hours": 12.5,
    "data_points_generated": 15420
}
```

### Command Line Interface

#### Basic Usage
```bash
# Real-time simulation (default)
python installation_sim.py

# Custom interval
python installation_sim.py --interval 10

# Demo mode with exaggerated changes
python installation_sim.py --demo --interval 5

# Single snapshot
python installation_sim.py --snapshot --output test_data

# Generate snapshot
python installation_sim.py --snapshot
```

#### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--interval` | int | 30 | Update interval in seconds |
| `--demo` | flag | False | Enable demo mode with exaggerated changes |
| `--snapshot` | flag | False | Generate single dataset and exit |
| `--output` | str | "forest_data" | Output file prefix |

## InfluxDB Bridge API

### Core Classes

#### `InstallationDataBridge`
Handles data conversion and upload to InfluxDB.

```python
class InstallationDataBridge:
    def __init__(self)
    def connect_influxdb(self) -> bool
    def process_dataset(self, dataset: Dict) -> bool
    def test_connection(self) -> bool
```

**Methods:**

##### `connect_influxdb()`
Establishes connection to InfluxDB instance.

**Returns:** `bool` - Connection success status

**Example:**
```python
bridge = InstallationDataBridge()
if bridge.connect_influxdb():
    print("Connected successfully")
```

##### `process_dataset(dataset)`
Converts and uploads a complete dataset to InfluxDB.

**Parameters:**
- `dataset` (Dict): Complete dataset from simulator

**Returns:** `bool` - Upload success status

**Example:**
```python
dataset = simulator.generate_single_dataset()
success = bridge.process_dataset(dataset)
```

##### `test_connection()`
Performs read/write test on InfluxDB connection.

**Returns:** `bool` - Test success status

### Command Line Interface

#### Basic Usage
```bash
# Direct API mode (recommended)
python influx_bridge.py --simulator-api --interval 30

# File watcher mode
python influx_bridge.py --file-watcher --input forest_data

# Test connection only
python influx_bridge.py --test-connection
```

#### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--simulator-api` | flag | False | Enable direct API mode |
| `--file-watcher` | flag | False | Enable file monitoring mode |
| `--test-connection` | flag | False | Test InfluxDB connection and exit |
| `--interval` | int | 30 | Update interval for API mode |
| `--input` | str | "forest_data" | Input file prefix for file mode |

### API Mode Functions

#### `run_simulator_api_mode(bridge, interval)`
Async function for direct API data streaming.

**Parameters:**
- `bridge` (InstallationDataBridge): Configured bridge instance
- `interval` (int): Update interval in seconds

**Usage:**
```python
import asyncio

bridge = InstallationDataBridge()
if bridge.connect_influxdb():
    asyncio.run(run_simulator_api_mode(bridge, 30))
```

## Data Models

### Point Conversion Methods

#### Environmental Data
```python
def convert_environmental_to_points(environmental_data: List[Dict]) -> List[Point]
```

**Input Format:**
```python
{
    "zone": "entrance_clearing",
    "temperature_c": 22.5,
    "humidity_percent": 65.2,
    "wind_speed_kmh": 8.3,
    "atmospheric_pressure_hpa": 1013.2,
    "timestamp": "2025-01-15T10:30:00Z"
}
```

**InfluxDB Point:**
```python
Point("environmental")
    .tag("zone", "entrance_clearing")
    .tag("measurement_type", "environmental")
    .field("temperature_c", 22.5)
    .field("humidity_percent", 65.2)
    .time("2025-01-15T10:30:00Z")
```

#### Tree Biometrics
```python
def convert_tree_biometrics_to_points(tree_data: List[Dict]) -> List[Point]
```

**Input Format:**
```python
{
    "tree_id": "OAK_001",
    "zone": "deep_forest",
    "species": "oak",
    "strain_gauge_reading": 0.0023,
    "movement_amplitude_mm": 3.2,
    "natural_frequency_hz": 0.8,
    "health_score": 0.92,
    "timestamp": "2025-01-15T10:30:00Z"
}
```

#### Visitor Detection
```python
def convert_visitor_detection_to_points(visitor_data: List[Dict]) -> List[Point]
```

**Input Format:**
```python
{
    "sensor_id": "LIDAR_ENT_001",
    "zone": "entrance_clearing",
    "distance_cm": 150,
    "movement_detected": True,
    "confidence_score": 0.95,
    "duration_seconds": 45,
    "timestamp": "2025-01-15T10:30:00Z"
}
```

## Error Handling

### Connection Errors

#### InfluxDB Connection Failure
```python
try:
    bridge.connect_influxdb()
except Exception as e:
    print(f"[ERROR] InfluxDB connection failed: {e}")
    # Implement retry logic or fallback storage
```

#### Network Timeout
```python
try:
    bridge.process_dataset(dataset)
except TimeoutError:
    print("[WARNING] Upload timeout, retrying...")
    # Implement exponential backoff
```

### Data Validation Errors

#### Invalid Data Format
```python
def validate_dataset(dataset: Dict) -> bool:
    required_keys = ["timestamp", "environmental", "tree_biometrics"]
    return all(key in dataset for key in required_keys)
```

#### Missing Fields
```python
def validate_environmental_data(data: Dict) -> bool:
    required_fields = ["zone", "temperature_c", "humidity_percent"]
    return all(field in data for field in required_fields)
```

### Error Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Continue processing |
| 400 | Bad Request | Validate data format |
| 401 | Unauthorized | Check API token |
| 429 | Rate Limited | Implement backoff |
| 500 | Server Error | Retry with exponential backoff |

## Usage Examples

### Basic Simulator Usage
```python
#!/usr/bin/env python3
from simulation.installation_sim import InstallationSimulator

# Create simulator instance
simulator = InstallationSimulator()

# Generate single dataset
dataset = simulator.generate_single_dataset()

# Access specific data types
environmental = dataset["environmental"]
trees = dataset["tree_biometrics"]
visitors = dataset["visitor_detection"]

print(f"Generated data for {len(trees)} trees")
print(f"Detected {sum(1 for v in visitors if v['movement_detected'])} visitors")
```

### Bridge Integration
```python
#!/usr/bin/env python3
import asyncio
from influxdb.influx_bridge import InstallationDataBridge
from simulation.installation_sim import InstallationSimulator

async def main():
    # Initialize components
    bridge = InstallationDataBridge()
    simulator = InstallationSimulator()

    # Connect to InfluxDB
    if not bridge.connect_influxdb():
        print("[ERROR] Failed to connect to InfluxDB")
        return

    # Generate and upload data
    for i in range(10):
        dataset = simulator.generate_single_dataset()
        success = bridge.process_dataset(dataset)

        if success:
            print(f"[OK] Uploaded dataset {i+1}")
        else:
            print(f"[ERROR] Failed to upload dataset {i+1}")

        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Data Processing
```python
#!/usr/bin/env python3
from influxdb.influx_bridge import InstallationDataBridge

# Initialize bridge
bridge = InstallationDataBridge()

# Custom environmental data
custom_data = [
    {
        "zone": "test_zone",
        "temperature_c": 25.0,
        "humidity_percent": 60.0,
        "wind_speed_kmh": 5.0,
        "atmospheric_pressure_hpa": 1015.0,
        "timestamp": "2025-01-15T12:00:00Z"
    }
]

# Convert to InfluxDB points
points = bridge.convert_environmental_to_points(custom_data)

# Upload to InfluxDB
if bridge.connected:
    bridge.write_api.write(bucket=bridge.config.bucket, record=points)
    print("[OK] Custom data uploaded")
```

### Monitoring System Status
```python
#!/usr/bin/env python3
import time
from influxdb.influx_bridge import InstallationDataBridge

def monitor_system():
    bridge = InstallationDataBridge()

    while True:
        # Test connection
        if bridge.test_connection():
            print("[OK] InfluxDB connection healthy")
        else:
            print("[ERROR] InfluxDB connection failed")

        # Display statistics
        stats = bridge.stats
        print(f"[STATS] Points written: {stats['total_points_written']}")
        print(f"[STATS] Uptime: {time.time() - stats['uptime_start']:.1f}s")

        time.sleep(60)

if __name__ == "__main__":
    monitor_system()
```

### Error Handling Example
```python
#!/usr/bin/env python3
import time
from influxdb.influx_bridge import InstallationDataBridge
from simulation.installation_sim import InstallationSimulator

def robust_data_collection():
    bridge = InstallationDataBridge()
    simulator = InstallationSimulator()

    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            # Attempt connection
            if bridge.connect_influxdb():
                print("[OK] Connected to InfluxDB")
                break
            else:
                raise ConnectionError("Failed to connect")

        except Exception as e:
            retry_count += 1
            wait_time = 2 ** retry_count  # Exponential backoff
            print(f"[ERROR] Connection attempt {retry_count} failed: {e}")
            print(f"[INFO] Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    if retry_count >= max_retries:
        print("[ERROR] Max retries exceeded, exiting")
        return

    # Main data collection loop
    while True:
        try:
            dataset = simulator.generate_single_dataset()
            success = bridge.process_dataset(dataset)

            if not success:
                print("[WARNING] Upload failed, buffering data locally")
                # Implement local buffering logic here

        except KeyboardInterrupt:
            print("[INFO] Shutting down gracefully")
            bridge.disconnect()
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            time.sleep(5)  # Brief pause before continuing

if __name__ == "__main__":
    robust_data_collection()
```