#!/usr/bin/env python3
"""
Interactive Installation - Data Simulator
==========================================================

Simulates a reduced interactive forest installation with:
- 15 capteurs TF-Mini LiDAR (5 par zone)
- 3 indicateurs audio (1 par zone)
- 3 indicateurs LED RGB (1 par zone)
- 9 arbres avec capteurs strain (3 par zone)
- Environmental sensors

Usage:
    python installation_sim.py --duration 300 --interval 30
    python installation_sim.py --output installation_data.json
"""

import asyncio
import json
import random
import numpy as np
import argparse
import csv
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import time


@dataclass 
class EnvironmentalReading:
    """Environmental data per zone"""
    timestamp: str
    zone: str
    temperature_c: float
    humidity_percent: float


@dataclass
class TreeBiometrics:
    """Tree biometric sensors"""
    timestamp: str
    tree_id: str
    strain_x_mm: float
    strain_y_mm: float


@dataclass
class VisitorDetection:
    """TF-Mini LiDAR visitor detection sensors"""
    timestamp: str
    sensor_id: str
    zone: str
    signal_strength: float
    confidence_level: float
    detection_active: bool
    visitor_count_estimate: int


@dataclass
class AudioSystem:
    """Audio system (minimal)"""
    timestamp: str
    speaker_id: str
    zone: str
    volume_db: float


@dataclass
class LightingSystem:
    """LED lighting system (minimal RGB)"""
    timestamp: str
    led_id: str
    zone: str
    red_intensity: int
    green_intensity: int  
    blue_intensity: int


@dataclass
class UserEngagement:
    """Visitor engagement metrics (derived)"""
    timestamp: str
    zone: str
    average_engagement_duration_sec: float
    engagement_score: float


