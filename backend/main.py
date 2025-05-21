import asyncio
import logging
import websockets

from bitlings.simulation.environment import Environment
from bitlings.simulation.loop import Simulation
from bitlings.network.server import NetworkServer

logging.basicConfig(level=logging.INFO)


async def main():
    # 1. Create the environment
    environment = Environment(width=1000, height=1000)

    # 2. Create the action queue
    action_queue = asyncio.Queue()

    # 3. Create the network server
    network_server = NetworkServer(action_queue)

    # 4. Create the simulation
    simulation = Simulation(environment, action_queue, network_server)

    # 5. Start the websocket server
    ws_server = await websockets.serve(network_server.handler, "0.0.0.0", 8765)
    logging.info("WebSocket server started on ws://0.0.0.0:8765")

    # 6. Start the simulation loop
    simulation_task = asyncio.create_task(simulation.run(tick_interval=0.1))

    # 7. Run forever
    try:
        await simulation_task
    finally:
        ws_server.close()
        await ws_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
