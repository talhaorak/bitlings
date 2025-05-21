import uuid
import random
from typing import Dict, Any


class Bitling:
    """Represents a single Bitling creature."""

    def __init__(self, x: float, y: float, environment):
        self.id = str(uuid.uuid4())
        self.x = x
        self.y = y
        self.environment = environment  # Reference to the world it lives in

        # --- Core Attributes ---
        self.health = 100
        self.hunger = random.randint(0, 50)  # Start slightly hungry
        self.energy = random.randint(80, 100)  # Start mostly energetic
        self.mood = 50  # Neutral
        self.age = 0

        # --- Placeholder Graphics ---
        self.emoji = "😊"  # Default emoji

        # --- Internal State for Actions ---
        self.current_action = "idle"
        self.action_timer = 0.0

        # --- Hardcoded speeds for now ---
        self.move_speed = 50.0  # Units per second

    def update_passive(self, time_delta: float):
        """Update needs and passive states over time."""
        self.age += time_delta
        # Hunger increases (faster if active?)
        self.hunger = min(100, self.hunger + 1.0 * time_delta)
        # Energy decreases (faster if active?)
        self.energy = max(0, self.energy - 0.5 * time_delta)

        # Basic mood/health effects (simple thresholds)
        if self.hunger > 80:
            self.mood = max(0, self.mood - 2 * time_delta)
        if self.energy < 20:
            self.mood = max(0, self.mood - 2 * time_delta)
        if self.hunger >= 100:
            self.health = max(0, self.health - 1 * time_delta)

        # Update emoji based on state (simple example)
        if self.hunger > 80:
            self.emoji = "😫"
        elif self.energy < 20:
            self.emoji = "😴"
        elif self.mood < 30:
            self.emoji = "😟"
        elif self.mood > 70:
            self.emoji = "😃"
        else:
            self.emoji = "😊"

        if self.health <= 0:
            self.emoji = "💀"
            self.current_action = "dead"  # Stop further actions

    def choose_action(self):
        """Decide the next action based on needs (AI Logic Placeholder)."""
        if self.current_action == "dead":
            return

        # --- Simple Priority Based Decisions (Pre-training / Hardcoded) ---
        if self.hunger > 70:
            self.current_action = "seeking_food"
            # TODO: Implement logic to find food in environment
        elif self.energy < 30:
            self.current_action = "seeking_sleep"
            # TODO: Implement sleeping logic
        else:
            # Default to wandering
            if self.current_action == "idle" or self.current_action == "wandering":
                if random.random() < 0.1:  # Chance to start wandering
                    self.current_action = "wandering"
                    self.action_timer = random.uniform(
                        1.0, 5.0)  # Wander for 1-5 secs
                    # TODO: Set a random target direction/position within bounds
                else:
                    self.current_action = "idle"

    def execute_action(self, time_delta: float):
        """Perform the current action."""
        if self.current_action == "dead":
            return

        if self.action_timer > 0:
            self.action_timer -= time_delta

        if self.current_action == "idle":
            pass  # Do nothing
        elif self.current_action == "wandering":
            if self.action_timer <= 0:
                self.current_action = "idle"
            else:
                # Basic random movement (replace with pathfinding later)
                move_dist = self.move_speed * time_delta
                self.x += random.uniform(-move_dist, move_dist)
                self.y += random.uniform(-move_dist, move_dist)
                # Clamp position to environment bounds
                self.x = max(0, min(self.environment.width, self.x))
                self.y = max(0, min(self.environment.height, self.y))
                # Consume a bit more energy when moving
                self.energy = max(0, self.energy - 1.0 * time_delta)

        # TODO: Implement execute logic for "seeking_food", "eating", "sleeping" etc.

    def get_state(self) -> Dict[str, Any]:
        """Return the creature's state for serialization."""
        return {
            "id": self.id,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "emoji": self.emoji,
            "action": self.current_action,
            # Optional: send needs for UI display
            "health": round(self.health),
            "hunger": round(self.hunger),
            "energy": round(self.energy),
            "mood": round(self.mood),
        }
