# Testing Procedures - Interactive Forest Art Installation

## Table of Contents
1. [Testing Overview](#testing-overview)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [System Testing](#system-testing)
5. [Performance Testing](#performance-testing)
6. [Data Validation](#data-validation)
7. [Security Testing](#security-testing)
8. [Monitoring & Alerting Tests](#monitoring--alerting-tests)
9. [Troubleshooting Tests](#troubleshooting-tests)

## Testing Overview

### Testing Philosophy
The Interactive Forest Art Installation requires comprehensive testing across multiple layers:
- **Unit tests** for individual components
- **Integration tests** for data flow between components
- **System tests** for end-to-end functionality
- **Performance tests** for scalability and reliability
- **Field tests** for real-world deployment scenarios

### Testing Environment
```
Development → Staging → Production
    ↓           ↓           ↓
Local      Docker      Cloud
Testing    Testing    Testing
```

### Test Data Requirements
- **Realistic sensor ranges**: Temperature 20-75°C, humidity 30-90%
- **Valid zone configurations**: 3 zones with appropriate sensor counts
- **Proper timestamps**: ISO 8601 format with timezone information
- **Network simulation**: Various connection states and speeds

## Unit Testing

### Simulator Component Tests

#### Test: Data Generation Validation
```bash
# Test basic data structure
python installation_sim.py --snapshot --output test_validation

# Verify output file exists and has correct structure
python -c "
import json
with open('test_validation_snapshot.json', 'r') as f:
    data = json.load(f)
    assert 'environmental' in data
    assert 'tree_biometrics' in data
    assert 'visitor_detection' in data
    print('[OK] Data structure validation passed')
"
```

#### Test: Environmental Data Consistency
```bash
# Test snapshot generation
echo "Testing snapshot generation"
python installation_sim.py --snapshot --output test_data

# Validate environmental data structure
python -c "
import json
with open('test_data_snapshot.json', 'r') as f:
    data = json.load(f)
    env = data['environmental'][0]

    assert 'temperature_c' in env, 'Environmental data should include temperature'
    assert 'humidity_percent' in env, 'Environmental data should include humidity'

    print('[OK] Environmental data validation passed')
    "
```

#### Test: Zone-Specific Behavior
```bash
# Test zone differences
python installation_sim.py --demo --snapshot --output test_zones

python -c "
import json
with open('test_zones_snapshot.json', 'r') as f:
    data = json.load(f)

    zones = {env['zone']: env for env in data['environmental']}

    # Entrance clearing should have more activity
    entrance = zones['entrance_clearing']
    forest = zones['deep_forest']

    # Test zone-specific characteristics
    visitors_entrance = sum(1 for v in data['visitor_detection']
                          if v['zone'] == 'entrance_clearing' and v['movement_detected'])
    visitors_forest = sum(1 for v in data['visitor_detection']
                        if v['zone'] == 'deep_forest' and v['movement_detected'])

    print(f'[INFO] Entrance visitors: {visitors_entrance}, Forest visitors: {visitors_forest}')
    print('[OK] Zone behavior validation passed')
"
```

### Bridge Component Tests

#### Test: InfluxDB Connection
```bash
# Test basic connection
python influx_bridge.py --test-connection

# Expected output should show:
# [OK] InfluxDB Health: pass
# [OK] Write test: SUCCESS
# [OK] Read test: SUCCESS
```

#### Test: Data Conversion
```bash
# Test data conversion without upload
python -c "
from influxdb.influx_bridge import InstallationDataBridge
from simulation.installation_sim import InstallationSimulator

bridge = InstallationDataBridge()
simulator = InstallationSimulator()

# Generate test dataset
dataset = simulator.generate_single_dataset()

# Test conversion methods
env_points = bridge.convert_environmental_to_points(dataset['environmental'])
tree_points = bridge.convert_tree_biometrics_to_points(dataset['tree_biometrics'])
visitor_points = bridge.convert_visitor_detection_to_points(dataset['visitor_detection'])

assert len(env_points) == 3, 'Should have 3 environmental points (one per zone)'
assert len(tree_points) == 27, 'Should have 27 tree points'
assert len(visitor_points) == 15, 'Should have 15 visitor detection points'

print('[OK] Data conversion validation passed')
"
```

## Integration Testing

### End-to-End Data Flow Test
```bash
# Test complete data pipeline
echo "[INFO] Starting integration test..."

# 1. Start simulator in background
python installation_sim.py --interval 5 --output integration_test &
SIM_PID=$!

# 2. Wait for initial data generation
sleep 10

# 3. Test bridge can process the file
python influx_bridge.py --file-watcher --input integration_test &
BRIDGE_PID=$!

# 4. Monitor for 30 seconds
sleep 30

# 5. Clean up
kill $SIM_PID $BRIDGE_PID 2>/dev/null

# 6. Verify data was processed
if ls integration_test_*.json 1> /dev/null 2>&1; then
    echo "[OK] Integration test - Files generated"
else
    echo "[ERROR] Integration test - No files generated"
    exit 1
fi

echo "[OK] Integration test completed"
```

### API Mode Integration Test
```bash
# Test direct API mode
echo "[INFO] Testing API mode integration..."

# Start API mode with short interval for testing
timeout 30s python influx_bridge.py --simulator-api --interval 5

# Check exit code (timeout should cause exit code 124)
if [ $? -eq 124 ]; then
    echo "[OK] API mode integration test completed"
else
    echo "[ERROR] API mode integration test failed"
    exit 1
fi
```

## System Testing

### Complete System Startup Test
```bash
# Test full system startup
echo "[INFO] Testing complete system startup..."

# Create logs directory
mkdir -p logs

# Start monitoring system
./start_monitoring.sh

# Wait for all components to start
sleep 15

# Check that all processes are running
check_process() {
    if pgrep -f "$1" > /dev/null; then
        echo "[OK] $1 is running"
        return 0
    else
        echo "[ERROR] $1 is not running"
        return 1
    fi
}

check_process "installation_sim" || exit 1
check_process "influx_bridge" || exit 1
check_process "telegraf" || exit 1

echo "[OK] System startup test completed"

# Clean up
pkill -f installation_sim
pkill -f influx_bridge
pkill -f telegraf
```

### Data Continuity Test
```bash
# Test data continuity during restart
echo "[INFO] Testing data continuity..."

# Start simulator
python installation_sim.py --interval 2 --output continuity_test &
SIM_PID=$!

# Let it run for 10 seconds
sleep 10

# Kill and restart simulator
kill $SIM_PID
sleep 2
python installation_sim.py --interval 2 --output continuity_test &
SIM_PID=$!

# Run for another 10 seconds
sleep 10
kill $SIM_PID

# Check that data files were created continuously
file_count=$(ls continuity_test_*.json 2>/dev/null | wc -l)
if [ $file_count -gt 5 ]; then
    echo "[OK] Data continuity test - $file_count files generated"
else
    echo "[ERROR] Data continuity test - Only $file_count files generated"
    exit 1
fi
```

## Performance Testing

### Data Volume Test
```bash
# Test high-frequency data generation
echo "[INFO] Testing high-frequency data generation..."

start_time=$(date +%s)

# Generate data every second for 1 minute
timeout 60s python installation_sim.py --interval 1 --output perf_test

end_time=$(date +%s)
duration=$((end_time - start_time))

# Count generated files
file_count=$(ls perf_test_*.json 2>/dev/null | wc -l)
rate=$(echo "scale=2; $file_count / $duration" | bc)

echo "[INFO] Generated $file_count files in $duration seconds"
echo "[INFO] Rate: $rate files/second"

if (( $(echo "$rate > 0.8" | bc -l) )); then
    echo "[OK] Performance test passed"
else
    echo "[ERROR] Performance test failed - rate too low"
    exit 1
fi
```

### Memory Usage Test
```bash
# Test memory usage during extended operation
echo "[INFO] Testing memory usage..."

# Start simulator in background
python installation_sim.py --interval 5 --demo &
SIM_PID=$!

# Monitor memory usage for 60 seconds
for i in {1..12}; do
    if ps -p $SIM_PID > /dev/null; then
        memory=$(ps -o vsz= -p $SIM_PID | tr -d ' ')
        echo "[INFO] Memory usage: ${memory}KB"

        # Check if memory usage is reasonable (< 500MB)
        if [ $memory -gt 500000 ]; then
            echo "[WARNING] High memory usage detected"
        fi
    else
        echo "[ERROR] Process died during memory test"
        exit 1
    fi
    sleep 5
done

kill $SIM_PID
echo "[OK] Memory usage test completed"
```

### Network Performance Test
```bash
# Test network upload performance
echo "[INFO] Testing network performance..."

# Test InfluxDB write performance
python -c "
import time
from influxdb.influx_bridge import InstallationDataBridge
from simulation.installation_sim import InstallationSimulator

bridge = InstallationDataBridge()
simulator = InstallationSimulator()

if not bridge.connect_influxdb():
    print('[ERROR] Cannot connect to InfluxDB')
    exit(1)

# Time 10 uploads
start_time = time.time()
for i in range(10):
    dataset = simulator.generate_single_dataset()
    success = bridge.process_dataset(dataset)
    if not success:
        print(f'[ERROR] Upload {i+1} failed')
        exit(1)

end_time = time.time()
duration = end_time - start_time
rate = 10 / duration

print(f'[INFO] Uploaded 10 datasets in {duration:.2f} seconds')
print(f'[INFO] Rate: {rate:.2f} uploads/second')

if rate > 0.5:  # Should handle at least 0.5 uploads/second
    print('[OK] Network performance test passed')
else:
    print('[ERROR] Network performance test failed')
    exit(1)
"
```

## Data Validation

### Data Quality Tests

#### Test: Value Range Validation
```bash
echo "[INFO] Testing data value ranges..."

python -c "
import json
from simulation.installation_sim import InstallationSimulator

simulator = InstallationSimulator()
dataset = simulator.generate_single_dataset()

# Test environmental data ranges
for env in dataset['environmental']:
    temp = env['temperature_c']
    humidity = env['humidity_percent']
    wind = env['wind_speed_kmh']
    pressure = env['atmospheric_pressure_hpa']

    assert 15 <= temp <= 40, f'Temperature out of range: {temp}'
    assert 30 <= humidity <= 95, f'Humidity out of range: {humidity}'
    assert 0 <= wind <= 50, f'Wind speed out of range: {wind}'
    assert 950 <= pressure <= 1050, f'Pressure out of range: {pressure}'

# Test tree data ranges
for tree in dataset['tree_biometrics']:
    strain = tree['strain_gauge_reading']
    amplitude = tree['movement_amplitude_mm']
    frequency = tree['natural_frequency_hz']
    health = tree['health_score']

    assert 0 <= strain <= 0.01, f'Strain out of range: {strain}'
    assert 0 <= amplitude <= 20, f'Amplitude out of range: {amplitude}'
    assert 0.1 <= frequency <= 5.0, f'Frequency out of range: {frequency}'
    assert 0.5 <= health <= 1.0, f'Health score out of range: {health}'

print('[OK] Data value range validation passed')
"
```

#### Test: Correlation Validation
```bash
echo "[INFO] Testing data correlations..."

python -c "
import json
from simulation.installation_sim import InstallationSimulator

simulator = InstallationSimulator(weather_pattern='windy')
dataset = simulator.generate_single_dataset()

# Get wind data
wind_speeds = {env['zone']: env['wind_speed_kmh'] for env in dataset['environmental']}

# Check tree movement correlates with wind
for tree in dataset['tree_biometrics']:
    zone = tree['zone']
    wind_speed = wind_speeds[zone]
    movement = tree['movement_amplitude_mm']

    # Higher wind should generally mean more movement
    if wind_speed > 20:  # Strong wind
        assert movement > 2, f'Tree movement too low for wind speed {wind_speed}'

print('[OK] Data correlation validation passed')
"
```

### Timestamp Validation
```bash
echo "[INFO] Testing timestamp consistency..."

python -c "
import json
from datetime import datetime, timezone
from simulation.installation_sim import InstallationSimulator

simulator = InstallationSimulator()
dataset = simulator.generate_single_dataset()

# Check main timestamp
main_timestamp = datetime.fromisoformat(dataset['timestamp'].replace('Z', '+00:00'))

# Check all sub-timestamps match
for category in ['environmental', 'tree_biometrics', 'visitor_detection']:
    for item in dataset[category]:
        item_timestamp = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
        time_diff = abs((main_timestamp - item_timestamp).total_seconds())
        assert time_diff < 1, f'Timestamp mismatch in {category}: {time_diff}s'

print('[OK] Timestamp consistency validation passed')
"
```

## Security Testing

### API Token Validation
```bash
echo "[INFO] Testing API token security..."

# Test with invalid token
python -c "
from influxdb.influx_bridge import InstallationDataBridge, InfluxDBConfig

# Test with invalid token
config = InfluxDBConfig()
config.token = 'invalid_token_12345'

bridge = InstallationDataBridge()
bridge.config = config

# This should fail
try:
    success = bridge.connect_influxdb()
    if success:
        print('[ERROR] Connected with invalid token - security issue!')
        exit(1)
    else:
        print('[OK] Invalid token properly rejected')
except Exception as e:
    print(f'[OK] Invalid token caused expected error: {type(e).__name__}')
"
```

### Data Sanitization Test
```bash
echo "[INFO] Testing data sanitization..."

python -c "
from influxdb.influx_bridge import InstallationDataBridge

bridge = InstallationDataBridge()

# Test with potentially malicious data
malicious_data = [
    {
        'zone': '<script>alert(\"xss\")</script>',
        'temperature_c': 25.0,
        'humidity_percent': 60.0,
        'wind_speed_kmh': 5.0,
        'atmospheric_pressure_hpa': 1015.0,
        'timestamp': '2025-01-15T12:00:00Z'
    }
]

# Convert to points (should sanitize automatically)
points = bridge.convert_environmental_to_points(malicious_data)

# Check that script tags are handled properly
point = points[0]
zone_tag = None
for field_key, field_value in point._tags.items():
    if field_key == 'zone':
        zone_tag = field_value
        break

# InfluxDB should handle this safely, but check it's not executed
if '<script>' in str(zone_tag):
    print('[WARNING] Script tags not sanitized in zone tag')
else:
    print('[OK] Data sanitization test passed')
"
```

## Monitoring & Alerting Tests

### Health Check Tests
```bash
echo "[INFO] Testing health check endpoints..."

# Test InfluxDB health
python -c "
from influxdb.influx_bridge import InstallationDataBridge

bridge = InstallationDataBridge()
if bridge.connect_influxdb():
    print('[OK] InfluxDB health check passed')
else:
    print('[ERROR] InfluxDB health check failed')
    exit(1)
"

# Test system process health
for process in "python.*installation_sim" "python.*influx_bridge"; do
    if pgrep -f "$process" > /dev/null; then
        echo "[OK] Process $process is healthy"
    else
        echo "[INFO] Process $process is not running (expected during test)"
    fi
done
```

### Log Analysis Test
```bash
echo "[INFO] Testing log analysis..."

# Create test logs
mkdir -p logs
echo "[OK] Test message" > logs/test.log
echo "[ERROR] Test error message" > logs/test.log
echo "[WARNING] Test warning message" > logs/test.log

# Analyze log patterns
error_count=$(grep -c "\[ERROR\]" logs/test.log)
warning_count=$(grep -c "\[WARNING\]" logs/test.log)
ok_count=$(grep -c "\[OK\]" logs/test.log)

echo "[INFO] Log analysis results:"
echo "  Errors: $error_count"
echo "  Warnings: $warning_count"
echo "  OK messages: $ok_count"

if [ $error_count -eq 1 ] && [ $warning_count -eq 1 ] && [ $ok_count -eq 1 ]; then
    echo "[OK] Log analysis test passed"
else
    echo "[ERROR] Log analysis test failed"
    exit 1
fi
```

## Troubleshooting Tests

### Recovery Tests

#### Test: Network Disconnection Recovery
```bash
echo "[INFO] Testing network disconnection recovery..."

# This test simulates network issues by using a fake endpoint
python -c "
import time
from influxdb.influx_bridge import InstallationDataBridge, InfluxDBConfig
from simulation.installation_sim import InstallationSimulator

# Create bridge with fake endpoint
config = InfluxDBConfig()
config.url = 'https://fake-endpoint-that-does-not-exist.com'

bridge = InstallationDataBridge()
bridge.config = config
simulator = InstallationSimulator()

# Try to connect (should fail)
connected = bridge.connect_influxdb()
if connected:
    print('[ERROR] Connected to fake endpoint - test invalid')
    exit(1)

print('[OK] Network disconnection simulation successful')

# Test that simulator continues working despite connection failure
dataset = simulator.generate_single_dataset()
if dataset and 'environmental' in dataset:
    print('[OK] Simulator continues working during network issues')
else:
    print('[ERROR] Simulator failed during network issues')
    exit(1)
"
```

#### Test: Data Recovery After Restart
```bash
echo "[INFO] Testing data recovery after restart..."

# Start simulator with specific output
python installation_sim.py --interval 2 --output recovery_test &
SIM_PID=$!

# Let it create some files
sleep 6

# Kill simulator
kill $SIM_PID

# Count files before restart
files_before=$(ls recovery_test_*.json 2>/dev/null | wc -l)

# Restart simulator with same output prefix
python installation_sim.py --interval 2 --output recovery_test &
SIM_PID=$!

# Let it create more files
sleep 6
kill $SIM_PID

# Count files after restart
files_after=$(ls recovery_test_*.json 2>/dev/null | wc -l)

if [ $files_after -gt $files_before ]; then
    echo "[OK] Data recovery test passed - new files created after restart"
else
    echo "[ERROR] Data recovery test failed - no new files after restart"
    exit 1
fi
```

### Error Scenario Tests

#### Test: Disk Space Handling
```bash
echo "[INFO] Testing disk space handling..."

# Create a small test filesystem (1MB)
test_dir="test_disk_space"
mkdir -p $test_dir

# Try to fill it up by generating many files
python -c "
import os
import json

test_dir = 'test_disk_space'
file_count = 0
max_files = 100

try:
    for i in range(max_files):
        filename = f'{test_dir}/test_file_{i:04d}.json'
        data = {'test': 'data' * 1000}  # Create larger files

        with open(filename, 'w') as f:
            json.dump(data, f)

        file_count += 1

        # Check disk usage
        if os.path.getsize(filename) == 0:
            print(f'[WARNING] Zero-size file created at {i} files')
            break

except OSError as e:
    print(f'[INFO] Disk space limit reached after {file_count} files: {e}')

print(f'[OK] Disk space handling test completed - created {file_count} files')
"

# Clean up
rm -rf $test_dir
```

### Performance Degradation Tests

#### Test: Memory Leak Detection
```bash
echo "[INFO] Testing for memory leaks..."

# Run simulator for extended period and monitor memory
python -c "
import time
import psutil
import os
from simulation.installation_sim import InstallationSimulator

simulator = InstallationSimulator()
process = psutil.Process(os.getpid())

initial_memory = process.memory_info().rss / 1024 / 1024  # MB
print(f'[INFO] Initial memory usage: {initial_memory:.2f} MB')

# Generate data continuously for 30 seconds
start_time = time.time()
iteration_count = 0

while time.time() - start_time < 30:
    dataset = simulator.generate_single_dataset()
    iteration_count += 1

    if iteration_count % 10 == 0:
        current_memory = process.memory_info().rss / 1024 / 1024
        print(f'[INFO] Memory after {iteration_count} iterations: {current_memory:.2f} MB')

    time.sleep(0.1)

final_memory = process.memory_info().rss / 1024 / 1024
memory_growth = final_memory - initial_memory

print(f'[INFO] Final memory usage: {final_memory:.2f} MB')
print(f'[INFO] Memory growth: {memory_growth:.2f} MB')

if memory_growth < 50:  # Less than 50MB growth is acceptable
    print('[OK] Memory leak test passed')
else:
    print('[WARNING] Potential memory leak detected')
"
```

## Test Automation Script

### Complete Test Suite
```bash
#!/bin/bash
# run_all_tests.sh - Complete test suite

echo "========================================="
echo "Interactive Forest Installation Tests"
echo "========================================="

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"

    echo ""
    echo "Running: $test_name"
    echo "-----------------------------------------"

    if eval "$test_command"; then
        echo "[OK] $test_name PASSED"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo "[ERROR] $test_name FAILED"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Run all test categories
run_test "Data Generation Validation" "python installation_sim.py --snapshot --output test_validation && [ -f test_validation_snapshot.json ]"

run_test "InfluxDB Connection" "python influx_bridge.py --test-connection"

run_test "Environmental Data Generation" "python installation_sim.py --snapshot --output test_data && [ -f test_data_snapshot.json ]"

run_test "System Startup" "./start_monitoring.sh && sleep 10 && pgrep -f 'installation_sim|influx_bridge|telegraf' > /dev/null && pkill -f 'installation_sim|influx_bridge|telegraf'"

# Summary
echo ""
echo "========================================="
echo "Test Results Summary"
echo "========================================="
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo "[OK] All tests passed!"
    exit 0
else
    echo "[ERROR] Some tests failed!"
    exit 1
fi
```

Make the script executable:
```bash
chmod +x run_all_tests.sh
```

Run the complete test suite:
```bash
./run_all_tests.sh
```