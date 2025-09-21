# Imagine this:
You’re having a stroll in the forest when a slight breeze picks up. You hear what you think, at first, is the rustling of leaves, but the rather soothing sound keeps building up. It grows to become what’s clearly no longer simply the trees but a more abstract, ambiant tone reminiscent of your favorite Chill & Ambient Brian Eno spotify playlist. All the while, individual LED pixels start shimmering, casting gentle glows against bark and branches.

These types of outdoor interactive experiences have grown in popularity over the last decades, enabled by democratization of technological means, open-source hardware platforms, and increasingly sophisticated yet accessible IoT ecosystems. Despite their diverse artistic expressions or technical complexity, these installations follow a consistent pattern: they sense the world around them, interpret that data through creative algorithms, and respond with generated audio, lighting, or visual elements that create a feedback loop between them and human presence.

Like any other distributed system, these art installations can profit considerably from real-time monitoring. When a sensor fails in a warehouse, you might lose some data points. When a sensor fails in an interactive forest installation at midnight, the charm is lost—trees sway silently, visitors wave at unresponsive lights, grow frustrated, and the carefully crafted relationship between nature and technology dissolves. 

This article demonstrates a monitoring architecture using InfluxDB and Grafana that addresses both the artistic and technical requirements of interactive installations. We'll build a system that captures over 200 data points every 5 seconds, correlates environmental inputs with creative outputs, and provides actionable insights for both artistic optimization, ongoing troubleshooting and predictive maintenance.

# Hypothetical Interactive Installation
To illustrate these challenges, let’s examine a hypothetical installation in a forest:
## Components

    • 3 “zones”: 
        ◦ Entrance clearing
        ◦ Deep forest
        ◦ Riverside
    • Each zone is equipped with:
        ◦ 5 proximity sensors
        ◦ 9 trees with strain gauge sensors and accelerometers
        ◦ Speakers
        ◦ LEDs
        ◦ A weather station
        ◦ A Raspberry Pi or microcontroller acting as a hub to the main control PC
    • An outdoor rack enclosure to house our PC, network gear, power distribution and so on.
    • A LAN network to connect it all
    • A remote server hosting InfluxDB and Grafana
We’re keeping this relatively contained for simplicity, but once we have the infrastructure down, our system could easily scale up or down.

Here’s what that might look like:

```
┌─────────────────┬─────────────────┬─────────────────┐         Data flow:
│  ENTRANCE       │  DEEP FOREST    │  RIVERSIDE      │         [Sensors + A/V devices] → [Zone Hubs] → [Control PC + Telegraf] → Server w/ InfluxDB → Grafana
│  CLEARING       │                 │                 │                                        ↓                    |                      ↓              |
├─────────────────┼─────────────────┼─────────────────┤                             (RPi/microcontrollers)          |               (Ubuntu/Docker)       |
│ 9 trees         │ 9 trees         │ 9 trees         │                                                             ↓                                     ↓
│ 5 LiDAR sensors │ 5 LiDAR sensors │ 5 LiDAR sensors │                                       (Windows w/ installation control software)      (Data viz/Monitoring/Alerts)
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
# Guide
## Prerequesites
Before diving in, you'll need:
    
    • Python 3.10+ for the simulation scripts 
    • Docker and/or Docker Compose for InfluxDB/Grafana. There are many ways of installing both these apps. We find it simpler in this context to work with Docker. You can follow this guide for getting InfluxDB up and running and this guide for Grafana.
    • Telegraf for system metrics collection.

## Install and setup
### Docker and python setup
Clone and enter the project directory
```
git clone https://github.com/G-sdn/InteractiveArtInstallationMonitoring
cd InteractiveArtInstallationMonitoring
``` 
Create and activate a Python virtual environment, then install dependencies: 
``` 
python -m venv venv
source venv/bin/activate 
pip install influxdb-client numpy watchdog
```  

If you don't have existing instances, spin them up with Docker:
```
# docker-compose.yml
version: '3'
services:
  influxdb:
    image: influxdb:latest
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=changeme123
      - DOCKER_INFLUXDB_INIT_ORG=interactiveInstallation
      - DOCKER_INFLUXDB_INIT_BUCKET=installations  # Primary bucket
      # Note: Create system-metrics bucket via UI or API after initialization
    volumes:
      - influxdb-storage:/var/lib/influxdb2
      - influxdb-config:/etc/influxdb2

  grafana:
    image: grafana/grafana-oss:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana-storage:/var/lib/grafana
      - grafana-config:/etc/grafana
    depends_on:
      - influxdb

volumes:
  influxdb-storage:
  grafana-storage:
  influxdb-config:
  grafana-config:
