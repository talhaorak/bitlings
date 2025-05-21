// src/ui/hud.ts
import { websocketClient } from '../network/websocketClient';
import { Renderer } from '../rendering/renderer';
import { SimulationState } from '../simulation/state';

export function setupUI(ws: websocketClient, renderer: Renderer, state: SimulationState) {
    const addFoodButton = document.getElementById('add-food-button');
    const canvas = renderer['app'].canvas; // Access canvas (might need cleaner way)

    if (!addFoodButton || !canvas) {
        console.error('UI elements not found!');
        return;
    }

    let isAddingFood = false;

    addFoodButton.onclick = () => {
        isAddingFood = !isAddingFood; // Toggle mode
        addFoodButton.textContent = isAddingFood ? 'Adding Food (Click Canvas)' : 'Add Food (Click Canvas)';
        addFoodButton.style.backgroundColor = isAddingFood ? '#4CAF50' : ''; // Indicate active mode
        console.log("Add food mode:", isAddingFood);
    };

    canvas.addEventListener('click', (event) => {
        if (!isAddingFood) return; // Only add food if in the correct mode

        if (!ws.isConnected()) {
            console.warn("Cannot add food, WebSocket not connected.");
            alert("Not connected to server!");
            return;
        }

        const rect = canvas.getBoundingClientRect();
        const screenX = event.clientX - rect.left;
        const screenY = event.clientY - rect.top;

        // Convert screen coordinates to world coordinates using the renderer
        const worldCoords = renderer.getWorldCoordinates(screenX, screenY);

        console.log(`User clicked at screen (${screenX}, ${screenY}), world (${worldCoords.x}, ${worldCoords.y}) to add food.`);

        // Send message to backend
        ws.sendMessage({
            type: "user_action",
            payload: {
                action: "add_food",
                x: worldCoords.x,
                y: worldCoords.y
            }
        });

        // Optional: Deactivate add food mode after one click
        // isAddingFood = false;
        // addFoodButton.textContent = 'Add Food (Click Canvas)';
        // addFoodButton.style.backgroundColor = '';
    });

    // Update UI elements based on state changes (can be expanded)
    // Example: Could use a more robust way than polling/direct manipulation later
    // setInterval(() => {
    //    document.getElementById('bitling-count')!.textContent = String(state.world.bitlings.length);
    // }, 1000); // Update count every second (the websocket handler already does this)
}