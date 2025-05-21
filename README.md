      
# Bitlings - Artificial Life Simulation Project

## Overview

Bitlings is an artificial life simulation project inspired by the concept of "Thronglets" featured in the *Black Mirror* episode "Plaything" (Season 7, Episode 4). The goal is to create a persistent digital world inhabited by creatures called **Bitlings**. These creatures are not merely scripted NPCs; they possess an adaptive AI driven by internal needs and environmental stimuli, allowing them to learn, evolve complex behaviors, and potentially develop unique "personalities" through interaction.

This project serves as an exploration into emergent behavior, artificial intelligence, and the simulation of life-like systems. We aim to build creatures that *feel* alive, fostering a sense of connection and observation akin to tending a digital terrarium filled with evolving entities.

## Inspiration and Philosophy

The core inspiration comes from the "Thronglets" – digital life forms presented as existing beyond simple game mechanics, requiring care and exhibiting unexpected potential. We aim to capture this spirit by focusing on:

*   **Emergence:** Complex behaviors should arise naturally from the interaction of simpler rules, internal drives, and environmental feedback, rather than being explicitly programmed.
*   **Adaptation:** Bitlings should learn and adapt their behavior based on their experiences and interactions with the user and the environment.
*   **Intrinsic Motivation:** Behavior is driven by internal "needs" or "stress" states, pushing the Bitlings towards actions that restore internal balance (homeostasis), rather than solely maximizing an external reward function.
*   **Observation & Nurturing:** The user's primary role is that of an observer and caretaker, influencing the environment and potentially communicating with the Bitlings, rather than directly controlling them.

## Core Features & Goals

*   **Simulated Ecosystem:** A persistent 2D world where Bitlings live.
*   **Bitling Creatures:** Individual agents with:
    *   **Basic Needs:** Hunger, Energy, Health, potentially Mood/Stimulation.
    *   **Adaptive AI:** Driven by the `BM-Stress` model (see below).
    *   **Sensory Input:** Perceive food, obstacles, other Bitlings, and user interactions.
    *   **Actions:** Move, Eat, Sleep, Interact with objects, Vocalize/Communicate.
*   **Online Learning:** Bitlings learn continuously from the moment they exist; no pre-training required for core adaptation.
*   **Complex Behavior Potential:** Aiming for emergent behaviors like rudimentary communication, social interactions (if multiple Bitlings interact), tool use (if applicable), and adaptation to user interaction patterns.
*   **User Interaction:**
    *   Modify the environment (add food, toys).
    *   Observe Bitling states and behaviors.
    *   (Planned) Communicate via text input, which Bitlings can learn to associate with events.
*   **Large, Scrollable World:** The environment is intended to be larger than the screen view.

## Technical Architecture

The project follows a client-server architecture:

*   **Backend (Python):** Handles the core simulation logic, world state, creature AI, physics (basic), and persistence (planned). Communicates with the frontend via WebSockets.
*   **Frontend (TypeScript):** Visualizes the simulation, handles user input, renders graphics (initially using PixiJS with emoji placeholders), and communicates with the backend via WebSockets.

### The Bitling AI: `BM-Stress` Model & Compartmentalization

The heart of the Bitling AI is a custom model we call **`BM-Stress`**, inspired by **Boltzmann Machines (BMs)** and principles of **biological homeostasis**.

1.  **Core Drive - Stress Minimization:**
    *   Each Bitling has an internal scalar value called `Stress` (or `Disequilibrium`).
    *   `Stress` increases due to unmet physiological needs (high Hunger, low Energy), negative environmental stimuli (threats), potentially cognitive load ('thinking'), or encountering unexpected situations.
    *   The fundamental drive of a Bitling is to perform actions that **reduce** this `Stress` level and return to a state of equilibrium.
    *   This acts as an intrinsic motivation system.

