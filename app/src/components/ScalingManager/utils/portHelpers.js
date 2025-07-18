/* Name: portHelpers.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Utility functions for port-related operations and information */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/utils */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

/**
 * Port range definitions for the ParcoRTLS system
 */
const PORT_RANGES = {
    // Inbound data ports (AllTraq, etc.)
    INBOUND: {
        start: 18000,
        end: 18999,
        description: 'Inbound Data Ports',
        category: 'inbound'
    },
    
    // Outbound service ports (API, WebSocket, etc.)
    OUTBOUND: {
        start: 8000,
        end: 8199,
        description: 'Outbound Service Ports',
        category: 'outbound'
    },
    
    // Scaling ports (dynamic instances)
    SCALING: {
        start: 8200,
        end: 8299,
        description: 'Scaling Instance Ports',
        category: 'scaling'
    }
};

/**
 * Port type mappings from database resource types
 */
const PORT_TYPES = {
    1: { name: 'Control', description: 'Control Manager', icon: '🎛️' },
    2: { name: 'RealTime', description: 'Real-Time Data Stream', icon: '⚡' },
    3: { name: 'OData', description: 'O Data Raw FS', icon: '📊' },
    4: { name: 'Raw', description: 'Raw Data Stream', icon: '📡' },
    5: { name: 'Live', description: 'Live Data Stream', icon: '🔴' },
    6: { name: 'Location', description: 'Location Service', icon: '📍' },
    7: { name: 'Subscription', description: 'R and T Raw Sub', icon: '📧' },
    8: { name: 'TETSE', description: 'Event Engine', icon: '🔄' },
    9: { name: 'Forward', description: 'Event Forwarding', icon: '➡️' },
    10: { name: 'Event', description: 'Event Broadcasting', icon: '📢' },
    11: { name: 'API', description: 'REST API Service', icon: '🌐' },
    12: { name: 'SensorData', description: 'Sensor Data FS', icon: '🔍' }
};

/**
 * Health threshold definitions
 */
const HEALTH_THRESHOLDS = {
    HEALTHY: { min: 0, max: 750, label: 'Healthy', color: 'success' },
    WARNING: { min: 750, max: 1000, label: 'Warning', color: 'warning' },
    CRITICAL: { min: 1000, max: Infinity, label: 'Critical', color: 'danger' }
};

/**
 * Scaling configuration for different base ports
 */
const SCALING_CONFIG = {
    8002: {
        range: '8200-8299',
        type: 'RealTime WebSocket',
        description: 'RealTime data stream scaling',
        resourceType: 2
    }
};

class PortHelpers {
    /**
     * Get port range information for a given port number
     * @param {number} port - Port number
     * @returns {Object} Port range information
     */
    static getPortRangeInfo(port) {
        const portNum = parseInt(port);
        
        if (portNum >= PORT_RANGES.INBOUND.start && portNum <= PORT_RANGES.INBOUND.end) {
            return {
                category: 'inbound',
                range: `${PORT_RANGES.INBOUND.start}-${PORT_RANGES.INBOUND.end}`,
                description: PORT_RANGES.INBOUND.description,
                scalingRange: null,
                scalingType: null
            };
        }
        
        if (portNum >= PORT_RANGES.SCALING.start && portNum <= PORT_RANGES.SCALING.end) {
            return {
                category: 'scaling',
                range: `${PORT_RANGES.SCALING.start}-${PORT_RANGES.SCALING.end}`,
                description: PORT_RANGES.SCALING.description,
                scalingRange: '8200-8299',
                scalingType: 'Dynamic Scaling Instance'
            };
        }
        
        if (portNum >= PORT_RANGES.OUTBOUND.start && portNum <= PORT_RANGES.OUTBOUND.end) {
            const scalingInfo = SCALING_CONFIG[portNum];
            return {
                category: 'outbound',
                range: `${PORT_RANGES.OUTBOUND.start}-${PORT_RANGES.OUTBOUND.end}`,
                description: PORT_RANGES.OUTBOUND.description,
                scalingRange: scalingInfo?.range || null,
                scalingType: scalingInfo?.type || null
            };
        }
        
        return {
            category: 'unknown',
            range: 'Unknown',
            description: 'Unknown Port Range',
            scalingRange: null,
            scalingType: null
        };
    }

    /**
     * Get port type description from resource type ID
     * @param {number} typeId - Resource type ID
     * @returns {string} Port type description
     */
    static getPortTypeDescription(typeId) {
        const type = PORT_TYPES[typeId];
        return type ? `${type.icon} ${type.name}` : `Unknown (${typeId})`;
    }

    /**
     * Get detailed port type information
     * @param {number} typeId - Resource type ID
     * @returns {Object} Port type information
     */
    static getPortTypeInfo(typeId) {
        return PORT_TYPES[typeId] || {
            name: 'Unknown',
            description: `Unknown Type (${typeId})`,
            icon: '❓'
        };
    }

    /**
     * Determine health status based on response time
     * @param {number} responseTime - Response time in milliseconds
     * @returns {Object} Health status information
     */
    static getHealthStatus(responseTime) {
        if (responseTime === null || responseTime === undefined || isNaN(responseTime)) {
            return {
                status: 'unknown',
                color: 'secondary',
                icon: '⚪',
                label: 'Unknown',
                threshold: null
            };
        }

        const time = parseFloat(responseTime);
        
        for (const [key, threshold] of Object.entries(HEALTH_THRESHOLDS)) {
            if (time >= threshold.min && time < threshold.max) {
                return {
                    status: key.toLowerCase(),
                    color: threshold.color,
                    icon: key === 'HEALTHY' ? '🟢' : key === 'WARNING' ? '🟡' : '🔴',
                    label: threshold.label,
                    threshold
                };
            }
        }

        return HEALTH_THRESHOLDS.CRITICAL;
    }

