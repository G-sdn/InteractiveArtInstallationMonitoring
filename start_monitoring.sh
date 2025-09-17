#!/bin/bash
# Interactive Installation - Monitoring System Startup
# =========================================================

echo "Starting Interactive Installation Monitoring..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if a process is running
check_process() {
    local name=$1
    local pattern=$2
    if pgrep -f "$pattern" > /dev/null; then
        echo "[INFO] $name is already running"
        return 0
    else
        echo "[NOT RUNNING] $name is not running"
        return 1
    fi
}

# Start process with terminal output
start_foreground() {
    local name=$1
    local command=$2

    echo "[STARTING] $name..."
    echo "[INFO] Running: $command"
    echo "[INFO] Press Ctrl+C to stop all processes"
    echo "----------------------------------------"

    exec $command
}

echo ""
echo "[INFO] Checking current status..."

# Check if components are already running
check_process "Installation Simulator" "python.*installation_sim"
SIMULATOR_RUNNING=$?

check_process "InfluxDB Bridge" "python.*influx_bridge"
BRIDGE_RUNNING=$?

check_process "Telegraf" "telegraf.*telegraf.conf"
TELEGRAF_RUNNING=$?

echo ""
echo "[INFO] Starting monitoring components..."
echo "[INFO] This will show all output in the terminal"
echo "[INFO] Use Ctrl+C to stop the monitoring system"
echo ""

# Check if components are already running
if [ $BRIDGE_RUNNING -eq 0 ]; then
    echo "[WARNING] InfluxDB Bridge is already running!"
    echo "[INFO] Use 'pkill -f influx_bridge' to stop it first"
    exit 1
fi

if [ $TELEGRAF_RUNNING -eq 0 ]; then
    echo "[WARNING] Telegraf is already running!"
    echo "[INFO] Use 'pkill -f telegraf' to stop it first"
    exit 1
fi

# Start Telegraf in background with visible output
echo "[STARTING] Telegraf System Metrics..."
telegraf --config telegraf/telegraf.conf &
TELEGRAF_PID=$!
echo "   Telegraf PID: $TELEGRAF_PID"

# Give Telegraf a moment to start
sleep 2

# Start InfluxDB Bridge
start_foreground "InfluxDB Bridge" \
    "python influx_bridge.py --simulator-api --interval 5"

# This line should never be reached due to exec in start_foreground
echo "[ERROR] Unexpected script continuation - bridge may have failed to start"