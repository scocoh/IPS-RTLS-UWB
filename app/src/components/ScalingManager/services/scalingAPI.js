/* Name: scalingAPI.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for scaling operations management */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { config } from '../../../config';

const API_BASE = config.API_BASE_URL + '/api/components';

class ScalingAPI {
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

        console.log(`🌐 Scaling API Request: ${options.method || 'GET'} ${url}`);

        try {
            const response = await fetch(url, defaultOptions);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ Scaling API Error (${response.status}):`, errorText);
                throw new Error(`Scaling API Error: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            console.log('✅ Scaling API Response:', data);
            return data;
        } catch (error) {
            console.error('❌ Scaling Network Error:', error);
            throw error;
        }
    }

    // Get comprehensive scaling status
    async getScalingStatus() {
        return await this.makeRequest('/scaling/status');
    }

    // Get scaling candidates (ports with auto_expand = true)
    async getScalingCandidates() {
        return await this.makeRequest('/scaling-candidates');
    }

    // Create a new scaling port (simple endpoint)
    async createScalingPort(port) {
        return await this.makeRequest(`/scaling/create/${port}`, {
            method: 'POST'
        });
    }

    // Remove a scaling port
    async removeScalingPort(port) {
        return await this.makeRequest(`/scaling/remove/${port}`, {
            method: 'DELETE'
        });
    }

    // Get next available port in scaling range
    async getNextScalingPort(basePort) {
        return await this.makeRequest(`/scaling/next-port/${basePort}`);
    }

    // Create scaling port with full configuration (advanced endpoint)
    async createScalingPortAdvanced(config) {
        return await this.makeRequest('/scaling/create-port', {
            method: 'POST',
            body: JSON.stringify({
                base_port: config.basePort,
                new_port: config.newPort,
                resource_name: config.resourceName,
                resource_type: config.resourceType,
                action: config.action || 'create'
            })
        });
    }

    // Get scaling menu for text-based operations
    async getScalingMenu() {
        return await this.makeRequest('/menu/scaling');
    }

    // Batch operations
    async batchCreatePorts(basePort, count) {
        const results = [];
        const errors = [];
        
        console.log(`🚀 Starting batch creation of ${count} ports from base ${basePort}`);
        
        for (let i = 0; i < count; i++) {
            try {
                // Get next available port
                const nextPortResult = await this.getNextScalingPort(basePort);
                const nextPort = nextPortResult.next_available_port;
                
                // Create the port
                const createResult = await this.createScalingPort(nextPort);
                
                results.push({
                    port: nextPort,
                    success: true,
                    result: createResult
                });
                
                console.log(`✅ Batch port ${i + 1}/${count}: Created port ${nextPort}`);
                
                // Small delay between requests to avoid overwhelming the server
                if (i < count - 1) {
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            } catch (error) {
                errors.push({
                    portIndex: i + 1,
                    error: error.message
                });
                
                console.error(`❌ Batch port ${i + 1}/${count}: Failed -`, error.message);
            }
        }
        
        return {
            totalRequested: count,
            successfulCreations: results.length,
            errors: errors.length,
            results,
            errors
        };
    }

    async batchRemovePorts(ports) {
        const results = [];
        const errors = [];
        
        console.log(`🗑️ Starting batch removal of ${ports.length} ports`);
        
        for (let i = 0; i < ports.length; i++) {
            const port = ports[i];
            
            try {
                const removeResult = await this.removeScalingPort(port);
                
                results.push({
                    port,
                    success: true,
                    result: removeResult
                });
                
                console.log(`✅ Batch remove ${i + 1}/${ports.length}: Removed port ${port}`);
                
                // Small delay between requests
                if (i < ports.length - 1) {
                    await new Promise(resolve => setTimeout(resolve, 300));
                }
            } catch (error) {
                errors.push({
                    port,
                    error: error.message
                });
                
                console.error(`❌ Batch remove ${i + 1}/${ports.length}: Failed to remove port ${port} -`, error.message);
            }
        }
        
        return {
            totalRequested: ports.length,
            successfulRemovals: results.length,
            errors: errors.length,
            results,
            errors
        };
    }

    // Utility methods
    async validatePortRange(basePort) {
        try {
            const result = await this.getNextScalingPort(basePort);
            return {
                valid: true,
                scalingRange: result.scaling_range,
                nextAvailable: result.next_available_port,
                existingPorts: result.existing_ports
            };
        } catch (error) {
            return {
                valid: false,
                error: error.message
            };
        }
    }

    async getScalingStatistics() {
        try {
            const status = await this.getScalingStatus();
            const candidates = await this.getScalingCandidates();
            
            return {
                totalCandidates: candidates.total_candidates || 0,
                availableSlots: status.available_scaling_ports?.length || 0,
                activeInstances: status.active_scaling_ports?.length || 0,
                utilizationRate: status.scaling_status?.active_scaling_instances || 0,
                capacityStatus: this.calculateCapacityStatus(status),
                recommendations: this.generateRecommendations(status, candidates)
            };
        } catch (error) {
            console.error('❌ Error getting scaling statistics:', error);
            throw error;
        }
    }

    calculateCapacityStatus(status) {
        const available = status.available_scaling_ports?.length || 0;
        const active = status.active_scaling_ports?.length || 0;
        const total = available + active;
        
        if (total === 0) return 'unknown';
        
        const utilization = (active / total) * 100;
        
        if (utilization < 50) return 'low';
        if (utilization < 80) return 'medium';
        if (utilization < 95) return 'high';
        return 'critical';
    }

    generateRecommendations(status, candidates) {
        const recommendations = [];
        
        const available = status.available_scaling_ports?.length || 0;
        const active = status.active_scaling_ports?.length || 0;
        const unhealthyPorts = status.port_health?.unhealthy_ports?.length || 0;
        
        if (available < 5) {
            recommendations.push({
                type: 'warning',
                message: `Low available scaling slots (${available}). Consider monitoring capacity.`,
                action: 'monitor_capacity'
            });
        }
        
        if (unhealthyPorts > 0) {
            recommendations.push({
                type: 'alert',
                message: `${unhealthyPorts} unhealthy ports detected. Consider investigating.`,
                action: 'investigate_health'
            });
        }
        
        if (active === 0 && candidates.total_candidates > 0) {
            recommendations.push({
                type: 'info',
                message: 'No scaling instances active. System ready for scaling when needed.',
                action: 'ready_to_scale'
            });
        }
        
        return recommendations;
    }
}

export const scalingAPI = new ScalingAPI();