    /**
     * Check if a port is in the scaling range
     * @param {number} port - Port number
     * @returns {boolean} True if port is in scaling range
     */
    static isScalingPort(port) {
        const portNum = parseInt(port);
        return portNum >= PORT_RANGES.SCALING.start && portNum <= PORT_RANGES.SCALING.end;
    }

    /**
     * Check if a port can be scaled
     * @param {number} port - Port number
     * @returns {boolean} True if port can be scaled
     */
    static canScale(port) {
        const portNum = parseInt(port);
        return Object.keys(SCALING_CONFIG).includes(portNum.toString());
    }

    /**
     * Get scaling configuration for a base port
     * @param {number} basePort - Base port number
     * @returns {Object|null} Scaling configuration
     */
    static getScalingConfig(basePort) {
        return SCALING_CONFIG[basePort] || null;
    }

    /**
     * Get next available port in scaling range
     * @param {Array} existingPorts - Array of existing port numbers
     * @param {number} startPort - Starting port number (default: 8200)
     * @returns {number|null} Next available port or null if none available
     */
    static getNextAvailableScalingPort(existingPorts = [], startPort = 8200) {
        for (let port = startPort; port <= PORT_RANGES.SCALING.end; port++) {
            if (!existingPorts.includes(port)) {
                return port;
            }
        }
        return null;
    }

    /**
     * Validate port number
     * @param {any} port - Port to validate
     * @returns {Object} Validation result
     */
    static validatePort(port) {
        const portNum = parseInt(port);
        
        if (isNaN(portNum)) {
            return {
                valid: false,
                error: 'Port must be a number'
            };
        }
        
        if (portNum < 1 || portNum > 65535) {
            return {
                valid: false,
                error: 'Port must be between 1 and 65535'
            };
        }
        
        return {
            valid: true,
            port: portNum,
            info: this.getPortRangeInfo(portNum)
        };
    }

    /**
     * Format port for display
     * @param {Object} port - Port object
     * @returns {string} Formatted port string
     */
    static formatPort(port) {
        const portNum = port.i_prt || port.port;
        const name = port.x_nm_res || port.name;
        const type = this.getPortTypeInfo(port.i_typ_res || port.type);
        
        return `${type.icon} Port ${portNum}${name ? ` (${name})` : ''}`;
    }

    /**
     * Group ports by category
     * @param {Array} ports - Array of port objects
     * @returns {Object} Ports grouped by category
     */
    static groupPortsByCategory(ports) {
        const grouped = {
            inbound: [],
            outbound: [],
            scaling: [],
            unknown: []
        };

        ports.forEach(port => {
            const portNum = port.i_prt || port.port;
            const info = this.getPortRangeInfo(portNum);
            grouped[info.category].push(port);
        });

        return grouped;
    }

    /**
     * Calculate port utilization statistics
     * @param {Array} allPorts - All configured ports
     * @param {Array} activePorts - Currently active ports
     * @returns {Object} Utilization statistics
     */
    static calculateUtilization(allPorts = [], activePorts = []) {
        const grouped = this.groupPortsByCategory(allPorts);
        const activeGrouped = this.groupPortsByCategory(activePorts);

        return {
            total: {
                configured: allPorts.length,
                active: activePorts.length,
                utilization: allPorts.length > 0 ? (activePorts.length / allPorts.length) * 100 : 0
            },
            inbound: {
                configured: grouped.inbound.length,
                active: activeGrouped.inbound.length,
                utilization: grouped.inbound.length > 0 ? (activeGrouped.inbound.length / grouped.inbound.length) * 100 : 0
            },
            outbound: {
                configured: grouped.outbound.length,
                active: activeGrouped.outbound.length,
                utilization: grouped.outbound.length > 0 ? (activeGrouped.outbound.length / grouped.outbound.length) * 100 : 0
            },
            scaling: {
                configured: grouped.scaling.length,
                active: activeGrouped.scaling.length,
                available: 100 - grouped.scaling.length, // Total scaling slots minus configured
                utilization: grouped.scaling.length > 0 ? (activeGrouped.scaling.length / grouped.scaling.length) * 100 : 0
            }
        };
    }

    /**
     * Generate port recommendations
     * @param {Object} utilization - Utilization statistics
     * @param {Array} unhealthyPorts - Unhealthy ports
     * @returns {Array} Array of recommendations
     */
    static generateRecommendations(utilization, unhealthyPorts = []) {
        const recommendations = [];

        // Scaling capacity recommendations
        if (utilization.scaling.available < 10) {
            recommendations.push({
                type: 'warning',
                category: 'capacity',
                message: `Low scaling capacity: only ${utilization.scaling.available} slots remaining`,
                action: 'monitor_scaling_capacity'
            });
        }

        // Health recommendations
        if (unhealthyPorts.length > 0) {
            recommendations.push({
                type: 'critical',
                category: 'health',
                message: `${unhealthyPorts.length} unhealthy ports require attention`,
                action: 'investigate_health_issues'
            });
        }

        // Utilization recommendations
        if (utilization.total.utilization > 80) {
            recommendations.push({
                type: 'info',
                category: 'utilization',
                message: 'High port utilization detected',
                action: 'consider_scaling'
            });
        }

        return recommendations;
    }
}

export { PortHelpers as portHelpers, PORT_RANGES, PORT_TYPES, HEALTH_THRESHOLDS, SCALING_CONFIG };