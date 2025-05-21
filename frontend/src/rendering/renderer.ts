// src/rendering/renderer.ts
import * as PIXI from 'pixi.js';
import { SimulationState, BitlingState, FoodState } from '../simulation/state';

export class Renderer {
    private app: PIXI.Application;
    private state: SimulationState;
    private bitlingSprites: Map<string, PIXI.Text> = new Map();
    private foodSprites: Map<string, PIXI.Text> = new Map();
    private worldContainer: PIXI.Container; // To allow panning/zooming later

    constructor(app: PIXI.Application, state: SimulationState) {
        this.app = app;
        this.state = state;

        // Create a container for all world objects
        this.worldContainer = new PIXI.Container();
        this.app.stage.addChild(this.worldContainer);
    }

    start() {
        this.app.ticker.add(this.renderLoop.bind(this));
    }

    stop() {
        this.app.ticker.remove(this.renderLoop.bind(this));
    }

    private renderLoop(ticker: PIXI.Ticker) {
        this.updateSprites(this.state.world.bitlings, this.bitlingSprites);
        this.updateSprites(this.state.world.food, this.foodSprites);

        // Note: PixiJS v8 ticker might pass Ticker instance, v7 passed delta time
        // We don't strictly need delta time here as positions are set directly from state
    }

    private updateSprites<T extends { id: string; x: number; y: number; emoji: string }>(
        items: T[],
        spriteMap: Map<string, PIXI.Text>
    ) {
        const currentIds = new Set<string>();

        // Update existing and add new sprites
        for (const item of items) {
            currentIds.add(item.id);
            let sprite = spriteMap.get(item.id);

            if (sprite) {
                // Update existing sprite
                sprite.x = item.x;
                sprite.y = item.y;
                if (sprite.text !== item.emoji) {
                    sprite.text = item.emoji;
                }
            } else {
                // Create new sprite
                sprite = new PIXI.Text({
                    text: item.emoji,
                    style: { fontSize: 20 } // Adjust size as needed
                });
                sprite.anchor.set(0.5); // Center the emoji on its coordinates
                sprite.x = item.x;
                sprite.y = item.y;
                this.worldContainer.addChild(sprite); // Add to the container
                spriteMap.set(item.id, sprite);
            }
        }

        // Remove old sprites
        for (const id of spriteMap.keys()) {
            if (!currentIds.has(id)) {
                const spriteToRemove = spriteMap.get(id);
                if (spriteToRemove) {
                    this.worldContainer.removeChild(spriteToRemove);
                    spriteToRemove.destroy(); // Free memory
                }
                spriteMap.delete(id);
            }
        }
    }

    // --- Interaction Methods ---
    // Get world coordinates from screen coordinates (needed for clicking)
    getWorldCoordinates(screenX: number, screenY: number): { x: number; y: number } {
        // For now, assume no camera panning/zooming
        // Later, this needs to account for worldContainer position and scale
        const worldPoint = this.worldContainer.toLocal(new PIXI.Point(screenX, screenY));
        return { x: worldPoint.x, y: worldPoint.y };
    }
}