class InstallationSim:
    """Installation data simulator"""
    
    def __init__(self, start_time: Optional[datetime] = None):
        self.start_time = start_time or datetime.now(timezone.utc)
        self.current_time = self.start_time

        # Forest zone configuration (reduced)
        self.zones = {
            "entrance_clearing": {
                "trees": 3, "visitor_sensors": 5, "speakers": 1, "leds": 1,
                "typical_visitors": 5, "description": "Zone d'accueil ouverte"
            },
            "deep_forest": {
                "trees": 3, "visitor_sensors": 5, "speakers": 1, "leds": 1,
                "typical_visitors": 2, "description": "Dense forest, more mystical"
            },
            "riverside": {
                "trees": 3, "visitor_sensors": 5, "speakers": 1, "leds": 1,
                "typical_visitors": 3, "description": "Near the river, water sounds"
            }
        }

        # Session variables for consistency
        self.tree_movement_intensity = 0.1
        self.visitor_flow_multiplier = 1.0

        # State variables for stable data and correlations
        self.last_temperature_by_zone = {}
        self.last_humidity_by_zone = {}
        self.last_volume_by_zone = {}
        self.zone_visitor_activity = {zone: 0 for zone in self.zones.keys()}
        
        # Real-time statistics
        self.stats = {
            "total_visitors_detected": 0,
            "active_audio_channels": 0,
            "total_power_consumption": 0,
            "average_tree_movement": 0
        }
        
        # Engagement tracking per zone
        self.engagement_history = {zone: [] for zone in self.zones.keys()}
        
    def advance_time(self, seconds: int = 30):
        """Avance la simulation de X secondes"""
        self.current_time += timedelta(seconds=seconds)
    
    def get_current_timestamp(self) -> str:
        """ISO formatted timestamp for data"""
        return self.current_time.isoformat()
    
    def simulate_weather_conditions(self) -> List[EnvironmentalReading]:
        """Generates environmental conditions"""
        readings = []
        hour = self.current_time.hour

        # Day/night cycle for base temperature
        base_temp = 15 + 8 * np.sin((hour - 6) * np.pi / 12)

        # Stable variation
        temp_variation = random.uniform(-0.5, 0.5)
        humidity_base = 60

        # Generate data per zone
        for zone_id in self.zones.keys():
            # Zone-specific micro-climate variations
            if zone_id == "riverside":
                zone_temp_mod = -2  # Cooler near water
                zone_humidity_mod = 15  # More humid
            elif zone_id == "deep_forest":
                zone_temp_mod = -1  # Tree shade
                zone_humidity_mod = 10  # Humidity retention
            else:  # entrance_clearing
                zone_temp_mod = 1  # More exposed to sun
                zone_humidity_mod = -5  # Drier

            # Use last temperature as base for stability, with small gradual changes
            target_temp = base_temp + temp_variation + zone_temp_mod
            if zone_id in self.last_temperature_by_zone:
                # Gradual change toward target
                current_temp = self.last_temperature_by_zone[zone_id]
                temperature = current_temp + (target_temp - current_temp) * 0.1
            else:
                temperature = target_temp

            # Similar for humidity
            target_humidity = max(20, min(95, humidity_base + zone_humidity_mod))
            if zone_id in self.last_humidity_by_zone:
                current_humidity = self.last_humidity_by_zone[zone_id]
                humidity = current_humidity + (target_humidity - current_humidity) * 0.1
            else:
                humidity = target_humidity

            # Store for next iteration
            self.last_temperature_by_zone[zone_id] = round(temperature, 1)
            self.last_humidity_by_zone[zone_id] = round(max(20, min(95, humidity)), 1)

            reading = EnvironmentalReading(
                timestamp=self.get_current_timestamp(),
                zone=zone_id,
                temperature_c=self.last_temperature_by_zone[zone_id],
                humidity_percent=self.last_humidity_by_zone[zone_id]
            )
            readings.append(reading)

        return readings
    
    def simulate_tree_biometrics(self) -> List[TreeBiometrics]:
        """Simule les capteurs strain gauge sur arbres"""
        readings = []
        total_movement = 0
        tree_count = 0
        
        for zone_id, zone_config in self.zones.items():
            for tree_idx in range(zone_config["trees"]):
                tree_id = f"{zone_id}_tree_{tree_idx:02d}"
                
                # Natural oscillation based on time
                time_factor = self.current_time.timestamp() * 0.1
                natural_sway = 0.1 * np.sin(time_factor + tree_idx)
                
                # Random variation for each tree
                random_movement = random.uniform(-0.05, 0.05)
                
                # Strain sur les axes X et Y
                strain_x = natural_sway + random_movement
                strain_y = natural_sway * 0.6 + random.uniform(-0.03, 0.03)
                
                movement_magnitude = abs(strain_x) + abs(strain_y)
                total_movement += movement_magnitude
                tree_count += 1
                
                reading = TreeBiometrics(
                    timestamp=self.get_current_timestamp(),
                    tree_id=tree_id,
                    strain_x_mm=round(strain_x, 4),
                    strain_y_mm=round(strain_y, 4)
                )
                readings.append(reading)
                
        # Update global intensity
        self.tree_movement_intensity = total_movement / tree_count if tree_count > 0 else 0.1
        self.stats["average_tree_movement"] = round(self.tree_movement_intensity, 3)
        
        return readings
    
    def simulate_visitor_detection(self) -> List[VisitorDetection]:
        """Simulates TF-Mini LiDAR sensors for visitor detection with improved correlations"""
        readings = []
        hour = self.current_time.hour

        # Presence probability by hour
        if 9 <= hour <= 18:  # Heures d'ouverture
            base_probability = 0.3
        elif 19 <= hour <= 22:  # Evening
            base_probability = 0.15
        else:  # Nuit
            base_probability = 0.02

        base_probability *= self.visitor_flow_multiplier

        total_visitors = 0

        # Reset zone activity before calculating
        for zone_id in self.zones.keys():
            self.zone_visitor_activity[zone_id] = 0

        for zone_id, zone_config in self.zones.items():
            zone_visitor_factor = zone_config["typical_visitors"] / 3
            zone_visitors_this_cycle = 0
            zone_detections = []

            for sensor_idx in range(zone_config["visitor_sensors"]):
                sensor_id = f"{zone_id}_lidar_{sensor_idx:02d}"

                detection_prob = base_probability * zone_visitor_factor
                has_detection = random.random() < detection_prob

                if has_detection:
                    # More stable signal strength when detecting
                    signal_strength = random.uniform(75, 90)  # Reduced noise range
                    confidence = min(95, signal_strength + random.uniform(-3, 3))  # Less noise
                    visitor_estimate = random.choice([1, 1, 1, 2, 2, 3])
                    total_visitors += visitor_estimate
                    zone_visitors_this_cycle += visitor_estimate
                else:
                    signal_strength = random.uniform(15, 40)
                    confidence = random.uniform(10, 30)
                    visitor_estimate = 0

                reading = VisitorDetection(
                    timestamp=self.get_current_timestamp(),
                    sensor_id=sensor_id,
                    zone=zone_id,
                    signal_strength=round(signal_strength, 1),
                    confidence_level=round(confidence, 1),
                    detection_active=has_detection,
                    visitor_count_estimate=visitor_estimate
                )
                readings.append(reading)
                zone_detections.append(reading)

            # Store zone activity for audio/lighting correlation
            self.zone_visitor_activity[zone_id] = int(zone_visitors_this_cycle)

        self.stats["total_visitors_detected"] = total_visitors
        return readings
    
    def simulate_audio_system(self) -> List[AudioSystem]:
        """Simulates audio system with direct correlation to visitors per zone"""
        readings = []

        for zone_id in self.zones.keys():
            speaker_id = f"{zone_id}_speaker_main"

            # Audio reacts directly to visitors in THIS zone
            zone_visitors = self.zone_visitor_activity.get(zone_id, 0)
            tree_influence = self.tree_movement_intensity * 0.3
            visitor_influence = min(0.7, zone_visitors * 0.15)  # Strong visitor response

            total_intensity = tree_influence + visitor_influence
            target_volume = 75 * total_intensity  # Max 75dB

            # Much more stable volume - use last volume for smoothing
            if zone_id in self.last_volume_by_zone:
                current_volume = self.last_volume_by_zone[zone_id]
                # Gradual change toward target
                new_volume = current_volume + (target_volume - current_volume) * 0.3
            else:
                new_volume = target_volume

            # Small amount of realistic noise
            new_volume = max(0, new_volume + random.uniform(-2, 2))
            self.last_volume_by_zone[zone_id] = float(round(new_volume, 1))

            reading = AudioSystem(
                timestamp=self.get_current_timestamp(),
                speaker_id=speaker_id,
                zone=zone_id,
                volume_db=self.last_volume_by_zone[zone_id]
            )
            readings.append(reading)

        return readings
    
    def simulate_lighting_system(self) -> List[LightingSystem]:
        """Simulates LED lighting system with direct reaction to visitors per zone"""
        readings = []
        hour = self.current_time.hour

        for zone_id in self.zones.keys():
            led_id = f"{zone_id}_led_main"

            # Lighting reacts to THIS zone's visitors specifically
            zone_visitors = self.zone_visitor_activity.get(zone_id, 0)

            # Base intensity according to time of day
            if 6 <= hour <= 18:  # Jour
                time_base = 0.2
            elif 18 <= hour <= 22:  # Evening
                time_base = 0.6
            else:  # Nuit
                time_base = 0.3

            # Strong correlation with zone visitor activity
            tree_influence = self.tree_movement_intensity * 0.2
            visitor_influence = min(0.6, zone_visitors * 0.2)  # Visitors cause bright response
            total_intensity = min(1.0, time_base + tree_influence + visitor_influence)

            # Base colors per zone with visitor-responsive brightness
            if zone_id == "riverside":
                # Tons bleus-verts - brighter when visitors present
                base_red, base_green, base_blue = 50, 150, 200
                visitor_red_boost = zone_visitors * 30
                visitor_green_boost = zone_visitors * 25
                visitor_blue_boost = zone_visitors * 15
            elif zone_id == "deep_forest":
                # Tons verts mystiques
                base_red, base_green, base_blue = 80, 180, 30
                visitor_red_boost = zone_visitors * 20
                visitor_green_boost = zone_visitors * 25
                visitor_blue_boost = zone_visitors * 35
            else:  # entrance_clearing
                # Tons blancs chauds
                base_red, base_green, base_blue = 200, 180, 120
                visitor_red_boost = zone_visitors * 15
                visitor_green_boost = zone_visitors * 15
                visitor_blue_boost = zone_visitors * 25

            # Apply tree movement and visitor boosts
            red = base_red + (self.tree_movement_intensity * 50) + visitor_red_boost
            green = base_green + (self.tree_movement_intensity * 40) + visitor_green_boost
            blue = base_blue + (self.tree_movement_intensity * 35) + visitor_blue_boost

            # Apply total intensity and clamp
            red = max(0, min(255, int(red * total_intensity)))
            green = max(0, min(255, int(green * total_intensity)))
            blue = max(0, min(255, int(blue * total_intensity)))

            reading = LightingSystem(
                timestamp=self.get_current_timestamp(),
                led_id=led_id,
                zone=zone_id,
                red_intensity=red,
                green_intensity=green,
                blue_intensity=blue
            )
            readings.append(reading)

        return readings
    
    def calculate_user_engagement(self, visitor_data: List[VisitorDetection]) -> List[UserEngagement]:
        """Calculates engagement metrics per zone"""
        readings = []
        
        for zone_id in self.zones.keys():
            # Filter visitor data for this zone
            zone_visitors = [v for v in visitor_data if v.zone == zone_id and v.detection_active]
            
            if zone_visitors:
                # Simulate engagement duration based on confidence
                avg_confidence = sum(v.confidence_level for v in zone_visitors) / len(zone_visitors)
                duration = max(5, (avg_confidence / 100) * 300)  # 5-300 seconds
                engagement_score = min(1.0, avg_confidence / 100)
            else:
                duration = 0
                engagement_score = 0.0
                
            # Stocker l'historique pour calculs futurs
            self.engagement_history[zone_id].append(engagement_score)
            if len(self.engagement_history[zone_id]) > 10:
                self.engagement_history[zone_id].pop(0)
            
            reading = UserEngagement(
                timestamp=self.get_current_timestamp(),
                zone=zone_id,
                average_engagement_duration_sec=round(duration, 1),
                engagement_score=round(engagement_score, 3)
            )
            readings.append(reading)
            
        return readings
    
    def generate_complete_dataset(self) -> Dict:
        """Generates a complete dataset for a given timestamp"""
        
        # 1. Weather conditions
        environmental_data = self.simulate_weather_conditions()
        
        # 2. Tree biometrics
        tree_data = self.simulate_tree_biometrics()
        
        # 3. Visitor detection
        visitor_data = self.simulate_visitor_detection()
        
        # 4. Engagement utilisateur (calculated from visitor data)
        engagement_data = self.calculate_user_engagement(visitor_data)
        
        # 5. Audio system (reacts to trees and visitors)
        audio_data = self.simulate_audio_system()
        
        # 6. Lighting system (reacts to everything)
        lighting_data = self.simulate_lighting_system()
        
        # Calcul de la puissance totale
        audio_power = len(audio_data) * 30  # ~30W per speaker
        lighting_power = sum((r.red_intensity + r.green_intensity + r.blue_intensity) / 3 * 0.2 for r in lighting_data)
        self.stats["total_power_consumption"] = round(audio_power + lighting_power + 100, 1)  # +100W base
        
        return {
            "metadata": {
                "timestamp": self.get_current_timestamp(),
                "simulation_time": str(self.current_time),
                "stats": self.stats.copy(),
                "user_engagement": [asdict(reading) for reading in engagement_data]
            },
            "environmental": [asdict(reading) for reading in environmental_data],
            "tree_biometrics": [asdict(reading) for reading in tree_data],
            "visitor_detection": [asdict(reading) for reading in visitor_data],
            "audio_system": [asdict(reading) for reading in audio_data],
            "lighting_system": [asdict(reading) for reading in lighting_data]
        }
    
    def print_live_stats(self):
        """Displays real-time installation statistics"""
        print(f"\n Installation Live Stats - {self.current_time.strftime('%H:%M:%S')}")
        print(f"   Visitors detected: {self.stats['total_visitors_detected']}")
        print(f"   Tree movement intensity: {self.stats['average_tree_movement']:.3f}")
        print(f"   Total power consumption: {self.stats['total_power_consumption']:.1f}W")


