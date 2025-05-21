import uuid
import random
import math
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
        self.stress = 0.0  # Initialize stress

        # --- Placeholder Graphics ---
        self.emoji = "😊"  # Default emoji

        # --- Internal State for Actions ---
        self.current_action = "idle"
        self.action_timer = 0.0
        self.target_food_pos = None
        self.eating_food_id = None

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

        # Calculate stress
        stress_from_hunger = (self.hunger / 100) * 50
        stress_from_low_energy = ((100 - self.energy) / 100) * 50
        self.stress = stress_from_hunger + stress_from_low_energy
        self.stress = max(0, min(100, self.stress))  # Cap stress between 0 and 100

    def choose_action(self):
        """Decide the next action based on needs (AI Logic Placeholder)."""
        if self.current_action == "dead":
            return

        STRESS_THRESHOLD = 30

        if self.stress > STRESS_THRESHOLD:
            # Prioritize actions based on what contributes most to stress
            # (Simplified: check hunger first, then energy)
            if self.hunger > 60: # Assuming hunger is a major stressor above this
                if self.environment.food_sources:
                    self.current_action = "seeking_food"
                    # Target the first food item
                    target_food = self.environment.food_sources[0]
                    self.target_food_pos = (target_food['x'], target_food['y'])
                else:
                    self.current_action = "idle" # No food, go idle
            elif self.energy < 40: # Assuming low energy is a major stressor below this
                self.current_action = "seeking_sleep"
                # No specific location needed for sleeping yet
            else:
                # Fallback if stress is high but neither hunger nor energy are extreme
                if self.hunger > self.energy: # A simple way to pick one
                    if self.environment.food_sources:
                        self.current_action = "seeking_food"
                        target_food = self.environment.food_sources[0]
                        self.target_food_pos = (target_food['x'], target_food['y'])
                    else:
                        self.current_action = "idle" # No food, go idle
                else:
                     self.current_action = "seeking_sleep"
                     # No specific location needed for sleeping yet
        else:
            # Default to wandering or idle if stress is low
            if self.current_action == "idle" or self.current_action == "wandering":
                if random.random() < 0.1:  # Chance to start wandering
                    self.current_action = "wandering"
                    self.action_timer = random.uniform(
                        1.0, 5.0)  # Wander for 1-5 secs
                    # TODO: Set a random target direction/position within bounds
                else:
                    self.current_action = "idle"
            elif self.current_action not in ["seeking_food", "seeking_sleep"]: # if it was doing something else, make it idle.
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
        
        elif self.current_action == "seeking_food":
            if self.target_food_pos:
                dx = self.target_food_pos[0] - self.x
                dy = self.target_food_pos[1] - self.y
                dist = math.sqrt(dx*dx + dy*dy)

                move_dist_this_frame = self.move_speed * time_delta

                if dist <= move_dist_this_frame or dist < 5: # Close enough or within 5 units
                    self.current_action = "eating"
                    self.action_timer = 2.0 # Eat for 2 seconds
                    # Assuming the target food is still the first one and available
                    # This needs to be more robust if food can disappear or multiple bitlings compete
                    if self.environment.food_sources:
                         self.eating_food_id = self.environment.food_sources[0]['id'] # Store ID
                    self.target_food_pos = None
                    self.emoji = "😋"
                else:
                    # Move towards target
                    self.x += (dx / dist) * move_dist_this_frame
                    self.y += (dy / dist) * move_dist_this_frame
                    # Clamp position
                    self.x = max(0, min(self.environment.width, self.x))
                    self.y = max(0, min(self.environment.height, self.y))
                    self.energy = max(0, self.energy - 1.5 * time_delta) # More energy for targeted movement
                    self.emoji = "🤔" # Thinking about food
            else:
                self.current_action = "idle" # No target

        elif self.current_action == "eating":
            if self.action_timer > 0:
                pass # Still eating
            else:
                self.hunger = max(0, self.hunger - 50) # Reduce hunger
                if self.eating_food_id:
                    self.environment.food_sources = [
                        food for food in self.environment.food_sources
                        if food['id'] != self.eating_food_id
                    ]
                    self.eating_food_id = None # Clear food ID
                self.current_action = "idle"
                # Emoji will be updated in update_passive

        elif self.current_action == "seeking_sleep":
            self.current_action = "sleeping"
            self.action_timer = random.uniform(5.0, 10.0) # Sleep for 5-10 seconds
            self.emoji = "😴"

        elif self.current_action == "sleeping":
            if self.action_timer > 0:
                self.energy = min(100, self.energy + 10 * time_delta) # Gradual energy restore
            else:
                self.energy = 100 # Fully restore energy
                self.current_action = "idle"
                # Emoji will be updated in update_passive based on new energy

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
            "stress": round(self.stress),
        }
