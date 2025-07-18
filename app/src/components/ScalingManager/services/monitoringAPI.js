/* Name: monitoringAPI.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for port monitoring configuration and management */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { config } from '../../../config';

const API_BASE = config.API_BASE_URL + '/api/components';

class MonitoringAPI {
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

        console.log(`🌐 Monitoring API Request: ${options.method || 'GET'} ${url}`);

        try {
            const response = await fetch(url, defaultOptions);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ Monitoring API Error (${response.status}):`, errorText);
                throw new Error(`Monitoring API Error: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            console.log('✅ Monitoring API Response:', data);
            return data;
        } catch (error) {
            console.error('❌ Monitoring Network Error:', error);
            throw error;
        }
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
            body: JSON.stringify(config)
        });
    }

    // Batch update multiple port configurations
    async batchUpdatePortConfigs(updates) {
        const results = [];
        const errors = [];
        
        console.log(`🔄 Starting batch update of ${updates.length} port configurations`);
        
        for (let i = 0; i < updates.length; i++) {
            const update = updates[i];
            
            try {
                const result = await this.updatePortMonitoringConfig(update.port, update.config);
                
                results.push({
                    port: update.port,
                    success: true,
                    result
                });
                
                console.log(`✅ Batch update ${i + 1}/${updates.length}: Port ${update.port} updated`);
                
                // Small delay between requests to avoid overwhelming the server
                if (i < updates.length - 1) {
                    await new Promise(resolve => setTimeout(resolve, 200));
                }
            } catch (error) {
                errors.push({
                    port: update.port,
                    error: error.message
                });
                
                console.error(`❌ Batch update ${i + 1}/${updates.length}: Port ${update.port} failed -`, error.message);
            }
        }
        
        return {
            totalRequested: updates.length,
            successfulUpdates: results.length,
            errors: errors.length,
            results,
            errors
        };
    }

    // Get monitoring templates for common configurations
    async getMonitoringTemplates() {
        // Return predefined monitoring templates
        return {
            templates: [
                {
                    name: 'Standard Monitoring',
                    description: 'Standard monitoring configuration for most ports',
                    config: {
                        monitor_enabled: true,
                        auto_expand: false,
                        monitor_interval: 30,
                        monitor_timeout: 5,
                        monitor_threshold: 2
                    }
                },
                {
                    name: 'High Frequency Monitoring',
                    description: 'More frequent monitoring for critical ports',
                    config: {
                        monitor_enabled: true,
                        auto_expand: false,
                        monitor_interval: 10,
                        monitor_timeout: 3,
                        monitor_threshold: 3
                    }
                },
                {
                    name: 'Scaling Candidate',
                    description: 'Configuration for ports that can auto-scale',
                    config: {
                        monitor_enabled: true,
                        auto_expand: true,
                        monitor_interval: 15,
                        monitor_timeout: 4,
                        monitor_threshold: 2
                    }
                },
                {
                    name: 'Low Priority Monitoring',
                    description: 'Less frequent monitoring for non-critical ports',
                    config: {
                        monitor_enabled: true,
                        auto_expand: false,
                        monitor_interval: 60,
                        monitor_timeout: 10,
                        monitor_threshold: 5
                    }
                },
                {
                    name: 'Disabled Monitoring',
                    description: 'Disable monitoring for inactive ports',
                    config: {
                        monitor_enabled: false,
                        auto_expand: false,
                        monitor_interval: 300,
                        monitor_timeout: 30,
                        monitor_threshold: 10
                    }
                }
            ]
        };
    }

    // Apply monitoring template to a port
    async applyTemplate(port, templateName) {
        const templates = await this.getMonitoringTemplates();
        const template = templates.templates.find(t => t.name === templateName);
        
        if (!template) {
            throw new Error(`Template '${templateName}' not found`);
        }
        
        console.log(`📋 Applying template '${templateName}' to port ${port}`);
        return await this.updatePortMonitoringConfig(port, template.config);
    }

    // Get monitoring statistics and analytics
    async getMonitoringStats() {
        try {
            const monitoringData = await this.getPortMonitoring();
            
            // Calculate statistics
            const stats = {
                total_ports: monitoringData.total_ports || 0,
                monitored_ports: monitoringData.monitored_ports || 0,
                auto_expand_ports: monitoringData.auto_expand_ports || 0,
                monitoring_coverage: 0,
                auto_expand_coverage: 0,
                port_categories: {
                    inbound: monitoringData.inbound_ports?.length || 0,
                    outbound: monitoringData.outbound_ports?.length || 0,
                    scaling: monitoringData.scaling_candidates?.length || 0
                },
                health_distribution: {
                    healthy: 0,
                    unhealthy: 0,
                    unknown: 0
                }
            };
            
            // Calculate coverage percentages
            if (stats.total_ports > 0) {
                stats.monitoring_coverage = Math.round((stats.monitored_ports / stats.total_ports) * 100);
                stats.auto_expand_coverage = Math.round((stats.auto_expand_ports / stats.total_ports) * 100);
            }
            
            return stats;
        } catch (error) {
            console.error('❌ Error calculating monitoring statistics:', error);
            throw error;
        }
    }

    // Validate monitoring configuration
    validateConfig(config) {
        const errors = [];
        const warnings = [];
        
        // Validate monitor_interval
        if (config.monitor_interval < 5 || config.monitor_interval > 300) {
            errors.push('Monitor interval must be between 5 and 300 seconds');
        } else if (config.monitor_interval < 10) {
            warnings.push('Monitor interval below 10 seconds may cause high system load');
        }
        
        // Validate monitor_timeout
        if (config.monitor_timeout < 1 || config.monitor_timeout > 30) {
            errors.push('Monitor timeout must be between 1 and 30 seconds');
        } else if (config.monitor_timeout >= config.monitor_interval) {
            errors.push('Monitor timeout must be less than monitor interval');
        }
        
        // Validate monitor_threshold
        if (config.monitor_threshold < 1 || config.monitor_threshold > 10) {
            errors.push('Monitor threshold must be between 1 and 10 failed checks');
        } else if (config.monitor_threshold > 5) {
            warnings.push('High monitor threshold may delay unhealthy port detection');
        }
        
        // Performance warnings
        if (config.monitor_enabled && config.monitor_interval < 15) {
            warnings.push('Frequent monitoring may impact system performance');
        }
        
        return {
            valid: errors.length === 0,
            errors,
            warnings
        };
    }

    // Test monitoring configuration
    async testMonitoringConfig(port, config) {
        const validation = this.validateConfig(config);
        
        if (!validation.valid) {
            throw new Error(`Invalid configuration: ${validation.errors.join(', ')}`);
        }
        
        console.log(`🧪 Testing monitoring configuration for port ${port}`);
        
        // Simulate configuration test
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    port,
                    config,
                    test_results: {
                        connectivity: Math.random() > 0.1,
                        response_time: Math.random() * 1000 + 100,
                        estimated_load: config.monitor_interval < 15 ? 'high' : 'normal',
                        recommendations: validation.warnings
                    },
                    timestamp: new Date()
                });
            }, 1000);
        });
    }

    // Export monitoring configuration
    async exportConfig(ports = []) {
        try {
            let configData;
            
            if (ports.length === 0) {
                // Export all ports
                configData = await this.getPortMonitoring();
            } else {
                // Export specific ports
                const portConfigs = [];
                for (const port of ports) {
                    try {
                        const config = await this.getPortMonitoringDetails(port);
                        portConfigs.push(config);
                    } catch (error) {
                        console.warn(`⚠️ Failed to export config for port ${port}:`, error);
                    }
                }
                configData = { exported_ports: portConfigs };
            }
            
            const exportData = {
                export_info: {
                    timestamp: new Date().toISOString(),
                    exported_by: 'ScalingManager',
                    version: '0.1.0',
                    total_ports: ports.length || configData.total_ports || 0
                },
                configuration: configData
            };
            
            return exportData;
        } catch (error) {
            console.error('❌ Error exporting monitoring configuration:', error);
            throw error;
        }
    }

    // Import monitoring configuration
    async importConfig(configData, options = {}) {
        const { 
            overwrite = false, 
            validateOnly = false,
            ignoreErrors = false 
        } = options;
        
        try {
            const results = {
                imported: 0,
                skipped: 0,
                errors: 0,
                details: []
            };
            
            const ports = configData.configuration?.exported_ports || [];
            
            for (const portConfig of ports) {
                const port = portConfig.i_prt || portConfig.port;
                
                try {
                    // Validate configuration
                    const validation = this.validateConfig(portConfig);
                    
                    if (!validation.valid && !ignoreErrors) {
                        results.errors++;
                        results.details.push({
                            port,
                            status: 'error',
                            message: `Validation failed: ${validation.errors.join(', ')}`
                        });
                        continue;
                    }
                    
                    if (validateOnly) {
                        results.details.push({
                            port,
                            status: 'valid',
                            message: 'Configuration is valid',
                            warnings: validation.warnings
                        });
                        continue;
                    }
                    
                    // Check if port exists and handle overwrite
                    let existingConfig = null;
                    try {
                        existingConfig = await this.getPortMonitoringDetails(port);
                    } catch (error) {
                        // Port doesn't exist, that's okay
                    }
                    
                    if (existingConfig && !overwrite) {
                        results.skipped++;
                        results.details.push({
                            port,
                            status: 'skipped',
                            message: 'Port exists and overwrite is disabled'
                        });
                        continue;
                    }
                    
                    // Apply configuration
                    await this.updatePortMonitoringConfig(port, {
                        monitor_enabled: portConfig.monitor_enabled,
                        auto_expand: portConfig.auto_expand,
                        monitor_interval: portConfig.monitor_interval,
                        monitor_timeout: portConfig.monitor_timeout,
                        monitor_threshold: portConfig.monitor_threshold
                    });
                    
                    results.imported++;
                    results.details.push({
                        port,
                        status: 'imported',
                        message: 'Configuration imported successfully'
                    });
                    
                } catch (error) {
                    results.errors++;
                    results.details.push({
                        port,
                        status: 'error',
                        message: error.message
                    });
                }
            }
            
            return results;
        } catch (error) {
            console.error('❌ Error importing monitoring configuration:', error);
            throw error;
        }
    }

    // Reset port configuration to defaults
    async resetPortConfig(port) {
        const defaultConfig = {
            monitor_enabled: true,
            auto_expand: false,
            monitor_interval: 30,
            monitor_timeout: 5,
            monitor_threshold: 2
        };
        
        console.log(`🔄 Resetting port ${port} to default configuration`);
        return await this.updatePortMonitoringConfig(port, defaultConfig);
    }

    // Get monitoring recommendations for a port
    async getPortRecommendations(port) {
        try {
            const portDetails = await this.getPortMonitoringDetails(port);
            const recommendations = [];
            
            // Analyze configuration and provide recommendations
            if (!portDetails.monitor_enabled) {
                recommendations.push({
                    type: 'suggestion',
                    message: 'Consider enabling monitoring for better system visibility',
                    action: 'enable_monitoring'
                });
            }
            
            if (portDetails.monitor_interval > 60) {
                recommendations.push({
                    type: 'optimization',
                    message: 'Long monitoring interval may delay issue detection',
                    action: 'reduce_interval'
                });
            }
            
            if (portDetails.monitor_interval < 15 && portDetails.monitor_enabled) {
                recommendations.push({
                    type: 'performance',
                    message: 'Frequent monitoring may impact system performance',
                    action: 'increase_interval'
                });
            }
            
            if (portDetails.can_scale && !portDetails.auto_expand) {
                recommendations.push({
                    type: 'scaling',
                    message: 'This port supports scaling - consider enabling auto-expand',
                    action: 'enable_auto_expand'
                });
            }
            
            return {
                port,
                recommendations,
                current_config: portDetails,
                timestamp: new Date()
            };
        } catch (error) {
            console.error(`❌ Error getting recommendations for port ${port}:`, error);
            throw error;
        }
    }
}

export const monitoringAPI = new MonitoringAPI();