```
Start the services: `docker-compose up -d`

### Check that InfluxDB is running and create your API Key
1. Head over to http://localhost:8086, if everything is working you should land on the InfluxDB login page.
2. Once logged in with the credentials you setup in the docker compose config file, navigate to **Load Data/API Tokens**
3. Under **Generate API Token**, select **All Access API Token**. Enter a description and hit **Save**.
4. Make sure to copy the API token in the pop-up.

### Creating Additional Buckets
After InfluxDB starts, create the system-metrics bucket:
1. Navigate to Data → Buckets
2. Click "Create Bucket"
3. Name it "system-metrics" with desired retention

You're all done with install and setup!

## Data Bridge
The data bridge script gathers the data from the installation and sends it to your InfluxDB instance using the python influxdb-client library. It does exactly what it's called, it *bridges* between these two instances. This code could also be written directly into your application, but we prefer to keep these decoupled to seperate concerns between data source and data pipeline. This makes it easier to transition from testing and development to production, to troubleshoot and gives you a reusable component for future projects.

Code comments in the influx_bridge.py script explain what each section does. You can also follow the [InfluxDB guide](https://docs.influxdata.com/influxdb/v2/api-guide/client-libraries/python/) for more information on setting up the python client library.

### Configuring the Data Bridge
Update influx_bridge.py with your connection details:
```
@dataclass
class InfluxDBConfig:
    url: str = "http://localhost:8086"  # Or your remote InfluxDB URL
    token: str = "your-influxdb-token"   # InfluxDB API Token from previous step
    org: str = "interactiveInstallation" 
    bucket: str = "installations"
```

## System metrics with Telegraf

While our Python data bridge handles artistic data from the installation (visitor engagement, tree movement, audio responses), Telegraf takes care of infrastructure and system monitoring. Telegraf is InfluxData's native data collection agent, designed specifically for gathering system metrics and sending them to InfluxDB.

### Why Telegraf Instead of Python?
First, we wanted to show different ways of writing data to InfluxDB. We could write Python scripts to collect system metrics in our data bridge script, but Telegraf offers several advantages such as pre-built plugins for things such as system stats and requires less code.

Code comments in the telegraf config explain what each section does. You can also follow the [InfluxDB Telegraf documentation](https://docs.influxdata.com/telegraf/v1/get-started/) for more information on setting up the config file.

### Configuring Telegraf
Just like with our data bridge, we need to adjust our connection details in the telegraf config file.

```
# =============================================================================
# GLOBAL SETTINGS
# =============================================================================
# Global tags are added to every metric collected by this Telegraf instance
[global_tags]
  installation = "interactive_installation"  # Identifies our specific installation
  environment = "production"  # Environment type (dev/staging/production)

...

# =============================================================================
# OUTPUT PLUGINS
# =============================================================================
# Define where collected metrics are sent

# InfluxDB v2 output - sends metrics to time-series database
[[outputs.influxdb_v2]]
  urls = ["http://localhost:8086"]  # InfluxDB instance endpoint
  token = "your-influxdb-token"
  organization = "interactiveInstallation"
  bucket = "system_metrics"
```

## Running the System
Start all components with a single command:

```
# Make the startup script executable (On Windows, skip this step)
chmod +x start_monitoring.sh

# Launch everything using the bash script
./start_monitoring.sh
```
Or run components individually for debugging:
```
# Terminal 1: Start the installation simulator
python installation_sim.py --interval 30

# Terminal 2: Start the InfluxDB bridge
python influx_bridge.py --simulator-api --interval 5

# Terminal 3: Start Telegraf
telegraf --config telegraf.conf
```

## Verifying the Data Pipeline

Check that data is flowing correctly:
```bash
# Test InfluxDB connection
python influx_test.py

# Query recent installation data
curl -G 'http://localhost:8086/api/v2/query' \
  -H "Authorization: Token your-token" \
  -H "org: interactiveInstallation" \
  --data-urlencode 'fluxQuery=from(bucket:"installations") 
    |> range(start: -5m) 
    |> limit(n:10)'
```
You should see:

1. Installation Simulator: Console output showing generated data
2. InfluxDB Bridge: Logs confirming successful writes
3. Telegraf: System metrics being collected

## Data visualization with Grafana
### Grafana Setup

1. Open Grafana at http://localhost:3000 
2. If the docker instance was correctly setup, you should be greeted with a login page. Default credentials should be **admin**/**admin**.
3. Open the menu by clicking on the Grafana logo on the top left corner.
4. Under **Connections**, select **Data sources**.
5. Add a new data source for each bucket. In our case we need one for *installation* and one for *system-metrics*
6. In the data source settings page:
   1. Select **Flux** as the query language
   2. Enter your InfluxDB instance url
   3. Under *InfluxDB Details*, fill the **Organization**, **API Token** and **Default Bucket** information.
   4. Click **Save & test**

Your Grafana instance should now be connected with your InfluxDB instance.

### Import the Grafana dashboard:

1. Under **Dashboards**, create a new dashboard by clicking the **+** sign beside the search bar.
2. Select **Import dashboard**.
3. Copy and paste or upload the grafana_dashboard.json file.
4. Click **load**.

Make sure the simulation instance is running and adjust the time window according to how long it has been running.

You should now see a dashboard displaying some data from the installation simulation.

## Taking It Further

- **Add alerting rules**: This is the obvious next step. With data now being monitored in realtime you could set up alerts with InfluxDB to be informed of any hardware issues, irregularities, and so on. 
- **Integrate with creative software**: You could also decide to further integrate InfluxDB with the software used to process the interactive installation, be it something like TouchDesigner or Max/MSP for real-time parameter adjustment.