2.  **Boltzmann Machine Inspiration:**
    *   We use concepts from BMs because they naturally deal with **energy minimization** in networks, which parallels our `Stress` minimization goal.
    *   The Bitling's "mind" is represented as a network of interconnected units (neurons). This network has its *own* internal energy state (`E_BM`) based on unit activations and connection weights.
    *   The network tends to settle into low `E_BM` states, representing stable internal "thoughts" or "representations" of the current context (needs + environment).
    *   **Crucially:** This is *not* a standard BM implementation. It's adapted:
        *   The network's settling process helps associate input contexts (high hunger + seeing food) with potential actions (approach food, eat).
        *   The *success* of an action is judged by the reduction in the global `Stress` value, not just the internal `E_BM`.

3.  **Compartmentalized Mind (Brain Analogy):**
    *   To manage complexity and specialize function, the AI network is conceptually divided into interacting compartments, loosely inspired by mammalian brain regions:
        *   **"Limbic System":** Core drive generator. Directly translates physiological needs (Hunger, Energy) into the primary `Stress` signal. Biases basic survival actions. Largely hard-coded drives, minimal learning.
        *   **"Temporal/Parietal Lobe" (Sensory):** Processes raw sensory inputs (visual, auditory, text). Handles feature extraction, pattern recognition (including word identification). Highly adaptive, learns new patterns/words dynamically.
        *   **"Midbrain" (World Model):** Builds and maintains an internal representation of the environment (spatial map, object locations). Learns associations within the environment.
        *   **"Frontal Cortex" (Executive & Self-Awareness):** Integrates information from all other compartments (`Stress`, sensory context, world state). Handles higher-level decision making, potentially overriding impulses. Includes **Meta-State Units** that receive the network's own state (e.g., current `Stress` level, `E_BM` stability, activity level) as input, enabling a basic form of self-referenced processing. This is where complex associations and temporal learning primarily occur.
    *   These compartments interact (bottom-up information flow, top-down modulation), all working towards the global goal of reducing `Stress`.

4.  **Learning Mechanisms:**
    *   **Online & Incremental:** Learning happens constantly during the simulation.
    *   **Hebbian Reinforcement:** Connections and pathways within the network compartments that were active during an action leading to successful `Stress` reduction are strengthened. ("Neurons that fire together wire together" when the outcome is good). Conversely, pathways leading to increased `Stress` might be weakened.
    *   **Temporal Association (Eligibility Traces):** Allows linking stimuli/actions to rewards (`Stress` reduction) that occur seconds later. Essential for learning from text commands (e.g., "feeding time" followed by food appearing).
    *   **Dynamic Topology:** The network structure itself can change over time:
        *   *Pruning:* Weak or unused connections are automatically removed.
        *   *Growth:* New connections or even new units can be added, for instance, when encountering unknown words or if the current network consistently fails to reduce `Stress` (indicating insufficient complexity).

## Technology Stack

*   **Backend:**
    *   Language: Python 3.x
    *   Package Manager: `uv`
    *   WebSocket Server: `websockets` library
    *   (Future) Potential integration: PyTorch/TensorFlow, C++/Rust modules for performance.
*   **Frontend:**
    *   Runtime/Package Manager: Bun (or Node.js/npm/pnpm)
    *   Build Tool: Vite
    *   Language: TypeScript
    *   Graphics Rendering: PixiJS
    *   Communication: Native WebSocket API
*   **Development:** Monorepo structure managed likely via workspace features (if using npm/pnpm/yarn) or simply shared Git repo.

## Project Structure (High Level)

```plaintext
bitlings-project/
├── backend/ # Python backend server code
│ ├── src/
│ ├── tests/
│ ├── pyproject.toml
│ └── README.md # Backend specific details
├── frontend/ # TypeScript frontend code
│ ├── public/
│ ├── src/
│ ├── index.html
│ ├── package.json
│ ├── tsconfig.json
│ ├── vite.config.ts
│ └── README.md # Frontend specific details
└── README.md # This file (Overall Project)

```
      
