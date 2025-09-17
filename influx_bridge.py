import asyncio
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# ================================================================================
# CONFIGURATION INFLUXDB
# ================================================================================

# To be filled with your InfluxDB instance details 
@dataclass
class InfluxDBConfig:
    url: str = "https://influx.g-sdn.com"
    token: str = "QPUlR2LDEuhyDW2zheg-6OM39JRCZb3UyOaeRK-tI1GOlSI754rqS9pM435TabBETeUPp2yk1VqDlyZb69P0Fw=="
    org: str = "interactiveInstallation"
    bucket: str = "installations"


class InstallationDataBridge:
    """Bridges installation data created by the simulator to InfluxDB"""

    def __init__(self):
        self.config = InfluxDBConfig()
        self.client = None
        self.write_api = None
        self.connected = False

        self.stats = {
            "total_points_written": 0,
            "total_batches_written": 0,
            "write_errors": 0,
            "last_write_time": None,
            "connection_attempts": 0,
            "uptime_start": time.time(),
        }

    def connect_influxdb(self) -> bool:
        """Establishes InfluxDB connection"""
        try:
            self.stats["connection_attempts"] += 1
            self.client = InfluxDBClient(
                url=self.config.url, token=self.config.token, org=self.config.org
            )

            # Test connection
            health = self.client.health()
            if health.status == "pass":
                self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
                self.connected = True
                print(f"Connected to InfluxDB: {self.config.url}")
                print(f"   Organization: {self.config.org}")
                print(f"   Bucket: {self.config.bucket}")
                return True
            else:
                print(f"[ERROR] InfluxDB health check failed: {health.status}")
                return False

        except Exception as e:
            print(f"[ERROR] InfluxDB connection failed: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Closes InfluxDB connection"""
        if self.client:
            self.client.close()
            self.connected = False
            print("[INFO] Disconnected from InfluxDB")

    def convert_environmental_to_points(
        self, environmental_data: List[Dict]
    ) -> List[Point]:
        """Converts environmental data to InfluxDB points"""
        points = []
        for reading in environmental_data:
            point = (
                Point("environmental")
                .tag("zone", reading["zone"])
                .tag("measurement_type", "weather")
                .field("temperature_c", float(reading["temperature_c"]))
                .field("humidity_percent", float(reading["humidity_percent"]))
                .time(reading["timestamp"])
            )
            points.append(point)
        return points

    def convert_tree_biometrics_to_points(self, tree_data: List[Dict]) -> List[Point]:
        """Converts tree data to InfluxDB points"""
        points = []
        for reading in tree_data:
            point = (
                Point("tree_biometrics")
                .tag("tree_id", reading["tree_id"])
                .field("strain_x_mm", float(reading["strain_x_mm"]))
                .field("strain_y_mm", float(reading["strain_y_mm"]))
                .time(reading["timestamp"])
            )
            points.append(point)
        return points

    def convert_visitor_detection_to_points(
        self, visitor_data: List[Dict]
    ) -> List[Point]:
        """Converts visitor detection data to InfluxDB points"""
        points = []
        for reading in visitor_data:
            point = (
                Point("visitor_detection")
                .tag("sensor_id", reading["sensor_id"])
                .tag("zone", reading["zone"])
                .tag("sensor_type", "tf_mini_lidar")
                .field("signal_strength", float(reading["signal_strength"]))
                .field("confidence_level", float(reading["confidence_level"]))
                .field("detection_active", reading["detection_active"])
                .field("visitor_count_estimate", int(reading["visitor_count_estimate"]))
                .time(reading["timestamp"])
            )
            points.append(point)
        return points

    def convert_user_engagement_to_points(
        self, engagement_data: List[Dict]
    ) -> List[Point]:
        """Converts user engagement data to InfluxDB points"""
        points = []
        for reading in engagement_data:
            point = (
                Point("user_engagement")
                .tag("zone", reading["zone"])
                .field("average_engagement_duration_sec", float(reading["average_engagement_duration_sec"]))
                .field("engagement_score", float(reading["engagement_score"]))
                .time(reading["timestamp"])
            )
            points.append(point)
        return points

    def convert_audio_system_to_points(self, audio_data: List[Dict]) -> List[Point]:
        """Converts audio data to InfluxDB points"""
        points = []
        for reading in audio_data:
            point = (
                Point("audio_system")
                .tag("speaker_id", reading["speaker_id"])
                .tag("zone", reading["zone"])
                .field("volume_db", float(reading["volume_db"]))
                .time(reading["timestamp"])
            )
            points.append(point)
        return points

    def convert_lighting_system_to_points(
        self, lighting_data: List[Dict]
    ) -> List[Point]:
        """Converts lighting data to InfluxDB points"""
        points = []
        for reading in lighting_data:
            point = (
                Point("lighting_system")
                .tag("led_id", reading["led_id"])
                .tag("zone", reading["zone"])
                .field("red_intensity", int(reading["red_intensity"]))
                .field("green_intensity", int(reading["green_intensity"]))
                .field("blue_intensity", int(reading["blue_intensity"]))
                .time(reading["timestamp"])
            )
            points.append(point)
        return points

    def convert_dataset_to_influx_points(self, dataset: Dict) -> List[Point]:
        """Convertit un dataset complet en points InfluxDB"""
        all_points = []

        if "environmental" in dataset:
            all_points.extend(
                self.convert_environmental_to_points(dataset["environmental"])
            )

        if "tree_biometrics" in dataset:
            all_points.extend(
                self.convert_tree_biometrics_to_points(dataset["tree_biometrics"])
            )

        if "visitor_detection" in dataset:
            all_points.extend(
                self.convert_visitor_detection_to_points(dataset["visitor_detection"])
            )

        if "metadata" in dataset and "user_engagement" in dataset["metadata"]:
            all_points.extend(
                self.convert_user_engagement_to_points(dataset["metadata"]["user_engagement"])
            )

        if "audio_system" in dataset:
            all_points.extend(
                self.convert_audio_system_to_points(dataset["audio_system"])
            )

        if "lighting_system" in dataset:
            all_points.extend(
                self.convert_lighting_system_to_points(dataset["lighting_system"])
            )

        if "metadata" in dataset:
            metadata = dataset["metadata"]
            meta_point = (
                Point("system_metadata")
                .tag("weather_pattern", metadata.get("weather_pattern", "unknown"))
                .field(
                    "total_visitors_detected",
                    int(metadata.get("stats", {}).get("total_visitors_detected", 0)),
                )
                .field(
                    "total_power_consumption",
                    float(metadata.get("stats", {}).get("total_power_consumption", 0)),
                )
                .field(
                    "average_tree_movement",
                    float(metadata.get("stats", {}).get("average_tree_movement", 0)),
                )
                .time(metadata["timestamp"])
            )
            all_points.append(meta_point)

        return all_points

    def write_points_to_influx(self, points: List[Point]) -> bool:
        """Writes a list of points to InfluxDB"""
        if not self.connected or not self.write_api:
            print("[ERROR] Not connected to InfluxDB")
            if not self.connect_influxdb():
                return False

        try:
            self.write_api.write(bucket=self.config.bucket, record=points)

            # Update statistics
            self.stats["total_points_written"] += len(points)
            self.stats["total_batches_written"] += 1
            self.stats["last_write_time"] = datetime.now(timezone.utc).isoformat()

            return True

        except Exception as e:
            print(f"[ERROR] Write error: {e}")
            self.stats["write_errors"] += 1
            return False

    def process_json_dataset(self, dataset: Dict) -> bool:
        """Traite un dataset JSON et l'envoie vers InfluxDB"""
        try:
            points = self.convert_dataset_to_influx_points(dataset)
            if points:
                success = self.write_points_to_influx(points)
                if success:
                    timestamp = dataset.get("metadata", {}).get("timestamp", "unknown")
                    print(f"[INFO] Wrote {len(points)} points to InfluxDB at {timestamp}")
                return success
            else:
                print("[WARNING] No points to write")
                return False

        except Exception as e:
            print(f"[ERROR] Error processing dataset: {e}")
            return False

    def print_statistics(self):
        """Displays bridge statistics"""
        uptime = time.time() - self.stats["uptime_start"]
        print(f"\n[STATS] InfluxDB Bridge Statistics:")
        print(
            f"   Uptime: {uptime//3600:.0f}h {(uptime%3600)//60:.0f}m {uptime%60:.0f}s"
        )
        print(
            f"   Connection: {'🟢 Connected' if self.connected else '🔴 Disconnected'}"
        )
        print(f"   Points written: {self.stats['total_points_written']}")
        print(f"   Batches written: {self.stats['total_batches_written']}")
        print(f"   Write errors: {self.stats['write_errors']}")
        if self.stats["total_batches_written"] + self.stats["write_errors"] > 0:
            success_rate = (self.stats['total_batches_written']/(self.stats['total_batches_written']+self.stats['write_errors'])*100)
            print(f"   Success rate: {success_rate:.1f}%")
        else:
            print(f"   Success rate: N/A")


async def run_simulator_api_mode(
    bridge: InstallationDataBridge, interval_seconds: int = 5
):
    """Direct API mode: generates and sends data without intermediate files"""
    from installation_sim import InstallationSim

    print("[INFO] API Bridge Mode - Direct connection to simulator")
    print(f"   Interval: {interval_seconds}s")
    print("   Press Ctrl+C to stop")
    print("=" * 60)

    simulator = InstallationSim()
    iterations = 0
    start_time = time.time()

    try:
        while True:
            iteration_start = time.time()

            # Use real time
            simulator.current_time = datetime.now(timezone.utc)

            dataset = simulator.generate_complete_dataset()

            # Send to InfluxDB
            success = bridge.process_json_dataset(dataset)

            if not success and iterations % 5 == 0:
                # Attempt reconnection every 5 iterations if failed
                print("[INFO] Attempting to reconnect to InfluxDB...")
                bridge.connect_influxdb()

            # Display stats periodically
            if iterations % 10 == 0:
                bridge.print_statistics()
                simulator.print_live_stats()

            iterations += 1

            # Respect interval
            iteration_time = time.time() - iteration_start
            sleep_time = max(0.1, interval_seconds - iteration_time)
            await asyncio.sleep(sleep_time)

    except KeyboardInterrupt:
        print(f"\n[INFO] API Bridge stopped after {iterations} iterations")
        bridge.print_statistics()


def test_connection_and_write(bridge: InstallationDataBridge):
    """Test InfluxDB connection with dummy data"""
    print("Testing InfluxDB connection...")

    if not bridge.connect_influxdb():
        return False

    # Create test point
    test_point = (
        Point("connection_test")
        .tag("test_type", "bridge_test_light")
        .field("value", 42.0)
        .field("timestamp", time.time())
        .time(datetime.now(timezone.utc))
    )

    success = bridge.write_points_to_influx([test_point])
    if success:
        print("[INFO] Test write successful")

        # Read test
        try:
            if bridge.client:
                query_api = bridge.client.query_api()
                query = f'from(bucket:"{bridge.config.bucket}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "connection_test")'
                result = query_api.query(query)
            else:
                print("[WARNING] Client not initialized")
                return False

            if result:
                print("[INFO] Test read successful")
                return True
            else:
                print("[WARNING] Test read: no data returned")
                return True  # Write succeeded at least
        except Exception as e:
            print(f"[WARNING] Test read failed: {e}")
            return True  # Write succeeded at least
    else:
        print("[ERROR] Test write failed")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Forest Installation InfluxDB Bridge (Light Version)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Direct API mode with simulator
  python influx_bridge_light.py --simulator-api --interval 30
  
  # Connection test
  python influx_bridge_light.py --test-connection
        """,
    )

    # Operation modes
    parser.add_argument(
        "--simulator-api",
        action="store_true",
        help="Direct API mode with simulator",
    )
    parser.add_argument(
        "--test-connection", action="store_true", help="Test InfluxDB connection"
    )

    # Configuration
    parser.add_argument(
        "--interval", type=int, default=30, help="Intervalle en secondes (mode API)"
    )

    args = parser.parse_args()

    # Create bridge
    bridge = InstallationDataBridge()

    try:
        if args.test_connection:
            test_connection_and_write(bridge)

        elif args.simulator_api:
            if not bridge.connect_influxdb():
                return 1
            asyncio.run(run_simulator_api_mode(bridge, args.interval))

        else:
            print(
                "[ERROR] Please specify a mode: --simulator-api or --test-connection"
            )
            parser.print_help()
            return 1

    finally:
        bridge.disconnect()

    return 0


if __name__ == "__main__":
    exit(main())