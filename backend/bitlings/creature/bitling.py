import uuid
import random
import math
from typing import Dict, Any
from backend.bitlings.ai.network import BitlingNetwork # Added BitlingNetwork import


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

        # --- AI Network ---
        self.network = BitlingNetwork()
        self.action_chosen_by_network_for_learning = None # For learning

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
        """Decide the next action using the BitlingNetwork."""
        if self.current_action == "dead":
            return

        # Determine food_nearby status
        food_nearby = bool(self.environment.food_sources) # True if list is not empty

        # Set network inputs
        self.network.set_inputs(self.hunger, self.energy, food_nearby)

        # Settle the network
        self.network.settle() # Using default iterations

        # Get chosen action from the network
        chosen_action = self.network.get_chosen_action()
        self.current_action = chosen_action
        self.action_chosen_by_network_for_learning = chosen_action # Store for learning

        # Handle actions that require specific setup
        if chosen_action == "seeking_food":
            if self.environment.food_sources:
                # Target the first available food source
                target_food = self.environment.food_sources[0]
                self.target_food_pos = (target_food['x'], target_food['y'])
                # self.eating_food_id = target_food['id'] # Deferred to execute_action's transition to "eating"
            else:
                # Network chose to seek food, but none is available
                self.current_action = "idle" # Default to idle to prevent errors
                self.target_food_pos = None # Ensure no stale target

        elif chosen_action == "eating":
            # This action is problematic if chosen directly by the network without
            # the Bitling being at a food source. execute_action for 'eating'
            # relies on self.eating_food_id being set, which happens when
            # 'seeking_food' transitions to 'eating'.
            # If not already at food (e.g. target_food_pos is None or not close enough)
            # it might be best to switch to idle or re-evaluate.
            # For now, we rely on execute_action to handle this potentially awkward state.
            # A simple patch for now if not already in the process of eating:
            if not self.eating_food_id and not self.target_food_pos: # if not already eating or seeking
                # Check if Bitling is *at* a food source to allow "eating"
                is_at_food = False
                if self.environment.food_sources:
                    for food_item in self.environment.food_sources:
                        dist_sq = (self.x - food_item['x'])**2 + (self.y - food_item['y'])**2
                        if dist_sq < 5**2: # Within 5 units (squared comparison)
                            self.eating_food_id = food_item['id']
                            is_at_food = True
                            break
                if not is_at_food:
                    self.current_action = "idle" # Not at food, cannot eat. Go idle.


        elif chosen_action == "seeking_sleep":
            # execute_action handles the transition to "sleeping" and sets action_timer
            pass

        elif chosen_action == "wandering":
            self.action_timer = random.uniform(1.0, 5.0) # Set wander duration
            # execute_action will handle movement if current_action is "wandering"
            # and action_timer > 0

        elif chosen_action == "idle":
            # No special setup needed for idle
            pass
        
        # Any other actions from the network that don't have specific setup
        # will just be set as current_action and execute_action will try to run them.
        # If they are not defined in execute_action, they will do nothing.

    def execute_action(self, time_delta: float):
        """Perform the current action."""
        if self.current_action == "dead":
            return

        stress_before_action = self.stress

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
                
                self.update_passive(time_delta=0) # Update stress based on new hunger
                stress_after_action = self.stress
                was_successful = stress_after_action < stress_before_action

                action_to_reinforce_name = self.action_chosen_by_network_for_learning
                if action_to_reinforce_name in self.network.output_names:
                    action_index = self.network.output_names.index(action_to_reinforce_name)
                    self.network.apply_learning(action_index, was_successful)
                
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
                
                self.update_passive(time_delta=0) # Update stress based on new energy
                stress_after_action = self.stress
                was_successful = stress_after_action < stress_before_action

                action_to_reinforce_name = self.action_chosen_by_network_for_learning
                # "seeking_sleep" is the action the network chooses.
                # We check if this choice led to successful sleep (energy restoration).
                if action_to_reinforce_name == "seeking_sleep":
                    # Find the index for "seeking_sleep" to reinforce that choice
                    if "seeking_sleep" in self.network.output_names:
                        action_index = self.network.output_names.index("seeking_sleep")
                        self.network.apply_learning(action_index, was_successful)
                
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
