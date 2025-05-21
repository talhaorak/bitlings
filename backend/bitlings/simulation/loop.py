# src/simulation/loop.py
import asyncio
import time
import json
import logging
from typing import Set, Any
import websockets  # To handle potential connection errors

from .environment import Environment

logger = logging.getLogger(__name__)


class Simulation:
    """Runs the main simulation loop and processes user actions."""

    def __init__(self, environment: Environment, action_queue: asyncio.Queue, network_server):
        self.environment = environment
        self.action_queue = action_queue
        self.network_server = network_server
        self.last_tick_time = time.monotonic()

    async def run(self, tick_interval: float):
        """The main simulation loop."""
        logger.info("Simulation loop started.")
        while True:
            current_time = time.monotonic()
            time_delta = current_time - self.last_tick_time
            self.last_tick_time = current_time

            # 1. Process user actions
            await self.process_actions()

            # 2. Update Environment State
            self.environment.update(time_delta)

            # 3. Update all Bitlings
            for bitling in self.environment.bitlings:
                bitling.update_passive(time_delta)
                bitling.choose_action()  # Decide what to do
                bitling.execute_action(time_delta)  # Do it

            # 4. Broadcast state to connected clients
            await self.network_server.broadcast_state(self.environment.get_state())

            # 5. Wait for the next tick
            await asyncio.sleep(tick_interval)

    async def process_actions(self):
        """Process all pending user actions from the queue."""
        while not self.action_queue.empty():
            action_item = await self.action_queue.get()
            action = action_item.get("action")
            # Example: handle add_food action
            if action.get("action") == "add_food":
                x = action.get("x")
                y = action.get("y")
                self.environment.add_food({
                    "emoji": "🍎",
                    "x": x,
                    "y": y
                })
                logger.info(f"Processed add_food action at ({x}, {y})")
            # Add more action types as needed
