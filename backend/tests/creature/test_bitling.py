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
        """Test perception of food in the environment."""
        # Test with no food
        self.mock_environment.food_sources = []
        distance, dx, dy = self.bitling.perceive_environment()
        self.assertEqual(distance, float('inf'))
        self.assertEqual(dx, 0.0)
        self.assertEqual(dy, 0.0)

        # Test with one food item
        self.bitling.x = 50
        self.bitling.y = 50
        self.mock_environment.food_sources = [
            {'id': 'food1', 'x': self.bitling.x + 30, 'y': self.bitling.y + 40, 'emoji': '🍎'}
        ]
        distance, dx, dy = self.bitling.perceive_environment()
        self.assertAlmostEqual(distance, 50.0) # sqrt(30^2 + 40^2) = 50
        self.assertAlmostEqual(dx, 30.0 / 50.0)
        self.assertAlmostEqual(dy, 40.0 / 50.0)

        # Test with multiple food items (ensure nearest is chosen)
        # self.bitling.x is 50, self.bitling.y is 50 (from setUp)
        # For this test, let's re-center the bitling for easier coordinate calculations
        self.bitling.x = 0 
        self.bitling.y = 0
        self.mock_environment.food_sources = [
            {'id': 'food_far', 'x': 30, 'y': 40, 'emoji': '🍎'},  # dist 50
            {'id': 'food_near', 'x': 10, 'y': 0, 'emoji': '🍏'}   # dist 10
        ]
        distance, dx, dy = self.bitling.perceive_environment()
        self.assertAlmostEqual(distance, 10.0)
        self.assertAlmostEqual(dx, 1.0) # 10.0 / 10.0
        self.assertAlmostEqual(dy, 0.0)  # 0.0 / 10.0

if __name__ == '__main__':
    unittest.main()
