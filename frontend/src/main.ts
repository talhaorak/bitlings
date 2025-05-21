import * as PIXI from 'pixi.js';
import { websocketClient } from "./network/websocketClient"
import { Renderer } from "./rendering/renderer"
import { SimulationState } from "./simulation/state"
import { setupUI } from "./ui/hud"

// --- Configuration ---
const BACKEND_URL = 'ws://localhost:8765'; // Adjust if needed

// --- Initialization ---
console.log('Bitlings frontend initializing...');

// 1. Setup PixiJS Application
const app = new PIXI.Application();
await app.init({
  width: window.innerWidth,
  height: window.innerHeight,
  backgroundColor: 0x228B22, // Forest Green
  autoDensity: true,
  resolution: window.devicePixelRatio || 1,
  resizeTo: window, // Automatically resize canvas to window
});
document.getElementById('app')?.appendChild(app.canvas);
console.log('PixiJS Initialized');

// 2. Initialize Simulation State Holder
const simulationState = new SimulationState();

// 3. Initialize Renderer
const renderer = new Renderer(app, simulationState);
renderer.start(); // Start the rendering loop
console.log('Renderer Initialized');

// 4. Initialize WebSocket Client
const ws = new websocketClient(BACKEND_URL, simulationState);
ws.connect();
console.log('WebSocket Client Initializing');

// 5. Setup UI Interactions
// Pass necessary references (websocket, renderer, state) to the UI setup
setupUI(ws, renderer, simulationState);
console.log('UI Initialized');

// --- Global Access (Optional, for debugging) ---
// window.app = app;
// window.state = simulationState;
// window.ws = ws;

console.log('Bitlings frontend setup complete.');