/**
 * WIFIjam Dashboard JavaScript
 * Handles all frontend interactions and real-time updates
 */

class WIFIjamDashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.scanningActive = false;
        this.attackActive = false;
        this.selectedTarget = null;
        this.networks = [];
        this.logs = [];
        this.config = {
            theme: 'dark',
            realTimeUpdates: true,
            soundNotifications: false,
            autoSaveLogs: true,
            defaultPacketCount: 100,
            defaultDelay: 100
        };
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadConfiguration();
        this.startSystemStatusCheck();
        this.hideLoadingOverlay();
        this.setupNotificationSystem();
        this.initializeCharts();
        this.simulateSystemInfo();
        
        // Add some demo activity
        setTimeout(() => {
            this.addActivity('System initialized successfully', 'success');
            this.addActivity('WiFi interfaces detected', 'info');
            this.addActivity('Monitor mode capabilities checked', 'info');
        }, 1000);
    }

    bindEvents() {
        // Sidebar navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                this.switchSection(section);
            });
        });

        // Sidebar toggle for mobile
        document.getElementById('sidebarToggle')?.addEventListener('click', () => {
            document.querySelector('.dashboard-sidebar').classList.toggle('open');
        });

        // Quick actions
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleQuickAction(action);
            });
        });

        // Scanner controls
        document.getElementById('scanToggle')?.addEventListener('click', () => {
            this.toggleScanning();
        });

        document.getElementById('refreshNetworks')?.addEventListener('click', () => {
            this.refreshNetworks();
        });

        document.getElementById('exportNetworks')?.addEventListener('click', () => {
            this.exportNetworks();
        });

        // Attack controls
        document.getElementById('startAttack')?.addEventListener('click', () => {
            this.startAttack();
        });

        document.getElementById('stopAttack')?.addEventListener('click', () => {
            this.stopAttack();
        });

        document.getElementById('testAttack')?.addEventListener('click', () => {
            this.testAttack();
        });

        document.getElementById('emergencyStop')?.addEventListener('click', () => {
            this.emergencyStop();
        });

        // Configuration
        document.getElementById('saveConfig')?.addEventListener('click', () => {
            this.saveConfiguration();
        });

        document.getElementById('resetConfig')?.addEventListener('click', () => {
            this.resetConfiguration();
        });

        // Log controls
        document.getElementById('clearLogs')?.addEventListener('click', () => {
            this.clearLogs();
        });

        document.getElementById('downloadLogs')?.addEventListener('click', () => {
            this.downloadLogs();
        });

        document.getElementById('clearActivity')?.addEventListener('click', () => {
            this.clearActivity();
        });

        // Help topics
        document.querySelectorAll('.help-topic').forEach(topic => {
            topic.addEventListener('click', (e) => {
                const topicName = e.currentTarget.dataset.topic;
                this.showHelpTopic(topicName);
            });
        });

        // Form change handlers
        document.getElementById('attackType')?.addEventListener('change', (e) => {
            this.updateAttackParams(e.target.value);
        });

        // OS tabs (if on installation page)
        document.querySelectorAll('.os-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchOSTab(e.target.dataset.tab);
            });
        });

        // Copy buttons
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.copyToClipboard(e.target);
            });
        });
    }

    switchSection(sectionName) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionName}-section`).classList.add('active');

        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            scanner: 'Network Scanner',
            attack: 'Attack Panel',
            config: 'Configuration',
            logs: 'System Logs',
            help: 'Help & Documentation'
        };
        
        document.getElementById('pageTitle').textContent = titles[sectionName] || sectionName;
        this.currentSection = sectionName;

        // Section-specific initialization
        if (sectionName === 'scanner') {
            this.loadNetworkInterfaces();
        } else if (sectionName === 'config') {
            this.loadConfigurationForm();
        }
    }

    handleQuickAction(action) {
        switch (action) {
            case 'scan':
                this.switchSection('scanner');
                setTimeout(() => this.toggleScanning(), 500);
                break;
            case 'monitor':
                this.toggleMonitorMode();
                break;
            case 'config':
                this.switchSection('config');
                break;
            case 'help':
                this.switchSection('help');
                break;
        }
    }

    toggleScanning() {
        const scanBtn = document.getElementById('scanToggle');
        const scanIcon = scanBtn.querySelector('i');
        
        if (!this.scanningActive) {
            this.scanningActive = true;
            scanBtn.classList.add('scanning');
            scanBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Scan';
            
            this.addActivity('Network scanning started', 'info');
            this.showNotification('Scanning Started', 'Network scanning in progress...', 'info');
            
            // Simulate network discovery
            this.simulateNetworkScan();
        } else {
            this.scanningActive = false;
            scanBtn.classList.remove('scanning');
            scanBtn.innerHTML = '<i class="fas fa-play"></i> Start Scan';
            
            this.addActivity('Network scanning stopped', 'info');
            this.showNotification('Scanning Stopped', 'Network scanning has been stopped.', 'info');
        }
    }

    simulateNetworkScan() {
        if (!this.scanningActive) return;

        const mockNetworks = [
            { ssid: 'HomeWiFi_2.4G', bssid: '00:1A:2B:3C:4D:5E', channel: 6, security: 'WPA2', signal: 85 },
            { ssid: 'OfficeNet', bssid: '00:1A:2B:3C:4D:5F', channel: 1, security: 'WPA3', signal: 72 },
            { ssid: 'GuestNetwork', bssid: '00:1A:2B:3C:4D:60', channel: 11, security: 'Open', signal: 68 },
            { ssid: 'MobileHotspot', bssid: '00:1A:2B:3C:4D:61', channel: 6, security: 'WPA2', signal: 45 },
            { ssid: 'Coffee_Shop_WiFi', bssid: '00:1A:2B:3C:4D:62', channel: 1, security: 'Open', signal: 38 }
        ];

        // Add networks gradually
        let networkIndex = 0;
        const addNetwork = () => {
            if (networkIndex < mockNetworks.length && this.scanningActive) {
                const network = mockNetworks[networkIndex];
                this.addNetwork(network);
                this.addActivity(`Discovered network: ${network.ssid}`, 'success');
                networkIndex++;
                
                setTimeout(addNetwork, 2000 + Math.random() * 3000);
            }
        };

        addNetwork();
    }

    addNetwork(network) {
        // Avoid duplicates
        if (this.networks.some(n => n.bssid === network.bssid)) return;

        this.networks.push(network);
        this.updateNetworksTable();
        this.updateNetworkStats();
        this.updateHeaderStats();
    }

    updateNetworksTable() {
        const tbody = document.getElementById('networksTableBody');
        const noNetworksMsg = document.getElementById('noNetworksMessage');
        
        if (this.networks.length === 0) {
            tbody.innerHTML = '';
            noNetworksMsg.style.display = 'block';
            return;
        }

        noNetworksMsg.style.display = 'none';
        
        tbody.innerHTML = this.networks.map(network => `
            <tr>
                <td>
                    <strong>${network.ssid}</strong>
                    ${network.security === 'Open' ? '<i class="fas fa-exclamation-triangle" style="color: var(--accent-warning); margin-left: 5px;" title="Open Network"></i>' : ''}
                </td>
                <td><code>${network.bssid}</code></td>
                <td>${network.channel}</td>
                <td>
                    <span class="security-badge ${network.security.toLowerCase().replace(/[^a-z]/g, '')}">${network.security}</span>
                </td>
                <td>
                    <div class="signal-bar">
                        <div class="signal-strength">
                            ${this.generateSignalBars(network.signal)}
                        </div>
                        <span>${network.signal}%</span>
                    </div>
                </td>
                <td>
                    <div class="network-actions">
                        <button class="network-btn" onclick="dashboard.selectTarget('${network.bssid}')">
                            <i class="fas fa-crosshairs"></i> Target
                        </button>
                        <button class="network-btn" onclick="dashboard.showNetworkDetails('${network.bssid}')">
                            <i class="fas fa-info"></i> Details
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    generateSignalBars(strength) {
        const bars = 5;
        const activeBars = Math.ceil((strength / 100) * bars);
        let html = '';
        
        for (let i = 0; i < bars; i++) {
            const isActive = i < activeBars;
            html += `<div class="signal-bar-item ${isActive ? 'active' : ''}"></div>`;
        }
        
        return html;
    }

    selectTarget(bssid) {
        const network = this.networks.find(n => n.bssid === bssid);
        if (!network) return;

        this.selectedTarget = network;
        this.updateTargetDisplay();
        this.switchSection('attack');
        
        this.showNotification('Target Selected', `${network.ssid} has been selected as target.`, 'success');
        this.addActivity(`Target selected: ${network.ssid} (${network.bssid})`, 'info');
    }

    updateTargetDisplay() {
        const targetInfo = document.getElementById('targetInfo');
        
        if (!this.selectedTarget) {
            targetInfo.innerHTML = `
                <div class="no-target">
                    <i class="fas fa-bullseye"></i>
                    <p>No target selected. Choose a network from the scanner.</p>
                </div>
            `;
            document.getElementById('startAttack').disabled = true;
            return;
        }

        const target = this.selectedTarget;
        targetInfo.innerHTML = `
            <div class="target-details">
                <div class="target-item">
                    <span class="target-label">SSID</span>
                    <span class="target-value">${target.ssid}</span>
                </div>
                <div class="target-item">
                    <span class="target-label">BSSID</span>
                    <span class="target-value">${target.bssid}</span>
                </div>
                <div class="target-item">
                    <span class="target-label">Channel</span>
                    <span class="target-value">${target.channel}</span>
                </div>
                <div class="target-item">
                    <span class="target-label">Security</span>
                    <span class="target-value">
                        <span class="security-badge ${target.security.toLowerCase().replace(/[^a-z]/g, '')}">${target.security}</span>
                    </span>
                </div>
                <div class="target-item">
                    <span class="target-label">Signal Strength</span>
                    <span class="target-value">${target.signal}%</span>
                </div>
            </div>
        `;
        
        document.getElementById('startAttack').disabled = false;
    }

    startAttack() {
        if (!this.selectedTarget || this.attackActive) return;

        const attackType = document.getElementById('attackType').value;
        const packetCount = document.getElementById('packetCount').value;
        const delay = document.getElementById('packetDelay').value;

        this.attackActive = true;
        document.getElementById('startAttack').disabled = true;
        document.getElementById('stopAttack').disabled = false;

        this.addActivity(`Attack started: ${attackType} on ${this.selectedTarget.ssid}`, 'warning');
        this.showNotification('Attack Started', `${attackType} attack initiated on ${this.selectedTarget.ssid}`, 'warning');

        // Simulate attack progress
        this.simulateAttackProgress(packetCount);
    }

    simulateAttackProgress(totalPackets) {
        let sentPackets = 0;
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        const updateProgress = () => {
            if (!this.attackActive) return;

            sentPackets += Math.floor(Math.random() * 10) + 1;
            const progress = Math.min((sentPackets / totalPackets) * 100, 100);
            
            progressFill.style.width = `${progress}%`;
            progressText.textContent = `${sentPackets}/${totalPackets} packets sent (${progress.toFixed(1)}%)`;

            if (sentPackets >= totalPackets) {
                this.stopAttack();
                this.showNotification('Attack Completed', 'Attack sequence completed successfully.', 'success');
            } else {
                setTimeout(updateProgress, 100 + Math.random() * 200);
            }
        };

        updateProgress();
    }

    stopAttack() {
        if (!this.attackActive) return;

        this.attackActive = false;
        document.getElementById('startAttack').disabled = false;
        document.getElementById('stopAttack').disabled = true;

        const progressText = document.getElementById('progressText');
        progressText.textContent = 'Attack stopped';

        this.addActivity('Attack stopped by user', 'info');
        this.showNotification('Attack Stopped', 'Attack has been stopped.', 'info');
    }

    testAttack() {
        this.showNotification('Test Mode', 'Attack configuration test completed successfully.', 'success');
        this.addActivity('Attack configuration tested', 'info');
    }

    emergencyStop() {
        this.attackActive = false;
        this.scanningActive = false;
        
        // Reset all controls
        document.getElementById('startAttack').disabled = false;
        document.getElementById('stopAttack').disabled = true;
        
        const scanBtn = document.getElementById('scanToggle');
        if (scanBtn) {
            scanBtn.classList.remove('scanning');
            scanBtn.innerHTML = '<i class="fas fa-play"></i> Start Scan';
        }

        this.addActivity('EMERGENCY STOP activated - All operations halted', 'error');
        this.showNotification('Emergency Stop', 'All operations have been halted immediately.', 'error');
    }

    updateNetworkStats() {
        const wpaCount = this.networks.filter(n => n.security.includes('WPA')).length;
        const wepCount = this.networks.filter(n => n.security === 'WEP').length;
        const openCount = this.networks.filter(n => n.security === 'Open').length;
        const total = this.networks.length;

        document.getElementById('wpaCount').textContent = wpaCount;
        document.getElementById('wepCount').textContent = wepCount;
        document.getElementById('openCount').textContent = openCount;

        // Update security chart
        const securityChart = document.getElementById('securityChart');
        const securedPercent = total > 0 ? Math.round(((wpaCount) / total) * 100) : 0;
        
        securityChart.querySelector('.stat-number').textContent = `${securedPercent}%`;
        
        // Update circle progress (simplified version)
        const degree = (securedPercent / 100) * 360;
        securityChart.style.background = `conic-gradient(var(--accent-primary) ${degree}deg, var(--border-color) ${degree}deg)`;
    }

    updateHeaderStats() {
        document.getElementById('networkCount').textContent = this.networks.length;
        document.getElementById('targetCount').textContent = this.selectedTarget ? 1 : 0;
    }

    addActivity(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const activity = { timestamp, message, type };
        
        this.logs.unshift(activity);
        
        // Keep only last 50 activities
        if (this.logs.length > 50) {
            this.logs = this.logs.slice(0, 50);
        }
        
        this.updateActivityFeed();
        this.addLogEntry(message, type);
    }

    updateActivityFeed() {
        const activityList = document.getElementById('activityList');
        
        activityList.innerHTML = this.logs.slice(0, 10).map(activity => `
            <div class="activity-item ${activity.type}">
                <div class="activity-time">${activity.timestamp}</div>
                <div class="activity-message">${activity.message}</div>
                <div class="activity-status ${activity.type}">
                    <i class="fas fa-${this.getActivityIcon(activity.type)}"></i>
                </div>
            </div>
        `).join('');
    }

    getActivityIcon(type) {
        const icons = {
            success: 'check',
            warning: 'exclamation-triangle',
            error: 'times',
            info: 'info'
        };
        return icons[type] || 'circle';
    }

    clearActivity() {
        this.logs = [];
        this.updateActivityFeed();
        this.showNotification('Activity Cleared', 'Activity feed has been cleared.', 'info');
    }

    addLogEntry(message, level = 'info') {
        const logViewer = document.getElementById('logViewer');
        const timestamp = new Date().toLocaleString();
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${level}`;
        logEntry.innerHTML = `
            <span class="log-time">${timestamp}</span>
            <span class="log-level">${level.toUpperCase()}</span>
            <span class="log-message">${message}</span>
        `;
        
        logViewer.appendChild(logEntry);
        
        // Auto-scroll if enabled
        if (document.getElementById('autoScroll')?.checked) {
            logViewer.scrollTop = logViewer.scrollHeight;
        }
        
        // Keep only last 1000 log entries
        const logEntries = logViewer.querySelectorAll('.log-entry');
        if (logEntries.length > 1000) {
            logEntries[0].remove();
        }
    }

    clearLogs() {
        document.getElementById('logViewer').innerHTML = '';
        this.showNotification('Logs Cleared', 'System logs have been cleared.', 'info');
    }

    downloadLogs() {
        const logEntries = document.querySelectorAll('.log-entry');
        let logContent = 'WIFIjam System Logs\n';
        logContent += '==================\n\n';
        
        logEntries.forEach(entry => {
            const time = entry.querySelector('.log-time').textContent;
            const level = entry.querySelector('.log-level').textContent;
            const message = entry.querySelector('.log-message').textContent;
            logContent += `[${time}] ${level}: ${message}\n`;
        });
        
        this.downloadFile('wifijam-logs.txt', logContent);
        this.showNotification('Download Started', 'System logs are being downloaded.', 'success');
    }

    downloadFile(filename, content) {
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    exportNetworks() {
        if (this.networks.length === 0) {
            this.showNotification('No Data', 'No networks to export.', 'warning');
            return;
        }

        const csvContent = 'SSID,BSSID,Channel,Security,Signal\n' +
            this.networks.map(n => `"${n.ssid}","${n.bssid}",${n.channel},"${n.security}",${n.signal}`).join('\n');
        
        this.downloadFile('networks.csv', csvContent);
        this.showNotification('Export Started', 'Network data is being exported.', 'success');
    }

    refreshNetworks() {
        this.networks = [];
        this.updateNetworksTable();
        this.updateNetworkStats();
        this.updateHeaderStats();
        
        this.showNotification('Networks Cleared', 'Network list has been refreshed.', 'info');
        this.addActivity('Network list refreshed', 'info');
    }

    showNetworkDetails(bssid) {
        const network = this.networks.find(n => n.bssid === bssid);
        if (!network) return;

        // In a real implementation, this would show a modal with detailed network information
        this.showNotification('Network Details', `Detailed information for ${network.ssid} would be displayed here.`, 'info');
    }

    loadNetworkInterfaces() {
        // Simulate loading network interfaces
        const interfaceSelect = document.getElementById('interfaceSelect');
        if (!interfaceSelect) return;

        const mockInterfaces = [
            'wlan0 - Intel WiFi 6 AX200',
            'wlan1 - USB WiFi Adapter',
            'wlp2s0 - Realtek RTL8821CE'
        ];

        interfaceSelect.innerHTML = '<option value="">Select WiFi Interface...</option>' +
            mockInterfaces.map(iface => `<option value="${iface}">${iface}</option>`).join('');
    }

    simulateSystemInfo() {
        // Simulate system information detection
        setTimeout(() => {
            document.getElementById('osInfo').textContent = 'Linux Ubuntu 22.04.3 LTS';
            document.getElementById('adapterInfo').textContent = 'Intel WiFi 6 AX200 (Monitor Capable)';
            document.getElementById('monitorMode').textContent = 'Supported';
        }, 2000);
    }

    toggleMonitorMode() {
        const monitorToggle = document.getElementById('monitorModeToggle');
        const isEnabled = monitorToggle?.checked;
        
        if (isEnabled) {
            this.addActivity('Monitor mode enabled', 'success');
            this.showNotification('Monitor Mode', 'Monitor mode has been enabled.', 'success');
        } else {
            this.addActivity('Monitor mode disabled', 'info');
            this.showNotification('Monitor Mode', 'Monitor mode has been disabled.', 'info');
        }
    }

    loadConfiguration() {
        // Load configuration from localStorage or use defaults
        const savedConfig = localStorage.getItem('wifijam-config');
        if (savedConfig) {
            this.config = { ...this.config, ...JSON.parse(savedConfig) };
        }
        
        this.applyConfiguration();
    }

    loadConfigurationForm() {
        // Populate configuration form with current values
        const elements = {
            'defaultPacketCount': this.config.defaultPacketCount,
            'defaultDelay': this.config.defaultDelay,
            'autoSaveLogs': this.config.autoSaveLogs,
            'realTimeUpdates': this.config.realTimeUpdates,
            'soundNotifications': this.config.soundNotifications,
            'themeSelect': this.config.theme
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (!element) return;

            if (element.type === 'checkbox') {
                element.checked = value;
            } else {
                element.value = value;
            }
        });
    }

    saveConfiguration() {
        // Read values from form
        const formData = {
            defaultPacketCount: parseInt(document.getElementById('defaultPacketCount')?.value) || 100,
            defaultDelay: parseInt(document.getElementById('defaultDelay')?.value) || 100,
            autoSaveLogs: document.getElementById('autoSaveLogs')?.checked || false,
            realTimeUpdates: document.getElementById('realTimeUpdates')?.checked || false,
            soundNotifications: document.getElementById('soundNotifications')?.checked || false,
            theme: document.getElementById('themeSelect')?.value || 'dark'
        };

        this.config = { ...this.config, ...formData };
        localStorage.setItem('wifijam-config', JSON.stringify(this.config));
        
        this.applyConfiguration();
        this.showNotification('Configuration Saved', 'Settings have been saved successfully.', 'success');
        this.addActivity('Configuration updated', 'info');
    }

    resetConfiguration() {
        this.config = {
            theme: 'dark',
            realTimeUpdates: true,
            soundNotifications: false,
            autoSaveLogs: true,
            defaultPacketCount: 100,
            defaultDelay: 100
        };
        
        localStorage.removeItem('wifijam-config');
        this.loadConfigurationForm();
        this.applyConfiguration();
        
        this.showNotification('Configuration Reset', 'Settings have been reset to defaults.', 'info');
        this.addActivity('Configuration reset to defaults', 'info');
    }

    applyConfiguration() {
        // Apply theme
        document.body.className = `theme-${this.config.theme}`;
        
        // Apply other settings
        if (this.config.realTimeUpdates) {
            this.startRealTimeUpdates();
        }
    }

    startRealTimeUpdates() {
        // Simulate real-time updates
        setInterval(() => {
            if (this.config.realTimeUpdates && this.scanningActive) {
                // Update signal strengths randomly
                this.networks.forEach(network => {
                    network.signal = Math.max(10, Math.min(100, network.signal + (Math.random() - 0.5) * 10));
                });
                this.updateNetworksTable();
            }
        }, 5000);
    }

    startSystemStatusCheck() {
        // Simulate system status monitoring
        setInterval(() => {
            const statusDot = document.querySelector('.status-dot');
            const statusText = document.querySelector('.status-text');
            
            // Randomly change status for demonstration
            const statuses = [
                { text: 'System Ready', class: 'ready', color: 'var(--accent-success)' },
                { text: 'Scanning...', class: 'scanning', color: 'var(--accent-primary)' },
                { text: 'Processing...', class: 'processing', color: 'var(--accent-warning)' }
            ];
            
            const currentStatus = this.scanningActive ? statuses[1] : 
                                this.attackActive ? statuses[2] : statuses[0];
            
            if (statusText) statusText.textContent = currentStatus.text;
            if (statusDot) statusDot.style.background = currentStatus.color;
        }, 3000);
    }

    showNotification(title, message, type = 'info') {
        const container = document.getElementById('notificationContainer');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            info: 'info-circle',
            success: 'check-circle',
            warning: 'exclamation-triangle',
            error: 'times-circle'
        };
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-${icons[type]}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
        
        // Play sound if enabled
        if (this.config.soundNotifications) {
            this.playNotificationSound(type);
        }
    }

    playNotificationSound(type) {
        // In a real implementation, this would play actual sound files
        console.log(`Playing ${type} notification sound`);
    }

    setupNotificationSystem() {
        // Request notification permission if supported
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            setTimeout(() => {
                overlay.style.opacity = '0';
                setTimeout(() => {
                    overlay.style.display = 'none';
                }, 300);
            }, 2000);
        }
    }

    updateAttackParams(attackType) {
        // Update attack parameters based on selected type
        const packetCountField = document.getElementById('packetCount');
        const delayField = document.getElementById('packetDelay');
        
        const presets = {
            deauth: { packets: 100, delay: 100 },
            jam24: { packets: 1000, delay: 50 },
            jam5: { packets: 1000, delay: 50 }
        };
        
        if (presets[attackType]) {
            packetCountField.value = presets[attackType].packets;
            delayField.value = presets[attackType].delay;
        }
        
        this.addActivity(`Attack type changed to: ${attackType}`, 'info');
    }

    showHelpTopic(topicName) {
        // Update active help topic
        document.querySelectorAll('.help-topic').forEach(topic => {
            topic.classList.remove('active');
        });
        document.querySelector(`[data-topic="${topicName}"]`).classList.add('active');
        
        // Update help content
        const helpContent = document.getElementById('helpContent');
        const helpTitle = document.getElementById('helpTopicTitle');
        
        const topics = {
            'getting-started': {
                title: 'Getting Started',
                content: `
                    <h4>Welcome to WIFIjam</h4>
                    <p>This is a powerful WiFi security testing tool designed for educational and authorized testing purposes only.</p>
                    
                    <h5>Basic Steps:</h5>
                    <ol>
                        <li>Ensure your WiFi adapter supports monitor mode</li>
                        <li>Configure your network interface in the Configuration section</li>
                        <li>Start scanning for networks</li>
                        <li>Select a target network</li>
                        <li>Configure and execute attacks responsibly</li>
                    </ol>
                    
                    <div class="warning-box">
                        <i class="fas fa-exclamation-triangle"></i>
                        <strong>Important:</strong> Only use this tool on networks you own or have explicit permission to test.
                    </div>
                `
            },
            'scanning': {
                title: 'Network Scanning',
                content: `
                    <h4>Network Discovery</h4>
                    <p>The network scanner helps you discover nearby WiFi networks and analyze their properties.</p>
                    
                    <h5>Scanning Process:</h5>
                    <ol>
                        <li>Select your WiFi interface from the dropdown</li>
                        <li>Choose scan duration (10 seconds to continuous)</li>
                        <li>Optionally select a specific channel</li>
                        <li>Click "Start Scan" to begin discovery</li>
                    </ol>
                    
                    <h5>Network Information:</h5>
                    <ul>
                        <li><strong>SSID:</strong> Network name</li>
                        <li><strong>BSSID:</strong> Access point MAC address</li>
                        <li><strong>Channel:</strong> WiFi channel number</li>
                        <li><strong>Security:</strong> Encryption type (Open, WEP, WPA/WPA2)</li>
                        <li><strong>Signal:</strong> Signal strength percentage</li>
                    </ul>
                `
            },
            'attacks': {
                title: 'Attack Types',
                content: `
                    <h4>Available Attack Methods</h4>
                    <p>WIFIjam supports several types of WiFi attacks for security testing.</p>
                    
                    <h5>Deauthentication Attack:</h5>
                    <ul>
                        <li>Disconnects devices from target network</li>
                        <li>Works on WPA/WPA2 networks</li>
                        <li>Useful for testing network resilience</li>
                    </ul>
                    
                    <h5>Jamming Attacks:</h5>
                    <ul>
                        <li><strong>2.4GHz Jamming:</strong> Targets 2.4GHz band</li>
                        <li><strong>5GHz Jamming:</strong> Targets 5GHz band</li>
                        <li>Prevents normal WiFi operation</li>
                    </ul>
                    
                    <div class="warning-box">
                        <i class="fas fa-exclamation-triangle"></i>
                        <strong>Legal Warning:</strong> WiFi jamming is illegal in many countries. Use only for authorized testing.
                    </div>
                `
            },
            'troubleshooting': {
                title: 'Troubleshooting',
                content: `
                    <h4>Common Issues</h4>
                    <p>Solutions for frequently encountered problems.</p>
                    
                    <h5>Monitor Mode Issues:</h5>
                    <ul>
                        <li>Ensure your WiFi adapter supports monitor mode</li>
                        <li>Check if adapter is compatible with aircrack-ng</li>
                        <li>Try running with administrator/root privileges</li>
                    </ul>
                    
                    <h5>No Networks Found:</h5>
                    <ul>
                        <li>Verify the correct interface is selected</li>
                        <li>Check if interface is in monitor mode</li>
                        <li>Try increasing scan duration</li>
                        <li>Ensure there are WiFi networks in range</li>
                    </ul>
                    
                    <h5>Attack Not Working:</h5>
                    <ul>
                        <li>Confirm target network is selected</li>
                        <li>Check packet injection capability</li>
                        <li>Verify you have necessary permissions</li>
                        <li>Ensure target is within range</li>
                    </ul>
                `
            }
        };
        
        const topic = topics[topicName];
        if (topic) {
            helpTitle.textContent = topic.title;
            helpContent.innerHTML = topic.content;
        }
    }

    switchOSTab(osName) {
        // Handle OS tab switching on installation page
        document.querySelectorAll('.os-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.os-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        document.querySelector(`[data-tab="${osName}"]`).classList.add('active');
        document.getElementById(osName).classList.add('active');
    }

    copyToClipboard(button) {
        const targetId = button.getAttribute('data-copytarget');
        const codeElement = document.getElementById(targetId);
        
        if (codeElement) {
            const text = codeElement.textContent;
            
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    this.showCopyFeedback(button);
                });
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                this.showCopyFeedback(button);
            }
        }
    }

    showCopyFeedback(button) {
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.classList.add('copied');
        
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('copied');
        }, 1200);
    }

    initializeCharts() {
        // Initialize any charts or visualizations
        this.updateNetworkStats();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new WIFIjamDashboard();
});

// Handle window resize for responsive design
window.addEventListener('resize', () => {
    // Handle any resize-specific logic here
    if (window.innerWidth <= 768) {
        document.querySelector('.dashboard-sidebar').classList.remove('open');
    }
});

// Handle keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
            case 's':
                e.preventDefault();
                if (window.dashboard.currentSection === 'config') {
                    window.dashboard.saveConfiguration();
                }
                break;
            case 'f':
                e.preventDefault();
                window.dashboard.switchSection('scanner');
                break;
            case 'Escape':
                window.dashboard.emergencyStop();
                break;
        }
    }
});
