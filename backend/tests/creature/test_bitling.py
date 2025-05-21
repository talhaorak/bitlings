import unittest
import sys
import os
import math # Added math import

# Adjust the Python path to include the 'backend' directory
# This assumes the tests are run from the root directory containing 'backend'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.bitlings.creature.bitling import Bitling
from backend.bitlings.simulation.environment import Environment

class TestBitling(unittest.TestCase):

    def setUp(self):
        """Set up for each test."""
        self.mock_environment = Environment(width=100, height=100)
        # Clear any default entities from the mock environment
        self.mock_environment.bitlings = []
        self.mock_environment.food_sources = []
        self.mock_environment.obstacles = [] # Ensure no obstacles from Environment's __init__
        
        self.bitling = Bitling(x=50, y=50, environment=self.mock_environment)
        # Reset bitling's core attributes for predictable tests
        self.bitling.health = 100
        self.bitling.hunger = 0
        self.bitling.energy = 100
        self.bitling.mood = 50
        self.bitling.age = 0
        self.bitling.stress = 0.0
        self.bitling.current_action = "idle"
        self.bitling.action_timer = 0.0
        self.bitling.target_food_pos = None
        self.bitling.eating_food_id = None


    def test_stress_calculation(self):
        """Test stress calculation based on hunger and energy."""
        # Case 1: Low hunger, high energy -> Low stress
        self.bitling.hunger = 0
        self.bitling.energy = 100
        self.bitling.update_passive(0.1)
        self.assertAlmostEqual(self.bitling.stress, 0, delta=0.1, msg="Stress should be near 0 for no hunger/full energy")

        # Case 2: High hunger, high energy -> Medium stress (from hunger)
        self.bitling.hunger = 100
        self.bitling.energy = 100
        self.bitling.update_passive(0.1) # Hunger increased by 0.1, Energy decreased by 0.05
        # Expected: (100/100)*50 + ((100-100)/100)*50 = 50
        self.assertAlmostEqual(self.bitling.stress, 50, delta=0.1, msg="Stress should be near 50 for full hunger/full energy")

        # Case 3: Low hunger, low energy -> Medium stress (from low energy)
        self.bitling.hunger = 0
        self.bitling.energy = 0
        self.bitling.update_passive(0.1) # Hunger increased by 0.1, Energy decreased by 0.05 (but capped at 0)
        # Expected: (0/100)*50 + ((100-0)/100)*50 = 50
        self.assertAlmostEqual(self.bitling.stress, 50, delta=0.1, msg="Stress should be near 50 for no hunger/no energy")

        # Case 4: High hunger, low energy -> High stress
        self.bitling.hunger = 100
        self.bitling.energy = 0
        self.bitling.update_passive(0.1)
        # Expected: (100/100)*50 + ((100-0)/100)*50 = 100
        self.assertAlmostEqual(self.bitling.stress, 100, delta=0.1, msg="Stress should be near 100 for full hunger/no energy")

        # Case 5: Intermediate values
        self.bitling.hunger = 50
        self.bitling.energy = 50
        self.bitling.update_passive(0.1) # Hunger up, energy down slightly
        # Expected: (50/100)*50 + ((100-50)/100)*50 = 25 + 25 = 50
        self.assertAlmostEqual(self.bitling.stress, 50, delta=0.1, msg="Stress should be near 50 for mid hunger/mid energy")

    def test_choose_action_stress_driven(self):
        """Test action choices based on stress levels."""
        # High Stress (Hunger):
        self.bitling.hunger = 80
        self.bitling.energy = 80
        self.bitling.update_passive(0.1) # Updates stress
        self.bitling.choose_action()
        self.assertEqual(self.bitling.current_action, "seeking_food", "Should seek food when stress is high due to hunger")

        # High Stress (Energy):
        self.bitling.hunger = 20
        self.bitling.energy = 20
        self.bitling.update_passive(0.1) # Updates stress
        self.bitling.choose_action()
        self.assertEqual(self.bitling.current_action, "seeking_sleep", "Should seek sleep when stress is high due to low energy")

        # Low Stress:
        self.bitling.hunger = 20
        self.bitling.energy = 80
        self.bitling.update_passive(0.1) # Updates stress
        self.bitling.choose_action()
        self.assertIn(self.bitling.current_action, ["idle", "wandering"], "Should be idle or wandering when stress is low")

    def test_action_eating(self):
        """Test the full cycle of seeking and eating food."""
        self.bitling.hunger = 80 # High hunger
        self.bitling.energy = 80 # Good energy
        self.mock_environment.add_food({'id': 'food1', 'x': 50, 'y': 50, 'emoji': '🍎'})
        
        self.bitling.update_passive(0.1) # Calculate initial stress
        initial_stress = self.bitling.stress
        # (80/100)*50 + ((100-80)/100)*50 = 40 + 10 = 50. Stress from hunger is dominant.

        self.bitling.choose_action()
        self.assertEqual(self.bitling.current_action, "seeking_food")

        # Simulate Bitling reaching food (already at food location in this test)
        self.bitling.x = 50 
        self.bitling.y = 50

        self.bitling.execute_action(0.1) # Should switch to "eating"
        self.assertEqual(self.bitling.current_action, "eating")
        self.assertEqual(self.bitling.eating_food_id, "food1")

        # Simulate eating duration
        self.bitling.action_timer = 0 # Force timer to expire
        self.bitling.execute_action(0.1) # Process eating completion

        self.assertEqual(self.bitling.hunger, 30, "Hunger should be reduced after eating")
        self.assertEqual(len(self.mock_environment.food_sources), 0, "Food should be removed from environment")
        self.assertEqual(self.bitling.current_action, "idle", "Should be idle after eating")

        # Re-calculate stress with new hunger
        self.bitling.update_passive(0.1) 
        # New stress: (30/100)*50 + ((100-~80)/100)*50 = 15 + ~10 = ~25
        self.assertLess(self.bitling.stress, initial_stress, "Stress should be reduced after eating and satisfying hunger")

    def test_action_sleeping(self):
        """Test the full cycle of seeking and executing sleep."""
        self.bitling.hunger = 20 # Low hunger
        self.bitling.energy = 20 # Low energy
        
        self.bitling.update_passive(0.1) # Calculate initial stress
        initial_stress = self.bitling.stress
        # (20/100)*50 + ((100-20)/100)*50 = 10 + 40 = 50. Stress from low energy is dominant.

        self.bitling.choose_action()
        self.assertEqual(self.bitling.current_action, "seeking_sleep")

        self.bitling.execute_action(0.1) # Should switch to "sleeping"
        self.assertEqual(self.bitling.current_action, "sleeping")
        self.assertTrue(self.bitling.action_timer > 0)

        # Simulate sleeping duration
        self.bitling.action_timer = 0 # Force timer to expire
        self.bitling.execute_action(0.1) # Process sleeping completion

        self.assertEqual(self.bitling.energy, 100, "Energy should be fully restored after sleeping")
        self.assertEqual(self.bitling.current_action, "idle", "Should be idle after sleeping")

        # Re-calculate stress with new energy
        self.bitling.update_passive(0.1)
        # New stress: (20/100)*50 + ((100-100)/100)*50 = 10 + 0 = 10
        self.assertLess(self.bitling.stress, initial_stress, "Stress should be reduced after sleeping and restoring energy")

    def test_perceive_environment(self):
        """Test perception of food and obstacles in the environment."""
        # --- Food Perception (existing tests adapted) ---
        self.mock_environment.food_sources = []
        self.mock_environment.obstacles = [] # Ensure no obstacles for this part
        dist_f, dx_f, dy_f, dist_o, dx_o, dy_o = self.bitling.perceive_environment()
        self.assertEqual(dist_f, float('inf'), "Distance to food should be inf when no food")
        self.assertEqual(dx_f, 0.0)
        self.assertEqual(dy_f, 0.0)
        self.assertEqual(dist_o, float('inf'), "Distance to obstacle should be inf when no obstacles")
        self.assertEqual(dx_o, 0.0)
        self.assertEqual(dy_o, 0.0)

        self.bitling.x = 50
        self.bitling.y = 50
        self.mock_environment.food_sources = [{'id': 'food1', 'x': self.bitling.x + 30, 'y': self.bitling.y + 40, 'emoji': '🍎'}]
        dist_f, dx_f, dy_f, _, _, _ = self.bitling.perceive_environment() # Ignoring obstacle part
        self.assertAlmostEqual(dist_f, 50.0) # sqrt(30^2 + 40^2) = 50
        self.assertAlmostEqual(dx_f, 30.0 / 50.0)
        self.assertAlmostEqual(dy_f, 40.0 / 50.0)

        self.bitling.x = 0; self.bitling.y = 0
        self.mock_environment.food_sources = [
            {'id': 'food_far', 'x': 30, 'y': 40, 'emoji': '🍎'},
            {'id': 'food_near', 'x': 10, 'y': 0, 'emoji': '🍏'}
        ]
        dist_f, dx_f, dy_f, _, _, _ = self.bitling.perceive_environment()
        self.assertAlmostEqual(dist_f, 10.0)
        self.assertAlmostEqual(dx_f, 1.0)
        self.assertAlmostEqual(dy_f, 0.0)

        # --- Obstacle Perception ---
        self.mock_environment.food_sources = [] # Clear food for obstacle specific tests
        self.mock_environment.obstacles = []
        self.bitling.x = 50; self.bitling.y = 50

        # Sub-test with no obstacles (already covered at the beginning, but good for clarity)
        _, _, _, dist_o, dx_o, dy_o = self.bitling.perceive_environment()
        self.assertEqual(dist_o, float('inf'))
        self.assertEqual(dx_o, 0.0)
        self.assertEqual(dy_o, 0.0)

        # Sub-test with one obstacle
        self.mock_environment.obstacles = [{'id': 'obs1', 'x': self.bitling.x + 30, 'y': self.bitling.y + 40, 'radius': 5, 'emoji': '🚧'}]
        _, _, _, dist_o, dx_o, dy_o = self.bitling.perceive_environment()
        expected_center_dist_o = 50.0
        expected_surface_dist_o = expected_center_dist_o - 5.0
        self.assertAlmostEqual(dist_o, expected_surface_dist_o)
        self.assertAlmostEqual(dx_o, 30.0 / expected_center_dist_o)
        self.assertAlmostEqual(dy_o, 40.0 / expected_center_dist_o)

        # Sub-test with multiple obstacles (ensure nearest is chosen based on center, distance to surface reported)
        self.mock_environment.obstacles = [] # Clear previous
        self.bitling.x = 0; self.bitling.y = 0
        obs1_x, obs1_y, obs1_r = 60, 80, 5  # center_dist=100, surface=95
        obs2_x, obs2_y, obs2_r = 10, 0, 3   # center_dist=10, surface=7
        self.mock_environment.add_obstacle(x=obs1_x, y=obs1_y, radius=obs1_r)
        self.mock_environment.add_obstacle(x=obs2_x, y=obs2_y, radius=obs2_r)
        
        _, _, _, dist_o, dx_o, dy_o = self.bitling.perceive_environment()
        self.assertAlmostEqual(dist_o, 7.0, msg="Should choose obs2, surface distance") # Surface distance to obs2
        self.assertAlmostEqual(dx_o, 1.0, msg="Direction dx to obs2 center")   # Direction to obs2 center (10.0/10.0)
        self.assertAlmostEqual(dy_o, 0.0, msg="Direction dy to obs2 center")

    def test_obstacle_avoidance_movement(self):
        """Test that the Bitling attempts to avoid obstacles when moving."""
        self.bitling.x, self.bitling.y = 50, 50
        initial_x, initial_y = self.bitling.x, self.bitling.y

        # Food target directly "below" the Bitling
        food_target_x, food_target_y = 50, 10
        self.mock_environment.food_sources = [{'id': 'food_target', 'x': food_target_x, 'y': food_target_y, 'emoji': '🎯'}]
        
        # Obstacle directly between Bitling and food
        obstacle_x, obstacle_y, obstacle_radius = 50, 30, 10
        self.mock_environment.obstacles = [{'id': 'obs1', 'x': obstacle_x, 'y': obstacle_y, 'radius': obstacle_radius, 'emoji': '🚧'}]

        self.bitling.current_action = "seeking_food"
        self.bitling.target_food_pos = (food_target_x, food_target_y)
        self.bitling.target_food_item_id = 'food_target' # As per current Bitling logic

        # Store position before movement
        original_x = self.bitling.x
        
        # Execute action for a small time_delta
        # A single step might not show dramatic avoidance, but it should deviate
        self.bitling.execute_action(time_delta=0.1) 

        # Assertions:
        # 1. The Bitling should have moved from its initial position.
        self.assertTrue(self.bitling.x != initial_x or self.bitling.y != initial_y, 
                        "Bitling should have moved.")

        # 2. The Bitling should have moved sideways, not straight down.
        #    Given the setup, AVOIDANCE_STRENGTH will push it away from x=50.
        self.assertNotEqual(self.bitling.x, original_x, 
                            "Bitling should have moved sideways (x position changed) to avoid obstacle.")

        # 3. Optional: Check if y position change is less than direct path or if it moved "up" slightly
        #    This is harder to assert precisely without replicating the exact vector math.
        #    If it moved purely sideways, y might not change much in one step.
        #    If obs_dx_perc was 0 (as it is here), steer_dx is 0, so obstacle_avoidance_force_x is 0.
        #    This means it should have tried to move along the y-axis primarily, but the obstacle is also on y-axis.
        #    Let's refine the scenario or assertion.
        #    The current avoidance logic uses -obs_dx_perc. If obs_dx_perc is 0, then steer_dx is 0.
        #    This is a flaw in the test setup for simple x-axis deviation.
        #    Let's shift the obstacle slightly to the side to make the test more effective.

        self.mock_environment.obstacles = [{'id': 'obs1', 'x': 55, 'y': 30, 'radius': 10, 'emoji': '🚧'}]
        self.bitling.x, self.bitling.y = 50, 50 # Reset position
        original_x_for_offset_obs = self.bitling.x
        self.bitling.execute_action(time_delta=0.1)
        
        # Now, obs_dx_perc will be non-zero, so steer_dx will be non-zero.
        # The Bitling is at x=50, obstacle at x=55. It should try to move left (x < 50).
        self.assertLess(self.bitling.x, original_x_for_offset_obs,
                        "Bitling should have moved left to avoid slightly offset obstacle.")


if __name__ == '__main__':
    unittest.main()
