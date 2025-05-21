import unittest
import numpy as np
import sys
import os

# Adjust the Python path to include the 'backend' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.bitlings.ai.network import BitlingNetwork, MAX_PERCEIVABLE_DISTANCE

class TestBitlingNetwork(unittest.TestCase):

    def setUp(self):
        """Set up for each test."""
        np.random.seed(42) # For predictable random weight initialization
        self.network = BitlingNetwork()
        # Default sizes: input=3, hidden=4, output=5
        # Default learning rate: 0.05

    def test_network_initialization(self):
        """Test shapes of weights, biases, and activations."""
        self.assertIsNotNone(self.network.weights_input_hidden)
        # Updated for new input size (5)
        self.assertEqual(self.network.weights_input_hidden.shape, (5, self.network.hidden_size)) 
        self.assertIsNotNone(self.network.weights_hidden_output)
        self.assertEqual(self.network.weights_hidden_output.shape, (self.network.hidden_size, self.network.output_size))

        self.assertIsNotNone(self.network.bias_hidden)
        self.assertEqual(self.network.bias_hidden.shape, (self.network.hidden_size,))
        self.assertIsNotNone(self.network.bias_output)
        self.assertEqual(self.network.bias_output.shape, (self.network.output_size,))

        self.assertIsNotNone(self.network.input_activations)
        # Updated for new input size (5)
        self.assertEqual(self.network.input_activations.shape, (5,)) 
        self.assertIsNotNone(self.network.hidden_activations)
        self.assertEqual(self.network.hidden_activations.shape, (self.network.hidden_size,))
        self.assertIsNotNone(self.network.output_activations)
        self.assertEqual(self.network.output_activations.shape, (5,))
        
        # Check learning rate
        self.assertEqual(self.network.learning_rate, 0.05)


    def test_set_inputs(self):
        """Test input normalization."""
        # Test case 1: Basic values
        self.network.set_inputs(hunger=100, energy=0, distance_to_food=10, food_dx=0.6, food_dy=-0.8)
        expected_activations_1 = np.array([
            1.0,                                 # hunger_norm
            0.0,                                 # energy_norm
            10.0 / MAX_PERCEIVABLE_DISTANCE,     # distance_norm
            0.6,                                 # food_dx_norm
            -0.8                                 # food_dy_norm
        ])
        np.testing.assert_array_almost_equal(self.network.input_activations, expected_activations_1)

        # Test case 2: Distance is float('inf')
        self.network.set_inputs(hunger=0, energy=100, distance_to_food=float('inf'), food_dx=0.0, food_dy=0.0)
        expected_activations_2 = np.array([0.0, 1.0, 1.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(self.network.input_activations, expected_activations_2)

        # Test case 3: Distance capping
        self.network.set_inputs(hunger=50, energy=75, distance_to_food=1000, food_dx=0.1, food_dy=0.2)
        expected_activations_3 = np.array([
            0.5,                                 # hunger_norm
            0.75,                                # energy_norm
            1.0,                                 # distance_norm (1000 / 500 = 2.0, capped to 1.0)
            0.1,                                 # food_dx_norm
            0.2                                  # food_dy_norm
        ])
        np.testing.assert_array_almost_equal(self.network.input_activations, expected_activations_3)
        
        # Test case 4: Clipping for hunger and energy
        self.network.set_inputs(hunger=150, energy=-20, distance_to_food=50, food_dx=-1.2, food_dy=1.2)
        expected_activations_4 = np.array([
            1.0,                                 # hunger_norm (clipped)
            0.0,                                 # energy_norm (clipped)
            50.0 / MAX_PERCEIVABLE_DISTANCE,     # distance_norm
            -1.0,                                # food_dx_norm (clipped)
            1.0                                  # food_dy_norm (clipped)
        ])
        np.testing.assert_array_almost_equal(self.network.input_activations, expected_activations_4)


    def test_feedforward_step_and_settle(self):
        """Test the feedforward mechanism (via settle)."""
        # Updated input_activations to 5 elements
        self.network.input_activations = np.array([1.0, 0.0, 0.1, 0.5, -0.5]) 
        
        # Set known weights and biases for predictability
        # Updated weights_input_hidden shape to (5, 4)
        self.network.weights_input_hidden = np.full((5, self.network.hidden_size), 0.5) 
        self.network.bias_hidden = np.full(self.network.hidden_size, 0.1)
        self.network.weights_hidden_output = np.full((self.network.hidden_size, self.network.output_size), 0.5)
        self.network.bias_output = np.full(self.network.output_size, 0.1)

        self.network.settle(iterations=5) # settle calls _feedforward_step

        self.assertIsNotNone(self.network.output_activations)
        # Check that activations are within sigmoid range (0 to 1)
        self.assertTrue(np.all(self.network.output_activations >= 0) and np.all(self.network.output_activations <= 1))
        # Check that they are not all zeros or all ones (highly unlikely with sigmoid unless inputs are extreme)
        self.assertFalse(np.all(self.network.output_activations == 0))
        self.assertFalse(np.all(self.network.output_activations == 1))

        # Example: Calculate one step manually for a rough check (optional)
        # inputs_to_hidden_sum = np.dot(np.array([1.0, 0.0, 1.0]), np.full((3,4), 0.5)) + np.full(4,0.1)
        # expected_hidden_activations = 1 / (1 + np.exp(-inputs_to_hidden_sum)) # sigmoid
        # self.network._feedforward_step() # Call one step
        # np.testing.assert_array_almost_equal(self.network.hidden_activations, expected_hidden_activations, decimal=5)


    def test_get_chosen_action(self):
        """Test action selection based on output activations."""
        # Output names: ["seeking_food", "eating", "seeking_sleep", "wandering", "idle"]
        self.network.output_activations = np.array([0.1, 0.2, 0.8, 0.3, 0.1])
        chosen_action = self.network.get_chosen_action()
        self.assertEqual(chosen_action, "seeking_sleep") # Index 2

        self.network.output_activations = np.array([0.9, 0.05, 0.1, 0.0, 0.0])
        chosen_action = self.network.get_chosen_action()
        self.assertEqual(chosen_action, "seeking_food") # Index 0

        self.network.output_activations = np.array([0.1, 0.1, 0.1, 0.1, 0.9])
        chosen_action = self.network.get_chosen_action()
        self.assertEqual(chosen_action, "idle") # Index 4

    def test_apply_learning_successful_action(self):
        """Test Hebbian learning rule for successful and unsuccessful actions."""
        # Updated input_activations to 5 elements
        self.network.input_activations = np.array([1.0, 0.5, 0.1, 0.2, -0.2]) 
        # Simulate that these inputs led to some hidden activations during feedforward
        self.network.hidden_activations = np.array([0.5, 0.6, 0.4, 0.7]) # Assuming 4 hidden units
        
        chosen_action_index = 0 # "seeking_food"

        # Store initial weights
        # Example: Input 0 (hunger) to Hidden 0
        initial_weight_ih_00 = self.network.weights_input_hidden[0, 0].copy() 
        # Example: Hidden 0 to Output action (seeking_food)
        initial_weight_ho_00 = self.network.weights_hidden_output[0, chosen_action_index].copy() 

        # Apply learning for a successful action
        self.network.apply_learning(chosen_action_index=chosen_action_index, was_successful=True)

        # Assert weights increased (positive reinforcement)
        # Check input to hidden (for hidden_activations > 0.1)
        self.assertGreater(self.network.weights_input_hidden[0, 0], initial_weight_ih_00)
        # Check hidden to output
        self.assertGreater(self.network.weights_hidden_output[0, chosen_action_index], initial_weight_ho_00)

        # Test unsuccessful action: weights should not change
        # Re-capture initial weights (or reset them if more complex changes happened)
        self.network.weights_input_hidden[0, 0] = initial_weight_ih_00
        self.network.weights_hidden_output[0, chosen_action_index] = initial_weight_ho_00
        
        initial_weight_ih_00_before_fail = self.network.weights_input_hidden[0, 0].copy()
        initial_weight_ho_00_before_fail = self.network.weights_hidden_output[0, chosen_action_index].copy()

        self.network.apply_learning(chosen_action_index=chosen_action_index, was_successful=False)

        self.assertEqual(self.network.weights_input_hidden[0, 0], initial_weight_ih_00_before_fail)
        self.assertEqual(self.network.weights_hidden_output[0, chosen_action_index], initial_weight_ho_00_before_fail)

    def test_get_action_probabilities(self):
        """Test softmax probability calculations."""
        self.network.output_activations = np.array([0.1, 0.2, 0.8, 0.3, 0.1])
        probabilities = self.network._get_action_probabilities()

        self.assertIsNotNone(probabilities)
        self.assertEqual(probabilities.shape, (self.network.output_size,))
        np.testing.assert_almost_equal(np.sum(probabilities), 1.0, decimal=6)
        self.assertTrue(np.all(probabilities >= 0) and np.all(probabilities <= 1))

        # Test with more varied activations
        self.network.output_activations = np.array([-0.5, 0.0, 0.5, 0.2, -0.1])
        probabilities = self.network._get_action_probabilities()
        np.testing.assert_almost_equal(np.sum(probabilities), 1.0, decimal=6)
        self.assertTrue(np.all(probabilities >= 0) and np.all(probabilities <= 1))


if __name__ == '__main__':
    unittest.main()