*(Refer to `backend/README.md` and `frontend/README.md` for detailed structure and setup)*

## Current Status (As of [Current Date])

*   **Architecture Defined:** The core concepts (`BM-Stress`, Compartments, Learning Rules) are designed conceptually.
*   **Basic Backend Skeleton:**
    *   Python server using `websockets` is set up.
    *   Basic simulation loop exists.
    *   Placeholder `Bitling` class with core needs (Hunger, Energy) that change over time.
    *   Placeholder actions (idle, basic random wandering). Needs are *not yet* driving actions effectively.
    *   Basic `Environment` class holding Bitlings and placeholder food.
    *   WebSocket broadcasting of world state implemented.
    *   Basic handling of "add_food" command from user.
*   **Basic Frontend Skeleton:**
    *   TypeScript project using Vite and PixiJS is set up.
    *   Connects to backend via WebSockets.
    *   Receives `world_update` messages.
    *   Renders Bitlings and food items using **Emojis** via `PIXI.Text`.
    *   Updates emoji positions and types based on backend state.
    *   Removes sprites for deleted entities.
    *   Basic HTML UI overlay for status and an "Add Food" button.
    *   Clicking on the canvas (in "Add Food" mode) sends coordinates to the backend.
*   **AI Implementation:** The complex `BM-Stress` model, compartmentalization, advanced learning rules, and dynamic topology are **NOT YET IMPLEMENTED**. Current Bitling behavior is very basic placeholder logic.

## Getting Started

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd bitlings-project
    ```
2.  **Setup Backend:**
    ```bash
    cd backend
    # Create virtual env if desired (python -m venv venv; source venv/bin/activate)
    uv sync # Installs dependencies from pyproject.toml using uv
    # Or: uv pip install -r requirements.txt # If using requirements.txt
    ```
3.  **Setup Frontend:**
    ```bash
    cd ../frontend
    bun install # Or: npm install / pnpm install
    ```
4.  **Run Backend:**
    *   Open a terminal in the `backend` directory.
    *   Run: `python src/main.py`
    *   Keep this terminal running.
5.  **Run Frontend:**
    *   Open *another* terminal in the `frontend` directory.
    *   Run: `bun run dev` (or `npm run dev` / `pnpm dev`)
    *   Open your web browser to the address provided (e.g., `http://localhost:5173`).

You should see the frontend connect to the backend and display the initial state of the simulation using emojis.

## Future Plans / Roadmap

1.  **Implement Core AI (`BM-Stress` Basics):**
    *   Connect Bitling needs directly to `Stress` generation.
    *   Implement basic BM-like network settling.
    *   Link network states to action probabilities.
    *   Implement basic Hebbian learning based on `Stress` reduction.
2.  **Implement Compartments:** Structure the AI into the defined compartments.
3.  **Refine Hard-coded Behaviors:** Improve obstacle avoidance, pathfinding to food/sleep spots.
4.  **Implement Temporal Learning:** Add eligibility traces for time-delayed associations (especially for text input).
5.  **Implement Text Input:** Allow user text input; handle unknown words by growing the network dynamically.
6.  **Replace Placeholders:** Integrate proper 2D sprite assets and animations.
7.  **World Persistence:** Save and load simulation state.
8.  **UI Enhancements:** More detailed status displays, interaction options.
9.  **Scalability & Optimization:** Address performance bottlenecks as the simulation grows.
10. **Dynamic Topology:** Fully implement network pruning and growth rules.

## Contributing

We welcome contributions! If you'd like to help, please:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name`).
3.  Make your changes. Ensure code follows existing style conventions.
4.  Test your changes thoroughly.
5.  Commit your changes with clear, descriptive messages.
6.  Push your branch to your fork (`git push origin feature/your-feature-name`).
7.  Open a Pull Request (PR) against the main branch of the original repository.
8.  Clearly describe the changes made and the reasoning behind them in the PR description.

Please feel free to open an issue to discuss potential changes or features before starting significant work.

    