/* Name: portHealthAPI.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for port health monitoring operations */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { config } from '../../../config';

const API_BASE = config.API_BASE_URL + '/api/components';

class PortHealthAPI {
    constructor() {
        this.baseURL = API_BASE;
    }

    // Helper method for making HTTP requests
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        console.log(`🌐 API Request: ${options.method || 'GET'} ${url}`);

        try {
            const response = await fetch(url, defaultOptions);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ API Error (${response.status}):`, errorText);
                throw new Error(`API Error: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            console.log('✅ API Response:', data);
            return data;
        } catch (error) {
            console.error('❌ Network Error:', error);
            throw error;
        }
    }

    // Get current port health status
    async getPortHealth() {
        return await this.makeRequest('/port-health');
    }

    // Get list of unhealthy ports
    async getUnhealthyPorts() {
        return await this.makeRequest('/unhealthy-ports');
    }

    // Refresh port health monitoring
    async refreshPortHealth() {
        return await this.makeRequest('/port-health/refresh', {
            method: 'POST'
        });
    }

    // Get live scaling candidates from heartbeat monitoring
    async getLiveScalingCandidates() {
        return await this.makeRequest('/scaling-candidates-live');
    }

    // Get next available scaling port from heartbeat monitoring
    async getNextScalingPortLive(basePort) {
        return await this.makeRequest(`/scaling/next-port-live/${basePort}`);
    }

    // Get all port monitoring configuration
    async getPortMonitoring() {
        return await this.makeRequest('/port-monitoring');
    }

    // Get monitoring details for a specific port
    async getPortMonitoringDetails(port) {
        return await this.makeRequest(`/port-monitoring/${port}`);
    }

    // Update port monitoring configuration
    async updatePortMonitoringConfig(port, config) {
        return await this.makeRequest(`/port-monitoring/${port}`, {
            method: 'PUT',
            body: JSON.stringify({
                port: config.port,
                monitor_enabled: config.monitor_enabled,
                auto_expand: config.auto_expand,
                monitor_interval: config.monitor_interval,
                monitor_timeout: config.monitor_timeout,
                monitor_threshold: config.monitor_threshold
            })
        });
    }

    // Health check with retry logic
    async healthCheck(retries = 3) {
        for (let i = 0; i < retries; i++) {
            try {
                console.log(`🏥 Health check attempt ${i + 1}/${retries}`);
                const result = await this.getPortHealth();
                
                if (result && !result.integration_needed) {
                    console.log('✅ Health check passed');
                    return { healthy: true, data: result };
                } else {
                    console.warn('⚠️ Health check: integration needed');
                    return { healthy: false, fallback: true, data: result };
                }
            } catch (error) {
                console.error(`❌ Health check attempt ${i + 1} failed:`, error);
                
                if (i === retries - 1) {
                    return { healthy: false, error: error.message };
                }
                
                // Wait before retry
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    }

    // Batch health check for multiple ports
    async batchHealthCheck(ports) {
        const results = [];
        
        for (const port of ports) {
            try {
                const result = await this.getPortMonitoringDetails(port);
                results.push({
                    port,
                    healthy: true,
                    data: result
                });
            } catch (error) {
                results.push({
                    port,
                    healthy: false,
                    error: error.message
                });
            }
        }
        
        return results;
    }

    // Monitor port health over time
    async monitorPortHealth(port, duration = 60000, interval = 5000) {
        const startTime = Date.now();
        const measurements = [];
        
        console.log(`📊 Starting port health monitoring for port ${port} (${duration}ms)`);
        
        while (Date.now() - startTime < duration) {
            try {
                const start = Date.now();
                const result = await this.getPortMonitoringDetails(port);
                const responseTime = Date.now() - start;
                
                measurements.push({
                    timestamp: new Date(),
                    responseTime,
                    healthy: responseTime < 750, // 750ms threshold
                    data: result
                });
                
                console.log(`📈 Port ${port} response time: ${responseTime}ms`);
            } catch (error) {
                measurements.push({
                    timestamp: new Date(),
                    responseTime: null,
                    healthy: false,
                    error: error.message
                });
                
                console.error(`❌ Port ${port} monitoring error:`, error);
            }
            
            await new Promise(resolve => setTimeout(resolve, interval));
        }
        
        // Calculate statistics
        const validMeasurements = measurements.filter(m => m.responseTime !== null);
        const avgResponseTime = validMeasurements.length > 0 
            ? validMeasurements.reduce((sum, m) => sum + m.responseTime, 0) / validMeasurements.length 
            : null;
        
        const healthyCount = measurements.filter(m => m.healthy).length;
        const healthPercentage = (healthyCount / measurements.length) * 100;
        
        return {
            port,
            duration,
            totalMeasurements: measurements.length,
            validMeasurements: validMeasurements.length,
            avgResponseTime,
            healthPercentage,
            measurements
        };
    }
}

export const portHealthAPI = new PortHealthAPI();