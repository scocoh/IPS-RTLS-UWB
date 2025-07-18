/* Name: PortHealthIndicator.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Visual port health indicators with response time metrics and status visualization */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/modules */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';
import { healthFormatters } from '../utils/healthFormatters';

const PortHealthIndicator = ({ 
    port, 
    isHealthy, 
    responseTime, 
    detailed = false, 
    compact = false,
    showTrend = false 
}) => {
    // Determine health status based on response time
    const getHealthStatus = (responseTime, isHealthy) => {
        if (!isHealthy || responseTime === null || responseTime === 'N/A') {
            return {
                status: 'critical',
                color: 'danger',
                icon: '🔴',
                label: 'Critical'
            };
        }

        const time = typeof responseTime === 'number' ? responseTime : parseFloat(responseTime);
        
        if (time <= 750) {
            return {
                status: 'healthy',
                color: 'success',
                icon: '🟢',
                label: 'Healthy'
            };
        } else if (time <= 1000) {
            return {
                status: 'warning',
                color: 'warning',
                icon: '🟡',
                label: 'Warning'
            };
        } else {
            return {
                status: 'critical',
                color: 'danger',
                icon: '🔴',
                label: 'Critical'
            };
        }
    };

    const healthStatus = getHealthStatus(responseTime, isHealthy);

    // Generate mock trend data for demonstration
    const getTrendData = () => {
        return Array.from({ length: 10 }, () => Math.random() * 100 + 200);
    };

    const trendData = showTrend ? getTrendData() : null;

    if (compact) {
        return (
            <div className="port-health-indicator compact d-flex align-items-center">
                <span className="health-icon me-2" title={healthStatus.label}>
                    {healthStatus.icon}
                </span>
                <div className="port-info">
                    <strong>Port {port.port}</strong>
                    <small className="d-block text-muted">
                        {typeof responseTime === 'number' ? `${responseTime.toFixed(0)}ms` : responseTime}
                    </small>
                </div>
            </div>
        );
    }

    return (
        <div className={`port-health-indicator card ${detailed ? 'detailed' : ''}`}>
            <div className="card-body">
                {/* Header */}
                <div className="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <h6 className="card-title mb-1">
                            <span className="health-icon me-2">{healthStatus.icon}</span>
                            Port {port.port}
                        </h6>
                        {port.name && (
                            <small className="text-muted">{port.name}</small>
                        )}
                    </div>
                    <span className={`badge bg-${healthStatus.color}`}>
                        {healthStatus.label}
                    </span>
                </div>

                {/* Response Time */}
                <div className="response-time mb-3">
                    <div className="d-flex justify-content-between align-items-center mb-1">
                        <span>Response Time:</span>
                        <strong className={`text-${healthStatus.color}`}>
                            {typeof responseTime === 'number' ? `${responseTime.toFixed(0)}ms` : responseTime}
                        </strong>
                    </div>
                    
                    {/* Response Time Progress Bar */}
                    {typeof responseTime === 'number' && (
                        <div className="progress" style={{ height: '8px' }}>
                            <div 
                                className={`progress-bar bg-${healthStatus.color}`}
                                style={{ 
                                    width: `${Math.min((responseTime / 1500) * 100, 100)}%` 
                                }}
                            />
                        </div>
                    )}
                </div>

                {/* Detailed Information */}
                {detailed && (
                    <div className="detailed-info">
                        <div className="row mb-2">
                            <div className="col-6">
                                <small className="text-muted">Type:</small><br/>
                                <span className="badge bg-secondary">
                                    {healthFormatters.getPortTypeDescription(port.type)}
                                </span>
                            </div>
                            <div className="col-6">
                                <small className="text-muted">Monitoring:</small><br/>
                                <span className={`badge ${port.monitor_enabled ? 'bg-success' : 'bg-secondary'}`}>
                                    {port.monitor_enabled ? 'Enabled' : 'Disabled'}
                                </span>
                            </div>
                        </div>

                        {port.auto_expand && (
                            <div className="mb-2">
                                <span className="badge bg-warning">
                                    🔄 Auto-Scaling Candidate
                                </span>
                            </div>
                        )}

                        {/* Health Thresholds */}
                        <div className="health-thresholds">
                            <small className="text-muted d-block mb-1">Health Thresholds:</small>
                            <div className="d-flex justify-content-between small">
                                <span className="text-success">≤750ms</span>
                                <span className="text-warning">750-1000ms</span>
                                <span className="text-danger">&gt;1000ms</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Trend Chart (when enabled) */}
                {showTrend && trendData && (
                    <div className="trend-chart mt-3">
                        <small className="text-muted d-block mb-2">Response Time Trend:</small>
                        <div className="mini-chart d-flex align-items-end" style={{ height: '40px' }}>
                            {trendData.map((value, index) => (
                                <div
                                    key={index}
                                    className={`trend-bar bg-${value > 750 ? 'danger' : 'success'}`}
                                    style={{
                                        height: `${Math.max((value / 1000) * 100, 10)}%`,
                                        width: '8px',
                                        marginRight: '2px',
                                        opacity: index === trendData.length - 1 ? 1 : 0.7
                                    }}
                                    title={`${value.toFixed(0)}ms`}
                                />
                            ))}
                        </div>
                    </div>
                )}

                {/* Action Buttons (for detailed view) */}
                {detailed && (
                    <div className="action-buttons mt-3">
                        <div className="btn-group btn-group-sm w-100">
                            <button 
                                className="btn btn-outline-primary"
                                onClick={() => window.open(`/components/port-monitoring/${port.port}`, '_blank')}
                                title="View detailed port configuration"
                            >
                                📊 Details
                            </button>
                            <button 
                                className="btn btn-outline-secondary"
                                onClick={() => {
                                    // Mock health check function
                                    console.log(`Performing health check for port ${port.port}`);
                                }}
                                title="Perform immediate health check"
                            >
                                🔄 Check
                            </button>
                            {port.port >= 8200 && port.port <= 8299 && (
                                <button 
                                    className="btn btn-outline-danger"
                                    onClick={() => {
                                        if (window.confirm(`Remove scaling port ${port.port}?`)) {
                                            console.log(`Removing port ${port.port}`);
                                        }
                                    }}
                                    title="Remove scaling port"
                                >
                                    🗑️ Remove
                                </button>
                            )}
                        </div>
                    </div>
                )}

                {/* Last Updated */}
                {detailed && (
                    <div className="last-updated mt-2 text-center">
                        <small className="text-muted">
                            Last checked: {healthFormatters.formatTimestamp(new Date())}
                        </small>
                    </div>
                )}
            </div>

            {/* Quick Status Footer */}
            {!detailed && (
                <div className={`card-footer bg-${healthStatus.color} bg-opacity-10 text-center py-1`}>
                    <small className={`text-${healthStatus.color} fw-bold`}>
                        {healthStatus.label} - {typeof responseTime === 'number' ? `${responseTime.toFixed(0)}ms` : responseTime}
                    </small>
                </div>
            )}
        </div>
    );
};

export default PortHealthIndicator;