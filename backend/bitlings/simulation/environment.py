import uuid
import random
from typing import List, Dict, Any
# Assuming creature.py is in bitlings folder
from bitlings.creature.bitling import Bitling


class Environment:
    """Manages the simulation world state."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.bitlings: List[Bitling] = []
        # Example: {'id': uuid, 'x': float, 'y': float, 'emoji': '🍎'}
        self.food_sources: List[Dict[str, Any]] = []

        # --- Populate initial state ---
        self.add_initial_creatures(5)
        self.add_initial_food(10)

    def add_bitling(self, bitling: Bitling):
        self.bitlings.append(bitling)

    def add_food(self, food: Dict[str, Any]):
        """Add food to the environment."""
        # if id is not provided, generate a new one
        if 'id' not in food:
            food['id'] = str(uuid.uuid4())

        # if coordinates are not provided, generate random ones
        if 'x' not in food or 'y' not in food:
            food['x'] = random.uniform(0, self.width)
            food['y'] = random.uniform(0, self.height)

        self.food_sources.append(food)

    def add_initial_creatures(self, count: int):
        for _ in range(count):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            # Pass self (the environment) to the Bitling
            creature = Bitling(x=x, y=y, environment=self)
            self.add_bitling(creature)

    def add_initial_food(self, count: int):
        for _ in range(count):
            self.add_food({
                'emoji': '🍎',
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height)
            })

    def update(self, time_delta: float):
        """Update environment state (e.g., food spawning/decaying)."""
        # Remove dead bitlings
        self.bitlings = [b for b in self.bitlings if b.health > 0]
        # TODO: Add logic for food spawning, object interactions etc.

    def get_state(self) -> Dict[str, Any]:
        """Return the environment state for serialization."""
        return {
            "bitlings": [b.get_state() for b in self.bitlings],
            "food": self.food_sources,
            # Add other environment objects later (trees, rocks, etc.)
        }
