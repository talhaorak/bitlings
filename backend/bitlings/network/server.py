import asyncio
import json
import logging
from typing import Set, Callable, Awaitable, Any
import websockets

logger = logging.getLogger(__name__)


class NetworkServer:
    """Handles WebSocket connections and communication."""

    def __init__(self, action_queue: asyncio.Queue):
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.action_queue = action_queue  # Queue for user actions

    async def handler(self, websocket):
        """Handles a single client connection."""
        logger.info(f"Client connected: {websocket.remote_address}")
        self.connected_clients.add(websocket)
        try:
            # Listen for messages from the client
            async for message in websocket:
                await self.handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosedOK:
            logger.info(
                f"Client {websocket.remote_address} disconnected cleanly.")
        except websockets.exceptions.ConnectionClosedError as e:
            logger.warning(
                f"Client {websocket.remote_address} disconnected with error: {e}")
        except Exception as e:
            logger.error(
                f"Error in handler for {websocket.remote_address}: {e}", exc_info=True)
        finally:
            # Ensure client is removed on disconnect/error
            logger.info(f"Removing client: {websocket.remote_address}")
            self.connected_clients.remove(websocket)

    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Processes incoming messages from a client."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            payload = data.get("payload")
            logger.debug(
                f"Received message type '{message_type}' from {websocket.remote_address}")

            # --- Handle different message types from frontend ---
            if message_type == "user_action":
                # Instead of acting directly, enqueue the action for the simulation
                await self.action_queue.put({
                    "websocket": websocket,
                    "action": payload
                })
                logger.info(f"Enqueued user action: {payload}")

            elif message_type == "ping":
                await websocket.send(json.dumps({"type": "pong"}))

            else:
                logger.warning(
                    f"Received unknown message type: {message_type}")

        except json.JSONDecodeError:
            logger.warning(
                f"Received invalid JSON from {websocket.remote_address}: {message}")
        except Exception as e:
            logger.error(
                f"Error handling message from {websocket.remote_address}: {e}", exc_info=True)

    async def broadcast_state(self, state: Any):
        """Broadcasts the current environment state to all connected clients."""
        if not self.connected_clients:
            return
        message = json.dumps({"type": "world_update", "payload": state})
        tasks = [asyncio.create_task(self.send_to_client(
            client, message)) for client in self.connected_clients]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                client = list(self.connected_clients)[i]
                logger.warning(
                    f"Failed to send state to client {client.remote_address}: {result}")

    async def send_to_client(self, client, message: str):
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosedOK:
            logger.info(
                f"Client {client.remote_address} disconnected cleanly.")
        except websockets.exceptions.ConnectionClosedError as e:
            logger.warning(
                f"Client {client.remote_address} disconnected with error: {e}")
        except Exception as e:
            logger.error(
                f"Error sending message to {client.remote_address}: {e}")
