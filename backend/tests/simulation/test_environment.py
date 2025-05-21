import unittest
import sys
import os

# Adjust the Python path to include the 'backend' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.bitlings.simulation.environment import Environment

class TestEnvironment(unittest.TestCase):

    def setUp(self):
        """Set up for each test."""
        # We re-initialize environment for each test to ensure a clean state,
        # especially regarding initial obstacles added in Environment.__init__
        self.environment = Environment(width=100, height=100)
        # Clear any default entities if necessary for specific tests,
        # though add_obstacle and get_state tests below should work with defaults.
        # For test_add_obstacle, we want to see the count increase from whatever __init__ adds.
        
    def test_add_obstacle(self):
        """Test adding an obstacle to the environment."""
        # Get initial count based on what __init__ might have added
        initial_obstacle_count = len(self.environment.obstacles)
        
        self.environment.add_obstacle(x=50, y=50, radius=5, emoji="🧱")
        
        self.assertEqual(len(self.environment.obstacles), initial_obstacle_count + 1,
                         "Obstacle count should increase by 1.")
        
        new_obstacle = self.environment.obstacles[-1]
        self.assertEqual(new_obstacle['x'], 50)
        self.assertEqual(new_obstacle['y'], 50)
        self.assertEqual(new_obstacle['radius'], 5)
        self.assertEqual(new_obstacle['emoji'], "🧱")
        self.assertIn('id', new_obstacle)
        self.assertTrue(isinstance(new_obstacle['id'], str))

    def test_get_state_includes_obstacles(self):
        """Test that get_state() includes the obstacles list."""
        # Add a specific obstacle for this test, in addition to any defaults
        self.environment.add_obstacle(x=20, y=20, radius=10, emoji="🌲")
        
        state = self.environment.get_state()
        
        self.assertIn('obstacles', state, "State should include 'obstacles' key.")
        self.assertIsInstance(state['obstacles'], list, "'obstacles' in state should be a list.")
        
        # Check if the count matches (includes defaults + the one added here)
        self.assertEqual(len(state['obstacles']), len(self.environment.obstacles))
        
        # Verify details of the last added obstacle (assuming it's the one we added)
        # This makes the test more robust if default obstacles change
        found_test_obstacle = False
        for obs_in_state in state['obstacles']:
            if obs_in_state['x'] == 20 and obs_in_state['y'] == 20 and obs_in_state['radius'] == 10:
                self.assertEqual(obs_in_state['emoji'], "🌲")
                found_test_obstacle = True
                break
        self.assertTrue(found_test_obstacle, "Test obstacle not found in state or details mismatch.")

if __name__ == '__main__':
    unittest.main()
