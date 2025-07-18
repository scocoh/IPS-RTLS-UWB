/* Name: healthFormatters.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Health status formatting utilities for display and visualization */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/utils */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

/**
 * Port type descriptions mapping
 */
const PORT_TYPE_DESCRIPTIONS = {
    1: 'Control Manager',
    2: 'Real-Time Stream',
    3: 'O Data Raw FS',
    4: 'Raw Data Stream',
    5: 'Live Data Stream',
    6: 'Location Service',
    7: 'R and T Raw Sub',
    8: 'Event Engine (TETSE)',
    9: 'Event Forwarding',
    10: 'Event Broadcasting',
    11: 'REST API Service',
    12: 'Sensor Data FS'
};

/**
 * Health status color mappings
 */
const HEALTH_COLORS = {
    healthy: { bg: 'success', text: 'success', border: 'success' },
    warning: { bg: 'warning', text: 'warning', border: 'warning' },
    critical: { bg: 'danger', text: 'danger', border: 'danger' },
    unknown: { bg: 'secondary', text: 'muted', border: 'secondary' }
};

/**
 * Response time categories
 */
const RESPONSE_TIME_CATEGORIES = {
    excellent: { max: 200, label: 'Excellent', color: 'success', icon: '🟢' },
    good: { max: 500, label: 'Good', color: 'success', icon: '🟢' },
    acceptable: { max: 750, label: 'Acceptable', color: 'warning', icon: '🟡' },
    slow: { max: 1000, label: 'Slow', color: 'warning', icon: '🟡' },
    critical: { max: Infinity, label: 'Critical', color: 'danger', icon: '🔴' }
};

class HealthFormatters {
    /**
     * Format timestamp for display
     * @param {Date|string|number} timestamp - Timestamp to format
     * @param {string} format - Format type ('short', 'long', 'relative')
     * @returns {string} Formatted timestamp
     */
    static formatTimestamp(timestamp, format = 'short') {
        const date = new Date(timestamp);
        
        if (isNaN(date.getTime())) {
            return 'Invalid Date';
        }

        switch (format) {
            case 'relative':
                return this.getRelativeTime(date);
            case 'long':
                return date.toLocaleString();
            case 'time-only':
                return date.toLocaleTimeString();
            case 'date-only':
                return date.toLocaleDateString();
            default: // 'short'
                return date.toLocaleString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
        }
    }

