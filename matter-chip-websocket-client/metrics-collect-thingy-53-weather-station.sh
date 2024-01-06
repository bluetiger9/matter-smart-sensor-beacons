#!/bin/bash

# Collect data in a loop
while true; do 

date

# Temperature
echo "Collecting Temperature measurement..."
python3 chip-tool-ws-client.py \
    --chip-tool-ws-url "${CHIP_TOOL_WS_URL}" \
    --influx-db-url "${INFLUX_DB_URL}" \
    --node-id 55 --endpoint-id 1 \
    --cluster-name temperaturemeasurement --divide 100.0 \
    --metric Temperature \
    --count 1

# Relative Humidity
echo "Collecting Humidity measurement..."
python3 chip-tool-ws-client.py \
    --chip-tool-ws-url "${CHIP_TOOL_WS_URL}" \
    --influx-db-url "${INFLUX_DB_URL}" \
    --node-id 55 --endpoint-id 2 \
    --cluster-name relativehumiditymeasurement --divide 100.0 \
    --metric Humidity \
    --count 1

# Air Pressure
echo "Collecting Air Pressure measurement..."
python3 chip-tool-ws-client.py \
    --chip-tool-ws-url "${CHIP_TOOL_WS_URL}" \
    --influx-db-url "${INFLUX_DB_URL}" \
    --node-id 55 --endpoint-id 3 \
    --cluster-name pressuremeasurement --divide 1.0 \
    --metric Pressure \
    --count 1

# Battery Percentage
echo "Collecting Battery Percentage measurement..."
python3 chip-tool-ws-client.py \
    --chip-tool-ws-url "${CHIP_TOOL_WS_URL}" \
    --influx-db-url "${INFLUX_DB_URL}" \
    --node-id 55 --endpoint-id 0 \
    --cluster-name powersource --divide 2.0 \
    --attribute-name bat-percent-remaining \
    --metric BatteryPercentage \
    --count 1

# Battery Voltage
echo "Collecting Battery Voltage measurement..."
python3 chip-tool-ws-client.py \
    --chip-tool-ws-url "${CHIP_TOOL_WS_URL}" \
    --influx-db-url "${INFLUX_DB_URL}" \
    --node-id 55 --endpoint-id 0 \
    --cluster-name powersource --divide 1000.0 \
    --attribute-name bat-voltage \
    --metric BatteryVoltage \
    --count 1

done