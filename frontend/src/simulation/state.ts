// src/simulation/state.ts

// Define interfaces for the data coming from the backend
export interface BitlingState {
    id: string;
    x: number;
    y: number;
    emoji: string;
    action: string;
    // Add other properties if needed (health, hunger for UI?)
}

export interface FoodState {
    id: string;
    x: number;
    y: number;
    emoji: string;
}

export interface WorldState {
    bitlings: BitlingState[];
    food: FoodState[];
    // Add other potential world objects (trees, rocks) later
}

export class SimulationState {
    public world: WorldState = {
        bitlings: [],
        food: [],
    };

    updateWorld(newState: WorldState) {
        // Directly replace state for now.
        // Later, could implement more granular updates if needed for performance.
        this.world = newState;
        // console.log("World state updated:", this.world);
    }
}