    /**
     * Get relative time description
     * @param {Date} date - Date to compare
     * @returns {string} Relative time string
     */
    static getRelativeTime(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffSeconds = Math.floor(diffMs / 1000);
        const diffMinutes = Math.floor(diffSeconds / 60);
        const diffHours = Math.floor(diffMinutes / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffSeconds < 60) {
            return 'Just now';
        } else if (diffMinutes < 60) {
            return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
        } else if (diffHours < 24) {
            return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
        } else if (diffDays < 7) {
            return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    /**
     * Format response time with appropriate units and styling
     * @param {number|string} responseTime - Response time in milliseconds
     * @param {boolean} includeIcon - Whether to include status icon
     * @returns {Object} Formatted response time object
     */
    static formatResponseTime(responseTime, includeIcon = true) {
        if (responseTime === null || responseTime === undefined || responseTime === 'N/A') {
            return {
                value: 'N/A',
                display: 'N/A',
                category: 'unknown',
                color: 'secondary',
                icon: includeIcon ? '⚪' : null,
                className: 'text-muted'
            };
        }

        const time = parseFloat(responseTime);
        if (isNaN(time)) {
            return {
                value: responseTime,
                display: responseTime.toString(),
                category: 'unknown',
                color: 'secondary',
                icon: includeIcon ? '⚪' : null,
                className: 'text-muted'
            };
        }

        // Determine category
        let category = null;
        for (const [key, config] of Object.entries(RESPONSE_TIME_CATEGORIES)) {
            if (time <= config.max) {
                category = config;
                break;
            }
        }

        if (!category) {
            category = RESPONSE_TIME_CATEGORIES.critical;
        }

        return {
            value: time,
            display: `${time.toFixed(0)}ms`,
            category: category.label.toLowerCase(),
            color: category.color,
            icon: includeIcon ? category.icon : null,
            className: `text-${category.color}`
        };
    }

    /**
     * Get port type description
     * @param {number} typeId - Port type ID
     * @returns {string} Port type description
     */
    static getPortTypeDescription(typeId) {
        return PORT_TYPE_DESCRIPTIONS[typeId] || `Unknown Type (${typeId})`;
    }

    /**
     * Format health percentage
     * @param {number} percentage - Health percentage (0-100)
     * @returns {Object} Formatted health percentage
     */
    static formatHealthPercentage(percentage) {
        const percent = parseFloat(percentage);
        
        if (isNaN(percent)) {
            return {
                value: 0,
                display: 'N/A',
                color: 'secondary',
                className: 'text-muted'
            };
        }

        let color = 'danger';
        if (percent >= 95) color = 'success';
        else if (percent >= 80) color = 'warning';
        else if (percent >= 60) color = 'warning';

        return {
            value: percent,
            display: `${percent.toFixed(1)}%`,
            color,
            className: `text-${color}`
        };
    }

    /**
     * Format port status badge
     * @param {string} status - Port status
     * @param {boolean} isHealthy - Whether port is healthy
     * @returns {Object} Badge formatting
     */
    static formatStatusBadge(status, isHealthy = true) {
        const statusLower = status.toLowerCase();
        
        if (!isHealthy || statusLower === 'critical' || statusLower === 'error') {
            return {
                text: 'Critical',
                className: 'badge bg-danger',
                icon: '🔴'
            };
        }
        
        if (statusLower === 'warning' || statusLower === 'slow') {
            return {
                text: 'Warning',
                className: 'badge bg-warning',
                icon: '🟡'
            };
        }
        
        if (statusLower === 'healthy' || statusLower === 'good' || statusLower === 'active') {
            return {
                text: 'Healthy',
                className: 'badge bg-success',
                icon: '🟢'
            };
        }
        
        return {
            text: 'Unknown',
            className: 'badge bg-secondary',
            icon: '⚪'
        };
    }

    /**
     * Format utilization percentage with color coding
     * @param {number} utilization - Utilization percentage
     * @returns {Object} Formatted utilization
     */
    static formatUtilization(utilization) {
        const percent = parseFloat(utilization);
        
        if (isNaN(percent)) {
            return {
                value: 0,
                display: '0%',
                color: 'secondary',
                level: 'unknown'
            };
        }

        let color, level;
        if (percent < 25) {
            color = 'success';
            level = 'low';
        } else if (percent < 50) {
            color = 'info';
            level = 'moderate';
        } else if (percent < 75) {
            color = 'warning';
            level = 'high';
        } else {
            color = 'danger';
            level = 'critical';
        }

        return {
            value: percent,
            display: `${percent.toFixed(1)}%`,
            color,
            level,
            className: `text-${color}`
        };
    }

    /**
     * Format duration (in milliseconds) to human readable format
     * @param {number} duration - Duration in milliseconds
     * @returns {string} Human readable duration
     */
    static formatDuration(duration) {
        if (!duration || isNaN(duration)) {
            return 'Unknown';
        }

        const seconds = Math.floor(duration / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) {
            return `${days}d ${hours % 24}h`;
        } else if (hours > 0) {
            return `${hours}h ${minutes % 60}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds % 60}s`;
        } else {
            return `${seconds}s`;
        }
    }

    /**
     * Format port health summary
     * @param {Object} healthData - Health data object
     * @returns {Object} Formatted health summary
     */
    static formatHealthSummary(healthData) {
        const {
            total = 0,
            healthy = 0,
            unhealthy = 0,
            unknown = 0
        } = healthData;

        const healthPercentage = total > 0 ? (healthy / total) * 100 : 0;
        const healthFormatted = this.formatHealthPercentage(healthPercentage);

        return {
            total,
            healthy,
            unhealthy,
            unknown,
            healthPercentage: healthFormatted,
            status: {
                icon: healthPercentage >= 95 ? '🟢' : healthPercentage >= 80 ? '🟡' : '🔴',
                text: healthPercentage >= 95 ? 'Excellent' : healthPercentage >= 80 ? 'Good' : 'Poor',
                color: healthPercentage >= 95 ? 'success' : healthPercentage >= 80 ? 'warning' : 'danger'
            }
        };
    }

    /**
     * Generate health trend indicator
     * @param {Array} measurements - Array of health measurements over time
     * @returns {Object} Trend information
     */
    static generateHealthTrend(measurements = []) {
        if (measurements.length < 2) {
            return {
                trend: 'stable',
                direction: 'none',
                icon: '➡️',
                color: 'secondary',
                description: 'Insufficient data for trend analysis'
            };
        }

        const recent = measurements.slice(-5); // Last 5 measurements
        const avgRecent = recent.reduce((sum, m) => sum + (m.responseTime || 0), 0) / recent.length;
        
        const older = measurements.slice(-10, -5); // Previous 5 measurements
        const avgOlder = older.length > 0 ? 
            older.reduce((sum, m) => sum + (m.responseTime || 0), 0) / older.length : 
            avgRecent;

        const changePercent = avgOlder > 0 ? ((avgRecent - avgOlder) / avgOlder) * 100 : 0;

        let trend, direction, icon, color, description;

        if (Math.abs(changePercent) < 5) {
            trend = 'stable';
            direction = 'none';
            icon = '➡️';
            color = 'success';
            description = 'Performance is stable';
        } else if (changePercent > 0) {
            trend = 'degrading';
            direction = 'up';
            icon = '📈';
            color = 'warning';
            description = `Response time increased by ${changePercent.toFixed(1)}%`;
        } else {
            trend = 'improving';
            direction = 'down';
            icon = '📉';
            color = 'success';
            description = `Response time improved by ${Math.abs(changePercent).toFixed(1)}%`;
        }

        return {
            trend,
            direction,
            icon,
            color,
            description,
            changePercent: Math.abs(changePercent),
            avgRecent,
            avgOlder
        };
    }

    /**
     * Format health alert level
     * @param {string} level - Alert level
     * @returns {Object} Formatted alert information
     */
    static formatAlertLevel(level) {
        const levels = {
            critical: { color: 'danger', icon: '🚨', priority: 4, text: 'Critical' },
            high: { color: 'warning', icon: '⚠️', priority: 3, text: 'High' },
            medium: { color: 'info', icon: 'ℹ️', priority: 2, text: 'Medium' },
            low: { color: 'secondary', icon: '💡', priority: 1, text: 'Low' },
            info: { color: 'primary', icon: '📢', priority: 0, text: 'Info' }
        };

        return levels[level] || levels.info;
    }
}

export { HealthFormatters as healthFormatters, PORT_TYPE_DESCRIPTIONS, HEALTH_COLORS, RESPONSE_TIME_CATEGORIES };