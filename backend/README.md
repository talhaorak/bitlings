# Bitlings - Backend Simulation Server

This is the Python backend server for the Bitlings artificial life simulation project. It handles the core simulation logic, creature AI, world state, and communication with the frontend via WebSockets.

Inspired by the "Thronglets" concept from Black Mirror's "Plaything" episode, this project aims to simulate digital life forms (`Bitlings`) that learn, adapt, and evolve based on interaction and internal drives.

## Core Concepts

*   **Bitlings:** The artificial life forms inhabiting the world.
*   **BM-Stress Model:** A custom AI model inspired by Boltzmann Machines and biological homeostasis. Bitlings aim to minimize internal "Stress" derived from needs (hunger, energy) and stimuli. Learning occurs by adapting internal network parameters and structure to better predict and execute Stress-reducing actions.
*   **Compartmentalized Mind:** The AI network is conceptually divided into areas inspired by brain functions (Limbic/Drive, Sensory, World Model, Frontal/Executive).
*   **Online Learning:** Bitlings learn continuously through interaction, starting with hard-coded basic behaviors (moving, eating) which are refined over time.
*   **Dynamic Topology:** The underlying AI network can potentially change its structure (add/remove connections/neurons) over long periods.
*   **World Simulation:** Manages the environment, objects (food, toys), time progression, and physics interactions (basic).
*   **WebSocket Server:** Communicates real-time updates (creature states, positions, environment changes) to the frontend and receives user commands (add food, text input).

## Tech Stack

*   **Language:** Python 3.x
*   **WebSocket Library:** [Choose one, e.g., `websockets`, `FastAPI WebSockets`, `Socket.IO (python-socketio)`]
*   **(Placeholder Graphics):** Note that the backend currently only manages state. Visual representation relies on the frontend interpreting state data (e.g., creature type/state maps to specific emojis initially).

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>/backend
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    # (You'll need to create requirements.txt later)
    # Example: pip install websockets fastapi uvicorn
    ```
4.  **Run the server:**
    ```bash
    # Example using FastAPI/Uvicorn:
    # uvicorn main:app --reload --port 8000
    # Or using a simple script:
    # python server.py
    ```
    The server will start and listen for WebSocket connections (defaulting to port 8000, adjust as needed).

      
## Future Plans

*   Implement the full `BM-Stress` model with dynamic topology.
*   Refine compartmentalized mind interactions.
*   Optimize core simulation loop (potentially using C++/Rust modules).
*   Integrate standard ML libraries (PyTorch/TensorFlow) for specific network components if beneficial.
*   Expand world interactions and creature abilities.
*   Add persistence (saving/loading simulation state).


    