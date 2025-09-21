# test_influx_connection.py
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration (remplacez par vos valeurs)
url = "http://localhost:8086"  # InfluxDB instance endpoint
token = "your-influxdb-token"  # Replace with your actual token
org = "interactiveInstallation"
bucket = "installations"

# Connection test
client = InfluxDBClient(url=url, token=token, org=org)

try:
    # Health test
    health = client.health()
    print(f"[OK] InfluxDB Health: {health.status}")
    
    # Write test
    write_api = client.write_api(write_options=SYNCHRONOUS)
    point = Point("connection_test").field("success", 1.0).tag("location", "server")
    write_api.write(bucket=bucket, record=point)
    print("[OK] Write test: SUCCESS")
    
    # Read test
    query_api = client.query_api()
    query = f'from(bucket:"{bucket}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "connection_test")'
    result = query_api.query(query)
    
    if result:
        print("[OK] Read test: SUCCESS")
        for table in result:
            for record in table.records:
                print(f"   Value: {record.get_value()}")
    else:
        print("[WARNING] Read test: No data found")
        
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
finally:
    client.close()