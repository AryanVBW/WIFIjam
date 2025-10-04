/**
 * Mock API for WIFIjam Dashboard Demo
 * This simulates backend responses for demonstration purposes
 */

class MockAPI {
    constructor() {
        this.isConnected = false;
        this.callbacks = new Map();
        this.mockData = {
            systemInfo: {
                os: 'Linux Ubuntu 22.04.3 LTS',
                adapter: 'Intel WiFi 6 AX200 (Monitor Capable)',
                monitorMode: true,
                interfaces: [
                    'wlan0 - Intel WiFi 6 AX200',
                    'wlan1 - USB WiFi Adapter',
                    'wlp2s0 - Realtek RTL8821CE'
                ]
            },
            networks: [],
            attackStatus: {
                active: false,
                target: null,
                progress: 0,
                type: null
            }
        };
        
        this.init();
    }

    init() {
        // Simulate connection establishment
        setTimeout(() => {
            this.isConnected = true;
            this.emit('connected', { status: 'Connected to WIFIjam backend' });
            this.startPeriodicUpdates();
        }, 1000);
    }

    // Event system for WebSocket-like behavior
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
    async getSystemInfo() {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    data: this.mockData.systemInfo
                });
            }, 500);
        });
    }

    async getNetworks() {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    data: this.mockData.networks
                });
            }, 300);
        });
    }

    async startScan(options = {}) {
        return new Promise((resolve) => {
            setTimeout(() => {
                this.simulateNetworkDiscovery();
                resolve({
                    success: true,
                    message: 'Network scan started'
                });
            }, 200);
        });
    }

    async stopScan() {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: 'Network scan stopped'
                });
            }, 200);
        });
    }

    async selectTarget(bssid) {
        return new Promise((resolve) => {
            const network = this.mockData.networks.find(n => n.bssid === bssid);
            if (network) {
                this.mockData.attackStatus.target = network;
                resolve({
                    success: true,
                    message: `Target selected: ${network.ssid}`,
                    data: network
                });
            } else {
                resolve({
                    success: false,
                    message: 'Network not found'
                });
            }
        });
    }

    async startAttack(config) {
        return new Promise((resolve) => {
            if (!this.mockData.attackStatus.target) {
                resolve({
                    success: false,
                    message: 'No target selected'
                });
                return;
            }

            setTimeout(() => {
                this.mockData.attackStatus.active = true;
                this.mockData.attackStatus.type = config.type;
                this.mockData.attackStatus.progress = 0;
                
                this.simulateAttackProgress(config);
                
                resolve({
                    success: true,
                    message: `${config.type} attack started`
                });
            }, 300);
        });
    }

    async stopAttack() {
        return new Promise((resolve) => {
            setTimeout(() => {
                this.mockData.attackStatus.active = false;
                this.mockData.attackStatus.progress = 0;
                
                resolve({
                    success: true,
                    message: 'Attack stopped'
                });
            }, 200);
        });
    }

    async emergencyStop() {
        return new Promise((resolve) => {
            setTimeout(() => {
                this.mockData.attackStatus.active = false;
                this.mockData.attackStatus.progress = 0;
                
                resolve({
                    success: true,
                    message: 'Emergency stop executed'
                });
            }, 100);
        });
    }

    async updateConfiguration(config) {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: 'Configuration updated'
                });
            }, 300);
        });
    }

    async getLogs(options = {}) {
        return new Promise((resolve) => {
            const mockLogs = [
                { timestamp: new Date().toISOString(), level: 'info', message: 'System initialized' },
                { timestamp: new Date().toISOString(), level: 'success', message: 'Network interfaces detected' },
                { timestamp: new Date().toISOString(), level: 'info', message: 'Monitor mode available' }
            ];

            setTimeout(() => {
                resolve({
                    success: true,
                    data: mockLogs
                });
            }, 200);
        });
    }

    // Simulation methods
    simulateNetworkDiscovery() {
        const mockNetworks = [
            { ssid: 'HomeWiFi_2.4G', bssid: '00:1A:2B:3C:4D:5E', channel: 6, security: 'WPA2', signal: 85, vendor: 'TP-Link' },
            { ssid: 'OfficeNet', bssid: '00:1A:2B:3C:4D:5F', channel: 1, security: 'WPA3', signal: 72, vendor: 'Cisco' },
            { ssid: 'GuestNetwork', bssid: '00:1A:2B:3C:4D:60', channel: 11, security: 'Open', signal: 68, vendor: 'Netgear' },
            { ssid: 'MobileHotspot', bssid: '00:1A:2B:3C:4D:61', channel: 6, security: 'WPA2', signal: 45, vendor: 'Samsung' },
            { ssid: 'Coffee_Shop_WiFi', bssid: '00:1A:2B:3C:4D:62', channel: 1, security: 'Open', signal: 38, vendor: 'Ubiquiti' },
            { ssid: 'NETGEAR_5G', bssid: '00:1A:2B:3C:4D:63', channel: 36, security: 'WPA2', signal: 55, vendor: 'Netgear' }
        ];

        // Add networks gradually
        let index = 0;
        const addNetwork = () => {
            if (index < mockNetworks.length) {
                const network = mockNetworks[index];
                
                // Avoid duplicates
                if (!this.mockData.networks.some(n => n.bssid === network.bssid)) {
                    this.mockData.networks.push(network);
                    this.emit('networkDiscovered', network);
                }
                
                index++;
                setTimeout(addNetwork, 1500 + Math.random() * 2000);
            }
        };

        setTimeout(addNetwork, 1000);
    }

    simulateAttackProgress(config) {
        if (!this.mockData.attackStatus.active) return;

        const totalPackets = config.packetCount || 100;
        let sentPackets = 0;

        const updateProgress = () => {
            if (!this.mockData.attackStatus.active) return;

            const increment = Math.floor(Math.random() * 10) + 1;
            sentPackets = Math.min(sentPackets + increment, totalPackets);
            
            this.mockData.attackStatus.progress = (sentPackets / totalPackets) * 100;
            
            this.emit('attackProgress', {
                progress: this.mockData.attackStatus.progress,
                sentPackets,
                totalPackets
            });

            if (sentPackets >= totalPackets) {
                this.mockData.attackStatus.active = false;
                this.emit('attackCompleted', {
                    message: 'Attack sequence completed'
                });
            } else {
                setTimeout(updateProgress, 100 + Math.random() * 200);
            }
        };

        updateProgress();
    }

    startPeriodicUpdates() {
        // Simulate periodic system updates
        setInterval(() => {
            if (this.isConnected) {
                // Update signal strengths
                this.mockData.networks.forEach(network => {
                    const change = (Math.random() - 0.5) * 10;
                    network.signal = Math.max(10, Math.min(100, network.signal + change));
                });

                this.emit('networksUpdated', this.mockData.networks);
            }
        }, 5000);

        // Simulate random system events
        setInterval(() => {
            if (this.isConnected && Math.random() < 0.3) {
                const events = [
                    { level: 'info', message: 'Channel hopping completed' },
                    { level: 'info', message: 'Interface statistics updated' },
                    { level: 'warning', message: 'High interference detected on channel 6' },
                    { level: 'success', message: 'Monitor mode verified' }
                ];

                const event = events[Math.floor(Math.random() * events.length)];
                this.emit('systemEvent', {
                    timestamp: new Date().toISOString(),
                    ...event
                });
            }
        }, 8000);
    }
}

