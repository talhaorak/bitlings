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
        self.target_food_item_id = None # ID of the food item being targeted

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

        # Perceive the environment
        distance, food_dx, food_dy = self.perceive_environment()

        # Set network inputs with new sensory data
        self.network.set_inputs(self.hunger, self.energy, distance, food_dx, food_dy)

        # Settle the network
        self.network.settle() # Using default iterations

        # Get chosen action from the network
        chosen_action = self.network.get_chosen_action()
        self.current_action = chosen_action
        self.action_chosen_by_network_for_learning = chosen_action # Store for learning

        # Handle actions that require specific setup
        if chosen_action == "seeking_food":
            if distance != float('inf') and self.environment.food_sources:
                # Target the first available food source from the list.
                # Note: perceive_environment gives distance/direction to nearest,
                # but for simplicity here, we'll target food_sources[0].
                # A more advanced implementation might ensure target_food_pos
                # aligns with the *perceived* nearest food item's actual coordinates.
                target_food = self.environment.food_sources[0] # Simplified: target the first food item
                self.target_food_pos = (target_food['x'], target_food['y'])
                self.target_food_item_id = target_food['id'] # Store the ID of the targeted food
            else:
                # Network chose to seek food, but no food is perceivable or available
                self.current_action = "idle" 
                self.target_food_pos = None 
                self.target_food_item_id = None # Clear target ID as well

        elif chosen_action == "eating":
            # If the network chooses "eating" directly:
            # - The Bitling should ideally be very close to food (low distance).
            # - execute_action will handle the details of finding the food item by ID
            #   if self.eating_food_id is already set (e.g. from seeking_food transitioning to eating)
            #   or try to find one if the Bitling is close enough.
            # - If distance is large and network chooses "eating", it's a mis-learned behavior.
            #   We can add a safeguard here or let execute_action handle it.
            # For now, no special setup here; rely on execute_action.
            # The check for `is_at_food` previously here has been removed to simplify choose_action.
            # `execute_action` for "eating" should be robust enough to handle cases
            # where `self.eating_food_id` is not yet set.
            pass

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

    def perceive_environment(self):
        """
        Finds the nearest food source and returns its distance and direction vector.
        """
        nearest_food_item = None
        min_dist_sq = float('inf')

        if not self.environment.food_sources:
            return (float('inf'), 0.0, 0.0)

        for food in self.environment.food_sources:
            dist_x = food['x'] - self.x
            dist_y = food['y'] - self.y
            dist_sq = dist_x**2 + dist_y**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest_food_item = food
        
        if nearest_food_item is not None:
            actual_distance = math.sqrt(min_dist_sq)
            dx = (nearest_food_item['x'] - self.x) / actual_distance if actual_distance > 0 else 0.0
            dy = (nearest_food_item['y'] - self.y) / actual_distance if actual_distance > 0 else 0.0
            return (actual_distance, dx, dy)
        else:
            # This case should ideally not be reached if food_sources was not empty initially,
            # but as a fallback:
            return (float('inf'), 0.0, 0.0)

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
                    self.eating_food_id = self.target_food_item_id # Set ID of food being eaten
                    self.target_food_pos = None
                    self.target_food_item_id = None # Clear the target ID
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
