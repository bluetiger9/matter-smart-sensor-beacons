import asyncio
import websockets
import json
import os
import datetime
from influxdb_client import InfluxDBClient
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

class WebSocket:
    def __init__(self, uri, callback):
        self.uri = uri
        self.callback = callback
        self.websocket = None        

    async def on_message(self, message):
        try:
            data = json.loads(message)            
            if 'results' in data:
                for result in data['results']:
                    print("RESULT: {}".format(result))
                    self.callback(result['value'])

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON message: {e}")

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        print(f"Connected to {self.uri}")

        # Start receive loop
        async def receive_messages():
            while True:
                try:
                    message = await self.websocket.recv()
                    await self.on_message(message)
                except websockets.ConnectionClosed:
                    print("WebSocket connection closed.")
                    break

        # Create a task for receiving messages in the background
        self.receive_task = asyncio.ensure_future(receive_messages())

    async def send(self, message):
        if self.websocket:
            await self.websocket.send(message)
            print(f"Sent message: {message}")
        else:
            print("WebSocket not connected. Cannot send message.")

    async def close(self):
        if self.websocket:
            await self.websocket.close()
        if hasattr(self, 'receive_task'):
            await self.receive_task

# main function (async)
async def main(chip_tool_ws_url, influx_db_url, node_id, endpoint_id, cluster_name, attribute_name, metric, divide, count):
    # Influx DB connection
    influx = InfluxDBClient(influx_db_url, token=os.environ.get('INFLUX_TOKEN'), org="none")
    influx_write = influx.write_api(write_options=SYNCHRONOUS)

    # callback for received values
    def callback(value):
        point = Point(f"{metric}") \
            .tag("device", f"node-{node_id}") \
            .field(f"{metric}", value / divide) \
            .time(datetime.datetime.utcnow())
        
        print(f"Sending Influx metric: {point}")

        try:
            response = influx_write.write(bucket = "bucket", record = point)
            print(f" \--> response: {response}")

        except ex:
            print(f"Sending Influx metric failed: {ex}")

    # WebSocket connection
    ws = WebSocket(chip_tool_ws_url, callback)
    await ws.connect()

    # main loop (async)
    for nr in range(0, count):
        message_to_send = f"{cluster_name} read {attribute_name} {node_id} {endpoint_id} --timeout 2"
        await ws.send(message_to_send)

        # Perform more actions if needed
        await asyncio.sleep(5)

    # Close the WebSocket connection
    await ws.close()

# Run the WebSocket client
if __name__ == "__main__":

    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--chip-tool-ws-url", help="CHIP Tool WebSocket URL", type=str, default="ws://localhost:9002/")
    parser.add_argument("--influx-db-url", help="InfluxDB URL", type=str, default="http://localhost:8086")
    parser.add_argument("--node-id", help="Matter Node ID", type=str, default="1")
    parser.add_argument("--endpoint-id", help="Matter Endpoint ID", type=str, default="1")
    parser.add_argument("--cluster-name", help="Matter Cluster Name", type=str, default="temperaturemeasurement")
    parser.add_argument("--attribute-name", help="Matter Attribute Name", type=str, default="measured-value")
    parser.add_argument("--metric", help="InfluxDB Metric Name", type=str, default="temperature")
    parser.add_argument("--divide", help="Divide int value to get a float", type=float, default="1.0")
    parser.add_argument("--count", help="Number of samples to collect", type=int, default="1")

    args = parser.parse_args()
    
    print(f"Parser: {args}")

    # run the AsyncIO event loop
    asyncio.get_event_loop().run_until_complete(main(args.chip_tool_ws_url, args.influx_db_url, args.node_id, args.endpoint_id, args.cluster_name, args.attribute_name, args.metric, args.divide, args.count))