// Enhanced Dashboard with API Integration
if (typeof window !== 'undefined' && window.dashboard) {
    // Extend the existing dashboard with API functionality
    window.dashboard.api = new MockAPI();

    // Wire up API events
    window.dashboard.api.on('connected', (data) => {
        window.dashboard.addActivity(data.status, 'success');
    });

    window.dashboard.api.on('networkDiscovered', (network) => {
        window.dashboard.addNetwork(network);
        window.dashboard.addActivity(`Discovered: ${network.ssid}`, 'success');
    });

    window.dashboard.api.on('networksUpdated', (networks) => {
        if (window.dashboard.config.realTimeUpdates) {
            window.dashboard.networks = networks;
            window.dashboard.updateNetworksTable();
        }
    });

    window.dashboard.api.on('attackProgress', (data) => {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        if (progressFill) progressFill.style.width = `${data.progress}%`;
        if (progressText) progressText.textContent = `${data.sentPackets}/${data.totalPackets} packets sent (${data.progress.toFixed(1)}%)`;
    });

    window.dashboard.api.on('attackCompleted', (data) => {
        window.dashboard.addActivity(data.message, 'success');
        window.dashboard.showNotification('Attack Completed', data.message, 'success');
        window.dashboard.attackActive = false;
        document.getElementById('startAttack').disabled = false;
        document.getElementById('stopAttack').disabled = true;
    });

    window.dashboard.api.on('systemEvent', (event) => {
        window.dashboard.addActivity(event.message, event.level);
    });

    // Override some dashboard methods to use API
    const originalToggleScanning = window.dashboard.toggleScanning;
    window.dashboard.toggleScanning = async function() {
        if (!this.scanningActive) {
            const result = await this.api.startScan();
            if (result.success) {
                originalToggleScanning.call(this);
            } else {
                this.showNotification('Scan Failed', result.message, 'error');
            }
        } else {
            await this.api.stopScan();
            originalToggleScanning.call(this);
        }
    };

    const originalStartAttack = window.dashboard.startAttack;
    window.dashboard.startAttack = async function() {
        if (!this.selectedTarget || this.attackActive) return;

        const config = {
            type: document.getElementById('attackType').value,
            packetCount: parseInt(document.getElementById('packetCount').value),
            delay: parseInt(document.getElementById('packetDelay').value)
        };

        const result = await this.api.startAttack(config);
        if (result.success) {
            originalStartAttack.call(this);
        } else {
            this.showNotification('Attack Failed', result.message, 'error');
        }
    };

    const originalStopAttack = window.dashboard.stopAttack;
    window.dashboard.stopAttack = async function() {
        await this.api.stopAttack();
        originalStopAttack.call(this);
    };

    const originalSelectTarget = window.dashboard.selectTarget;
    window.dashboard.selectTarget = async function(bssid) {
        const result = await this.api.selectTarget(bssid);
        if (result.success) {
            originalSelectTarget.call(this, bssid);
        } else {
            this.showNotification('Target Selection Failed', result.message, 'error');
        }
    };

    console.log('✅ WIFIjam Dashboard with Mock API initialized');
}
