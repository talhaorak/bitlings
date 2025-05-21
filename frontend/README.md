# Bitlings - Frontend Interface

This is the frontend web application for the Bitlings artificial life simulation. It connects to the Python backend via WebSockets to visualize the world, the `Bitlings`, and allow user interaction.

## Features

*   Visualizes the Bitling simulation world based on data from the backend.
*   Renders Bitlings and environment objects.
    *   **(Placeholder Graphics): Currently uses emojis to represent Bitlings and objects based on their state/type.**
*   Provides a user interface (UI) for monitoring Bitling needs (hunger, energy, etc.) and world status.
*   Allows user interaction:
    *   Scrolling/panning the large world view.
    *   Adding food or other items to the environment.
    *   Potentially interacting directly with Bitlings (petting, talking via text input).
*   Communicates user actions back to the backend via WebSockets.

## Tech Stack

*   **Package Manager/Runtime:** Bun (or Node.js/npm/pnpm/yarn)
*   **Build Tool:** Vite (or directly via Bun)
*   **Language:** TypeScript
*   **Graphics Library:** [PixiJS recommended, but choose one: `pixi.js`, `phaser`, `konva`]
*   **Framework (Optional):** [React, Vue, Svelte, or Vanilla TS]
*   **Communication:** Native WebSocket API (or libraries like `socket.io-client`)

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>/frontend
    ```
2.  **Install dependencies:**
    ```bash
    # Using Bun
    bun install

    # Or using npm
    # npm install

    # Or using pnpm
    # pnpm install
    ```
3.  **Configure Backend Connection:**
    *   Ensure the WebSocket URL in the frontend code (e.g., in a config file or environment variable) points to your running backend server (e.g., `ws://localhost:8000`).
    
4.  **Run the development server:**
    ```bash
    # Using Bun with Vite config
    bun run dev

    # Or using npm with Vite
    # npm run dev

    # Or using pnpm with Vite
    # pnpm dev
    ```
    This will start the Vite development server, usually accessible at `http://localhost:5173` (check console output).

## Project Structure (Example using Vite + Vanilla TS)

    

```plaintext

frontend/
├── node_modules/ # Dependencies
├── public/ # Static assets (e.g., index.html base, maybe actual assets later)
│ └── index.html
├── src/ # Main source code
│ ├── assets/ # (Empty for now, will hold real graphics)
│ ├── network/ # WebSocket client logic
│ │ └── websocketClient.ts
│ ├── rendering/ # Graphics rendering logic (PixiJS specific)
│ │ ├── renderer.ts
│ │ ├── spriteManager.ts
│ │ └── worldView.ts
│ ├── simulation/ # Frontend representation of sim state
│ │ └── state.ts
│ ├── ui/ # UI components (status bars, buttons)
│ │ └── hud.ts
│ └── main.ts # Application entry point
├── index.html # Entry HTML (often minimal with Vite)
├── package.json # Project metadata and dependencies
├── tsconfig.json # TypeScript configuration
├── vite.config.ts # Vite build tool configuration
└── README.md # This file

```

      
## Future Plans

*   Replace emoji placeholders with actual sprite assets and animations.
*   Implement smooth scrolling and zooming for the large world.
*   Develop richer UI elements for interaction and monitoring.
*   Add visual effects (particles, etc.).
*   Optimize rendering performance for many Bitlings.
*   Implement text input interface for communication.