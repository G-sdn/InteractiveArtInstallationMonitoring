#!/usr/bin/env python3
"""
Zone Hub System Metrics Simulator
=================================

Simulates system metrics for 3 zone microcontrollers (ESP32/Arduino)
that would be deployed in the forest installation.

This script outputs InfluxDB line protocol format for Telegraf to consume.
"""

import random
import time
import sys
from datetime import datetime, timezone

def generate_zone_metrics():
    """Generate realistic system metrics for zone microcontrollers"""

    zones = [
        {"id": "mcu-entrance", "zone": "entrance_clearing", "base_temp": 35},
        {"id": "mcu-forest", "zone": "deep_forest", "base_temp": 32},
        {"id": "mcu-riverside", "zone": "riverside", "base_temp": 30}
    ]

    timestamp_ns = int(time.time() * 1e9)

    for zone in zones:
        device_id = zone["id"]
        zone_name = zone["zone"]
        base_temp = zone["base_temp"]

        # Simulate realistic microcontroller metrics
        cpu_usage = max(10, min(85, 25 + random.gauss(0, 15)))  # 10-85% range
        memory_usage = max(20, min(80, 45 + random.gauss(0, 10)))  # 20-80% range

        # Temperature varies with load and environment
        temp_variation = (cpu_usage - 25) * 0.3 + random.gauss(0, 3)
        system_temp = max(25, min(75, base_temp + temp_variation))

        # Uptime (simulate occasional restarts)
        uptime_hours = random.randint(1, 720)  # 1 hour to 30 days
        uptime_seconds = uptime_hours * 3600 + random.randint(0, 3600)

        # WiFi signal strength (varies by zone)
        if zone_name == "deep_forest":
            wifi_rssi = random.randint(-85, -65)  # Weaker signal in forest
        else:
            wifi_rssi = random.randint(-75, -45)  # Better signal in clearing/riverside

        # Sensor count (number of connected sensors per zone)
        if zone_name == "entrance_clearing":
            sensor_count = 8  # More sensors at entrance
        else:
            sensor_count = 6  # Fewer sensors in other zones

        # Output in InfluxDB line protocol format
        print(f"zone_hub_system,device_id={device_id},zone={zone_name},device_type=esp32 "
              f"cpu_usage_percent={cpu_usage:.1f},"
              f"memory_usage_percent={memory_usage:.1f},"
              f"system_temperature_c={system_temp:.1f},"
              f"uptime_seconds={uptime_seconds}i,"
              f"wifi_rssi_dbm={wifi_rssi}i,"
              f"connected_sensors={sensor_count}i "
              f"{timestamp_ns}")

        # Network metrics for each zone hub
        packet_loss = max(0, min(5, random.gauss(0.5, 1)))  # 0-5% packet loss
        latency_ms = max(1, random.gauss(15, 8))  # Network latency varies

        print(f"zone_hub_network,device_id={device_id},zone={zone_name} "
              f"packet_loss_percent={packet_loss:.2f},"
              f"latency_ms={latency_ms:.1f},"
              f"wifi_connected={1 if wifi_rssi > -80 else 0}i "
              f"{timestamp_ns}")

        # Power metrics (simulated from battery/solar if applicable)
        battery_percent = max(50, min(100, 85 + random.gauss(0, 10)))  # 50-100%
        power_consumption_w = max(2, 5 + (cpu_usage / 100) * 3 + random.gauss(0, 0.5))  # 2-8W

        print(f"zone_hub_power,device_id={device_id},zone={zone_name} "
              f"battery_percent={battery_percent:.1f},"
              f"power_consumption_w={power_consumption_w:.2f},"
              f"charging={1 if random.random() > 0.3 else 0}i "
              f"{timestamp_ns}")

def generate_installation_infrastructure_metrics():
    """Generate metrics for overall installation infrastructure"""

    timestamp_ns = int(time.time() * 1e9)

    # Total installation power consumption
    total_power = random.gauss(1200, 200)  # ~1200W ± 200W
    total_power = max(800, min(2000, total_power))

    # UPS/Battery backup status
    ups_battery = max(75, min(100, 90 + random.gauss(0, 5)))
    ups_load_percent = max(20, min(90, total_power / 15))  # Assuming 1500W UPS

    # Network infrastructure
    switch_temp = max(25, min(65, 40 + random.gauss(0, 5)))
    connected_devices = random.randint(12, 18)  # 3 zone hubs + sensors + control systems

    print(f"installation_infrastructure,component=power_management "
          f"total_power_consumption_w={total_power:.1f},"
          f"ups_battery_percent={ups_battery:.1f},"
          f"ups_load_percent={ups_load_percent:.1f} "
          f"{timestamp_ns}")

    print(f"installation_infrastructure,component=network "
          f"switch_temperature_c={switch_temp:.1f},"
          f"connected_devices={connected_devices}i,"
          f"network_uptime_percent={random.uniform(98, 100):.2f} "
          f"{timestamp_ns}")

def main():
    """Main execution function"""
    try:
        # Generate zone hub metrics
        generate_zone_metrics()

        # Generate installation infrastructure metrics
        generate_installation_infrastructure_metrics()

    except Exception as e:
        # Log errors to stderr (Telegraf will capture this)
        print(f"Error generating zone metrics: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()