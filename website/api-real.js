/**
 * Real API client for WIFIjam Dashboard
 * Connects to the Python backend API server
 */

class RealAPI {
    constructor(baseURL = 'http://localhost:8080') {
        this.baseURL = baseURL;
        this.ws = null;
        this.wsReconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.callbacks = new Map();
        this.isConnected = false;
        
        this.init();
    }

    init() {
        // Connect WebSocket
        this.connectWebSocket();
        
        // Test API connection
        this.testConnection();
    }

    // WebSocket Management
    connectWebSocket() {
        const wsURL = this.baseURL.replace('http', 'ws') + '/ws';
        
        try {
            this.ws = new WebSocket(wsURL);
            
            this.ws.onopen = () => {
                console.log('✅ WebSocket connected');
                this.isConnected = true;
                this.wsReconnectAttempts = 0;
                this.emit('connected', { status: 'Connected to WIFIjam backend' });
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.attemptReconnect();
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.attemptReconnect();
        }
    }

    attemptReconnect() {
        if (this.wsReconnectAttempts < this.maxReconnectAttempts) {
            this.wsReconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.wsReconnectAttempts), 30000);
            console.log(`Reconnecting WebSocket in ${delay}ms (attempt ${this.wsReconnectAttempts})`);
            setTimeout(() => this.connectWebSocket(), delay);
        } else {
            console.error('Max WebSocket reconnection attempts reached');
            this.emit('connectionFailed', { message: 'Failed to connect to server' });
        }
    }

    handleWebSocketMessage(data) {
        const { type, data: payload } = data;
        
        switch (type) {
            case 'connected':
                console.log('Server connection confirmed');
                break;
            case 'network_discovered':
                this.emit('networkDiscovered', payload);
                break;
            case 'attack_progress':
                this.emit('attackProgress', payload);
                break;
            case 'monitor_mode':
                this.emit('monitorMode', payload);
                break;
            case 'system_event':
                this.emit('systemEvent', payload);
                break;
            default:
                console.log('Unknown WebSocket message type:', type);
        }
    }

    // Event System
    on(event, callback) {
        if (!this.callbacks.has(event)) {
            this.callbacks.set(event, []);
        }
        this.callbacks.get(event).push(callback);
    }

    emit(event, data) {
        if (this.callbacks.has(event)) {
            this.callbacks.get(event).forEach(callback => callback(data));
        }
    }

    // API Methods
    async testConnection() {
        try {
            const response = await fetch(`${this.baseURL}/api/system/info`);
            if (response.ok) {
                console.log('✅ API server connected');
                return true;
            }
        } catch (error) {
            console.error('❌ API server not reachable:', error);
            return false;
        }
    }

    async getSystemInfo() {
        return this.request('GET', '/api/system/info');
    }

    async getDependencies() {
        return this.request('GET', '/api/system/dependencies');
    }

    async getAdapters() {
        return this.request('GET', '/api/adapters');
    }

    async getAdapter(interface) {
        return this.request('GET', `/api/adapters/${interface}`);
    }

    async selectAdapter(interface) {
        return this.request('POST', `/api/adapters/${interface}/select`);
    }

    async enableMonitorMode() {
        return this.request('POST', '/api/monitor/enable');
    }

    async disableMonitorMode() {
        return this.request('POST', '/api/monitor/disable');
    }

    async getMonitorStatus() {
        return this.request('GET', '/api/monitor/status');
    }

    async startScan(options = {}) {
        return this.request('POST', '/api/scan/start', options);
    }

    async stopScan() {
        return this.request('POST', '/api/scan/stop');
    }

    async getNetworks() {
        return this.request('GET', '/api/scan/networks');
    }

    async getScanStatus() {
        return this.request('GET', '/api/scan/status');
    }

    async startAttack(config) {
        return this.request('POST', '/api/attack/start', config);
    }

    async stopAttack() {
        return this.request('POST', '/api/attack/stop');
    }

    async getAttackStatus() {
        return this.request('GET', '/api/attack/status');
    }

    async getConfig() {
        return this.request('GET', '/api/config');
    }

    async updateConfig(config) {
        return this.request('POST', '/api/config', config);
    }

    async resetConfig() {
        return this.request('POST', '/api/config/reset');
    }

    // Helper Methods
    async request(method, endpoint, data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            if (data && (method === 'POST' || method === 'PUT')) {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.baseURL}${endpoint}`, options);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Request failed');
            }

            return result;
        } catch (error) {
            console.error(`API request failed: ${method} ${endpoint}`, error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Utility Methods
    sendWebSocketMessage(type, data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, data }));
        } else {
            console.warn('WebSocket not connected');
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

// Initialize API when dashboard loads
if (typeof window !== 'undefined' && window.dashboard) {
    window.dashboard.api = new RealAPI();

    // Wire up API events to dashboard
    window.dashboard.api.on('connected', (data) => {
        window.dashboard.addActivity(data.status, 'success');
    });

    window.dashboard.api.on('networkDiscovered', (network) => {
        window.dashboard.addNetwork(network);
        window.dashboard.addActivity(`Discovered: ${network.ssid}`, 'success');
    });

    window.dashboard.api.on('attackProgress', (data) => {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        if (progressFill && data.total > 0) {
            const progress = (data.sent / data.total) * 100;
            progressFill.style.width = `${progress}%`;
        }
        if (progressText) {
            progressText.textContent = `${data.sent}/${data.total} packets sent`;
        }
    });

    window.dashboard.api.on('monitorMode', (data) => {
        const status = data.enabled ? 'enabled' : 'disabled';
        window.dashboard.addActivity(`Monitor mode ${status}`, 'info');
    });

    window.dashboard.api.on('systemEvent', (event) => {
        window.dashboard.addActivity(event.message, event.level || 'info');
    });

    window.dashboard.api.on('connectionFailed', (data) => {
        window.dashboard.showNotification(
            'Connection Failed',
            'Failed to connect to WIFIjam server. Make sure the server is running.',
            'error'
        );
    });

    console.log('✅ Real API initialized');
}

