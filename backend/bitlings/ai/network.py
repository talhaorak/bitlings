import numpy as np
import math

MAX_PERCEIVABLE_DISTANCE = 500.0 # Class/Module Constant

class BitlingNetwork:
    """
    A simple feedforward neural network for Bitling decision-making.
    """
    def __init__(self, hidden_size=4, output_size=5): # Removed input_size from signature
        """
        Initialize the neural network's structure, weights, and biases.

        Args:
            hidden_size (int): Number of hidden neurons.
            output_size (int): Number of output neurons.
        """
        # Define names for input and output layers for clarity
        self.input_names = ["hunger", "energy", "distance_to_food", "food_dx", "food_dy"]
        self.output_names = ["seeking_food", "eating", "seeking_sleep", "wandering", "idle"]

        self.input_size = len(self.input_names) # Updated input_size
        self.hidden_size = hidden_size
        self.output_size = output_size


        # Initialize weights with small random values between -0.5 and 0.5
        self.weights_input_hidden = np.random.uniform(-0.5, 0.5, (self.input_size, self.hidden_size))
        self.weights_hidden_output = np.random.rand(self.hidden_size, self.output_size) - 0.5 # Kept as is

        # Initialize biases with small random values between -0.5 and 0.5
        self.bias_hidden = np.random.rand(self.hidden_size) - 0.5 # Kept as is
        self.bias_output = np.random.rand(self.output_size) - 0.5 # Kept as is
        
        # Alternative: Initialize biases with zeros
        # self.bias_hidden = np.zeros(self.hidden_size)
        # self.bias_output = np.zeros(self.output_size)

        # Initialize activation storage (using numpy arrays for efficient calculations)
        self.input_activations = np.zeros(self.input_size, dtype=float) # Resized
        self.hidden_activations = np.zeros(self.hidden_size, dtype=float)
        self.output_activations = np.zeros(self.output_size, dtype=float)

        self.learning_rate = 0.05

    def set_inputs(self, hunger: float, energy: float, distance_to_food: float, food_dx: float, food_dy: float):
        """
        Normalize and set the input activations for the network.
        Args:
            hunger (float): Current hunger level (0-100).
            energy (float): Current energy level (0-100).
            distance_to_food (float): Distance to the nearest food.
            food_dx (float): Normalized x-component of direction to food.
            food_dy (float): Normalized y-component of direction to food.
        """
        hunger_norm = np.clip(hunger / 100.0, 0.0, 1.0)
        energy_norm = np.clip(energy / 100.0, 0.0, 1.0)

        if distance_to_food == float('inf') or distance_to_food > MAX_PERCEIVABLE_DISTANCE:
            distance_norm = 1.0
        else:
            distance_norm = min(distance_to_food / MAX_PERCEIVABLE_DISTANCE, 1.0)
        
        # food_dx and food_dy are assumed to be already normalized (-1 to 1)
        # We can clip them just in case for robustness, though they should be correct from perceive_environment
        food_dx_norm = np.clip(food_dx, -1.0, 1.0)
        food_dy_norm = np.clip(food_dy, -1.0, 1.0)

        self.input_activations = np.array([
            hunger_norm, 
            energy_norm, 
            distance_norm, 
            food_dx_norm, 
            food_dy_norm
        ], dtype=float)
        
    def _sigmoid(self, x):
        """
        Sigmoid activation function.
        Using np.exp for element-wise application if x is a numpy array.
        """
        # Clip x to prevent overflow in exp, common practice
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))

    def _feedforward_step(self):
        """
        Performs a single feedforward pass through the network.
        """
        # Calculate hidden layer activations
        hidden_inputs = np.dot(self.input_activations, self.weights_input_hidden) + self.bias_hidden
        self.hidden_activations = self._sigmoid(hidden_inputs)

        # Calculate output layer activations
        output_inputs = np.dot(self.hidden_activations, self.weights_hidden_output) + self.bias_output
        self.output_activations = self._sigmoid(output_inputs)

    def settle(self, iterations: int = 10):
        """
        Calls _feedforward_step() multiple times to allow activations to stabilize.
        Args:
            iterations (int): The number of feedforward passes.
        """
        for _ in range(iterations):
            self._feedforward_step()
        # The final state of self.output_activations is the result.

    def get_chosen_action(self) -> str:
        """
        Determines the action to take based on the highest output activation.
        Assumes `settle()` has been called and `self.output_activations` is populated.

        Returns:
            str: The name of the chosen action.
        """
        chosen_index = np.argmax(self.output_activations)
        if chosen_index < len(self.output_names):
            return self.output_names[chosen_index]
        else:
            # Fallback or error, though argmax should be within bounds
            # if output_activations has the correct size.
            return "idle" # Default to idle if something is wrong

    def _get_action_probabilities(self):
        """
        Calculates action probabilities using the softmax function
        over the output activations.
        For internal/future use.

        Returns:
            numpy.ndarray: An array of probabilities for each action.
        """
        # Subtract max for numerical stability before exponentiation
        stable_activations = self.output_activations - np.max(self.output_activations)
        exp_activations = np.exp(stable_activations)
        probabilities = exp_activations / np.sum(exp_activations)
        return probabilities

    def apply_learning(self, chosen_action_index: int, was_successful: bool):
        """
        Applies a simplified Hebbian-like learning rule.
        Args:
            chosen_action_index (int): Index of the action chosen by the network.
            was_successful (bool): True if the action led to stress reduction.
        """
        if not was_successful:
            return # Only apply positive reinforcement for now

        # Reinforce weights from Hidden layer to the chosen Output action
        for j in range(self.hidden_size):
            self.weights_hidden_output[j, chosen_action_index] += \
                self.learning_rate * self.hidden_activations[j]

        # Reinforce weights from Input layer to active Hidden units
        # This strengthens connections that contributed to the active hidden units
        # which in turn contributed to the successful action.
        for i in range(self.input_size):
            for j in range(self.hidden_size):
                if self.hidden_activations[j] > 0.1: # Only for significantly active hidden units
                    self.weights_input_hidden[i, j] += \
                        self.learning_rate * self.input_activations[i] * self.hidden_activations[j]
        
        # Optional: Clip weights to prevent them from growing too large, e.g., np.clip
        # self.weights_hidden_output = np.clip(self.weights_hidden_output, -1.0, 1.0)
        # self.weights_input_hidden = np.clip(self.weights_input_hidden, -1.0, 1.0)