async def run_realtime_simulation(simulator: InstallationSim, 
                                 interval_seconds: int = 30,
                                 output_file: Optional[str] = None,
                                 live_display: bool = True):
    """Continuous real-time simulation"""

    print(f"   Installation - REAL-TIME MONITORING (Light Version)")
    print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Update interval: {interval_seconds}s")
    print(f"   Press Ctrl+C to stop")
    print("=" * 60)
    
    datasets = []
    start_real_time = time.time()
    iterations = 0
    
    try:
        while True:
            iteration_start = time.time()
            
            # Simulation time follows real time
            simulator.current_time = datetime.now(timezone.utc)
            
            # Complete dataset generation
            dataset = simulator.generate_complete_dataset()
            
            # Memory save (keep only last 10)
            datasets.append(dataset)
            if len(datasets) > 10:
                datasets.pop(0)
            
            # Real-time display
            if live_display and (iterations % 1 == 0):
                print(f"\n--- Iteration {iterations + 1} ---")
                simulator.print_live_stats()
                print(f"Data points this cycle: {sum(len(v) if isinstance(v, list) else 1 for k, v in dataset.items() if k != 'metadata')}")
            
            # Periodic JSON save
            if output_file and iterations % 10 == 9:
                backup_file = f"{output_file}_backup.json"
                with open(backup_file, 'w') as f:
                    json.dump({
                        "last_update": simulator.get_current_timestamp(),
                        "runtime_seconds": time.time() - start_real_time,
                        "total_iterations": iterations + 1,
                        "recent_datasets": datasets[-5:]  # 5 derniers points
                    }, f, indent=2)
            
            iterations += 1
            
            # Precise timing to respect interval
            iteration_time = time.time() - iteration_start
            sleep_time = max(0.1, interval_seconds - iteration_time)
            await asyncio.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print(f"\n\n[INFO] Real-time simulation stopped by user")
        print(f"   Total runtime: {time.time() - start_real_time:.1f}s")
        print(f"   Total iterations: {iterations}")
        
        # Sauvegarde finale
        if output_file and datasets:
            final_file = f"{output_file}_final.json"
            with open(final_file, 'w') as f:
                json.dump({
                    "session_info": {
                        "start_time": start_real_time,
                        "end_time": time.time(),
                        "total_iterations": iterations,
                        "final_stats": simulator.stats
                    },
                    "recent_data": datasets[-5:]
                }, f, indent=2)
            print(f"[INFO] Session data saved to: {final_file}")


