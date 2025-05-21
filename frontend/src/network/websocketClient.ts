// src/network/websocketClient.ts
import { SimulationState } from "../simulation/state"

export class websocketClient {
    private url: string;
    private ws: WebSocket | null = null;
    private state: SimulationState;
    private reconnectInterval = 5000; // Try reconnecting every 5 seconds
    private reconnectTimer: number | null = null;

    constructor(url: string, state: SimulationState) {
        this.url = url;
        this.state = state;
    }

    connect() {
        console.log(`Attempting to connect to ${this.url}...`);
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('WebSocket connection established.');
            document.getElementById('status-text')!.textContent = 'Connected';
            if (this.reconnectTimer) {
                clearTimeout(this.reconnectTimer);
                this.reconnectTimer = null;
            }
            // Maybe request initial state or send a hello message?
            // this.sendMessage({ type: 'request_initial_state' });
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (error) {
                console.error('Failed to parse message or handle:', event.data, error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            // The onclose event will handle reconnection logic
        };

        this.ws.onclose = (event) => {
            console.warn(`WebSocket connection closed. Code: ${event.code}, Reason: ${event.reason}. Attempting to reconnect...`);
            document.getElementById('status-text')!.textContent = 'Disconnected. Reconnecting...';
            this.ws = null;
            if (!this.reconnectTimer) {
                this.reconnectTimer = window.setTimeout(() => {
                    this.connect();
                }, this.reconnectInterval);
            }
        };
    }

    private handleMessage(message: any) {
        // console.debug('Message received:', message);
        switch (message.type) {
            case 'world_update':
                this.state.updateWorld(message.payload);
                document.getElementById('bitling-count')!.textContent = String(message.payload.bitlings?.length || 0);
                break;
            case 'pong':
                console.log('Received pong');
                break;
            // Handle other message types from backend if needed
            default:
                console.warn(`Received unknown message type: ${message.type}`);
        }
    }

    sendMessage(data: object) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.error('WebSocket is not connected. Cannot send message:', data);
        }
    }

    isConnected(): boolean {
        return this.ws?.readyState === WebSocket.OPEN;
    }
}