def run_single_snapshot(simulator: InstallationSim,
                       output_file: Optional[str] = None):
    """Generates a single data snapshot"""
    
    print(f"  Generating single snapshot at {simulator.current_time}")
    
    dataset = simulator.generate_complete_dataset()
    simulator.print_live_stats()
    
    # Calcul du nombre total de points
    total_points = sum(len(v) if isinstance(v, list) else 1 for k, v in dataset.items() if k != 'metadata')
    print(f"\n Data Summary:")
    print(f"   Environmental: {len(dataset['environmental'])} readings")
    print(f"   Tree Biometrics: {len(dataset['tree_biometrics'])} readings")
    print(f"   Visitor Detection: {len(dataset['visitor_detection'])} readings")
    print(f"   Audio System: {len(dataset['audio_system'])} readings")
    print(f"   Lighting System: {len(dataset['lighting_system'])} readings")
    print(f"   User Engagement: {len(dataset['metadata']['user_engagement'])} analytics (in metadata)")
    print(f"   Total data points: {total_points}")
    
    if output_file:
        with open(f"{output_file}_snapshot.json", 'w') as f:
            json.dump(dataset, f, indent=2)
        print(f"[INFO] Snapshot saved to {output_file}_snapshot.json")
    
    return dataset


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Forest Interactive Installation - Data Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard real-time mode (data every 30s)
  python installation_sim_light.py
  
  # Fast real-time mode (data every 10s) 
  python installation_sim_light.py --interval 10
  
  # Real-time mode with logging
  python installation_sim_light.py --output forest_logs --interval 20
  
  # Un seul snapshot pour test
  python installation_sim_light.py --snapshot --output test_data
        """
    )
    
    parser.add_argument('--interval', type=int, default=30,
                       help='Interval between measurements in seconds (default: 30)')
    parser.add_argument('--output', type=str, default=None,
                       help='Base name for log files')
    parser.add_argument('--no-display', action='store_true',
                       help='Disable real-time display')
    parser.add_argument('--snapshot', action='store_true',
                       help='Generate single snapshot instead of real-time mode')

    args = parser.parse_args()

    # Initialisation du simulateur
    simulator = InstallationSim()

    # Execution according to mode
    if args.snapshot:
        run_single_snapshot(simulator, args.output)
    else:
        # Default real-time mode
        asyncio.run(run_realtime_simulation(
            simulator=simulator,
            interval_seconds=args.interval,
            output_file=args.output,
            live_display=not args.no_display
        ))


if __name__ == "__main__":
    main()