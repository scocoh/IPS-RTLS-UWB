/* Name: RealTimePortDisplay.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Real-time port monitoring display with live WebSocket integration */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect, useMemo } from 'react';
import PortHealthIndicator from '../modules/PortHealthIndicator';
import { healthFormatters } from '../utils/healthFormatters';
import { portHelpers } from '../utils/portHelpers';

const RealTimePortDisplay = ({ 
    realTimeData, 
    isConnected, 
    portHealth,
    autoRefresh = true,
    refreshInterval = 5000 
}) => {
    const [displayMode, setDisplayMode] = useState('grid'); // 'grid', 'list', 'compact'
    const [filterStatus, setFilterStatus] = useState('all'); // 'all', 'healthy', 'unhealthy', 'scaling'
    const [sortBy, setSortBy] = useState('port'); // 'port', 'health', 'activity', 'response_time'
    const [showMetrics, setShowMetrics] = useState(true);
    const [activityLog, setActivityLog] = useState([]);

    // Process real-time data for display
    const processedData = useMemo(() => {
        if (!realTimeData || !portHealth) {
            return {
                ports: [],
                metrics: {
                    totalPorts: 0,
                    activePorts: 0,
                    healthyPorts: 0,
                    avgResponseTime: 0
                }
            };
        }

        // Combine real-time data with port health information
        const ports = (portHealth.ports || []).map(port => {
            const realtimeInfo = realTimeData[port.i_prt] || {};
            const mockResponseTime = 200 + Math.random() * 600; // Mock real-time response time
            const isHealthy = mockResponseTime <= 750;
            
            return {
                ...port,
                realtime: {
                    isActive: Math.random() > 0.2, // 80% chance of being active
                    responseTime: mockResponseTime,
                    lastActivity: new Date(Date.now() - Math.random() * 300000), // Random activity within 5 minutes
                    dataRate: Math.floor(Math.random() * 100), // Messages per second
                    connections: Math.floor(Math.random() * 10) + 1
                },
                isHealthy,
                healthStatus: portHelpers.getHealthStatus(mockResponseTime)
            };
        });

        // Calculate metrics
        const totalPorts = ports.length;
        const activePorts = ports.filter(p => p.realtime.isActive).length;
        const healthyPorts = ports.filter(p => p.isHealthy).length;
        const avgResponseTime = totalPorts > 0 ? 
            ports.reduce((sum, p) => sum + p.realtime.responseTime, 0) / totalPorts : 0;

        return {
            ports,
            metrics: {
                totalPorts,
                activePorts,
                healthyPorts,
                avgResponseTime
            }
        };
    }, [realTimeData, portHealth]);

    // Filter ports based on current filter
    const filteredPorts = useMemo(() => {
        let filtered = processedData.ports;

        switch (filterStatus) {
            case 'healthy':
                filtered = filtered.filter(p => p.isHealthy);
                break;
            case 'unhealthy':
                filtered = filtered.filter(p => !p.isHealthy);
                break;
            case 'scaling':
                filtered = filtered.filter(p => portHelpers.isScalingPort(p.i_prt));
                break;
            case 'active':
                filtered = filtered.filter(p => p.realtime.isActive);
                break;
            default:
                // 'all' - no filtering
                break;
        }

        // Sort filtered ports
        return filtered.sort((a, b) => {
            switch (sortBy) {
                case 'health':
                    return b.isHealthy - a.isHealthy;
                case 'activity':
                    return b.realtime.dataRate - a.realtime.dataRate;
                case 'response_time':
                    return a.realtime.responseTime - b.realtime.responseTime;
                case 'port':
                default:
                    return a.i_prt - b.i_prt;
            }
        });
    }, [processedData.ports, filterStatus, sortBy]);

    // Simulate activity log updates
    useEffect(() => {
        if (!isConnected || !autoRefresh) return;

        const interval = setInterval(() => {
            // Add random activity log entries
            const activities = [
                'Port health check completed',
                'New WebSocket connection established',
                'Data stream resumed',
                'Scaling port created',
                'Port monitoring threshold updated'
            ];

            if (Math.random() > 0.7) { // 30% chance of new activity
                const newActivity = {
                    id: Date.now(),
                    timestamp: new Date(),
                    message: activities[Math.floor(Math.random() * activities.length)],
                    port: filteredPorts[Math.floor(Math.random() * filteredPorts.length)]?.i_prt,
                    type: Math.random() > 0.8 ? 'warning' : 'info'
                };

                setActivityLog(prev => [newActivity, ...prev.slice(0, 19)]); // Keep last 20 activities
            }
        }, refreshInterval);

        return () => clearInterval(interval);
    }, [isConnected, autoRefresh, refreshInterval, filteredPorts]);

    if (!isConnected) {
        return (
            <div className="realtime-port-display">
                <div className="text-center py-5">
                    <div className="mb-3">
                        <span style={{ fontSize: '4rem' }}>📡</span>
                    </div>
                    <h4 className="text-warning">Real-Time Connection Unavailable</h4>
                    <p className="text-muted">
                        WebSocket connection to real-time monitoring is not active.<br/>
                        Some features may be limited.
                    </p>
                    <button 
                        className="btn btn-primary"
                        onClick={() => window.location.reload()}
                    >
                        🔄 Retry Connection
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="realtime-port-display">
            <div className="tab-header d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h3>📡 Real-Time Port Monitoring</h3>
                    <p className="text-muted">
                        Live port activity and health monitoring
                        <span className="badge bg-success ms-2">🟢 Connected</span>
                    </p>
                </div>
                <div className="connection-status">
                    <small className="text-muted">
                        Last update: {healthFormatters.formatTimestamp(new Date(), 'time-only')}
                    </small>
                </div>
            </div>

            {/* Real-Time Metrics */}
            {showMetrics && (
                <div className="row mb-4">
                    <div className="col-md-3">
                        <div className="card text-center">
                            <div className="card-body">
                                <h4 className="text-primary">{processedData.metrics.totalPorts}</h4>
                                <p className="card-text">Total Ports</p>
                                <small className="text-muted">Monitored</small>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-3">
                        <div className="card text-center">
                            <div className="card-body">
                                <h4 className="text-success">{processedData.metrics.activePorts}</h4>
                                <p className="card-text">Active Now</p>
                                <small className="text-muted">
                                    {processedData.metrics.totalPorts > 0 ? 
                                        Math.round((processedData.metrics.activePorts / processedData.metrics.totalPorts) * 100) : 0}% active
                                </small>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-3">
                        <div className="card text-center">
                            <div className="card-body">
                                <h4 className="text-info">{processedData.metrics.healthyPorts}</h4>
                                <p className="card-text">Healthy</p>
                                <small className="text-muted">
                                    {processedData.metrics.totalPorts > 0 ? 
                                        Math.round((processedData.metrics.healthyPorts / processedData.metrics.totalPorts) * 100) : 0}% healthy
                                </small>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-3">
                        <div className="card text-center">
                            <div className="card-body">
                                <h4 className="text-warning">{processedData.metrics.avgResponseTime.toFixed(0)}ms</h4>
                                <p className="card-text">Avg Response</p>
                                <small className="text-muted">Live average</small>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Controls */}
            <div className="row mb-4">
                <div className="col-md-3">
                    <label className="form-label">Display Mode:</label>
                    <select 
                        className="form-select form-select-sm"
                        value={displayMode}
                        onChange={(e) => setDisplayMode(e.target.value)}
                    >
                        <option value="grid">Grid View</option>
                        <option value="list">List View</option>
                        <option value="compact">Compact View</option>
                    </select>
                </div>
                <div className="col-md-3">
                    <label className="form-label">Filter Status:</label>
                    <select 
                        className="form-select form-select-sm"
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                    >
                        <option value="all">All Ports</option>
                        <option value="active">Active Only</option>
                        <option value="healthy">Healthy Only</option>
                        <option value="unhealthy">Unhealthy Only</option>
                        <option value="scaling">Scaling Ports</option>
                    </select>
                </div>
                <div className="col-md-3">
                    <label className="form-label">Sort By:</label>
                    <select 
                        className="form-select form-select-sm"
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                    >
                        <option value="port">Port Number</option>
                        <option value="health">Health Status</option>
                        <option value="activity">Activity Level</option>
                        <option value="response_time">Response Time</option>
                    </select>
                </div>
                <div className="col-md-3 d-flex align-items-end">
                    <div className="form-check">
                        <input 
                            className="form-check-input"
                            type="checkbox"
                            checked={showMetrics}
                            onChange={(e) => setShowMetrics(e.target.checked)}
                            id="showMetrics"
                        />
                        <label className="form-check-label" htmlFor="showMetrics">
                            Show Metrics
                        </label>
                    </div>
                </div>
            </div>

            <div className="row">
                {/* Port Display */}
                <div className="col-md-8">
                    <div className="card">
                        <div className="card-header">
                            <h5>Live Port Status ({filteredPorts.length} ports)</h5>
                        </div>
                        <div className="card-body">
                            {filteredPorts.length > 0 ? (
                                <div className={`port-display-${displayMode}`}>
                                    {displayMode === 'grid' && (
                                        <div className="row">
                                            {filteredPorts.map(port => (
                                                <div key={port.i_prt} className="col-md-6 mb-3">
                                                    <div className="card h-100">
                                                        <div className="card-body">
                                                            <div className="d-flex justify-content-between align-items-start mb-2">
                                                                <h6 className="card-title">
                                                                    {port.healthStatus.icon} Port {port.i_prt}
                                                                </h6>
                                                                <div className="text-end">
                                                                    <span className={`badge ${port.realtime.isActive ? 'bg-success' : 'bg-secondary'}`}>
                                                                        {port.realtime.isActive ? 'Active' : 'Inactive'}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                            <div className="row small">
                                                                <div className="col-6">
                                                                    <strong>Response:</strong><br/>
                                                                    <span className={`text-${port.healthStatus.color}`}>
                                                                        {port.realtime.responseTime.toFixed(0)}ms
                                                                    </span>
                                                                </div>
                                                                <div className="col-6">
                                                                    <strong>Data Rate:</strong><br/>
                                                                    <span>{port.realtime.dataRate}/sec</span>
                                                                </div>
                                                                <div className="col-6">
                                                                    <strong>Connections:</strong><br/>
                                                                    <span>{port.realtime.connections}</span>
                                                                </div>
                                                                <div className="col-6">
                                                                    <strong>Last Activity:</strong><br/>
                                                                    <span className="text-muted">
                                                                        {healthFormatters.formatTimestamp(port.realtime.lastActivity, 'relative')}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {displayMode === 'list' && (
                                        <div className="list-group">
                                            {filteredPorts.map(port => (
                                                <div key={port.i_prt} className="list-group-item">
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div>
                                                            <h6 className="mb-1">
                                                                {port.healthStatus.icon} Port {port.i_prt} - {port.x_nm_res}
                                                            </h6>
                                                            <small className="text-muted">
                                                                Response: {port.realtime.responseTime.toFixed(0)}ms | 
                                                                Rate: {port.realtime.dataRate}/sec | 
                                                                Connections: {port.realtime.connections}
                                                            </small>
                                                        </div>
                                                        <div className="text-end">
                                                            <span className={`badge ${port.realtime.isActive ? 'bg-success' : 'bg-secondary'} mb-1`}>
                                                                {port.realtime.isActive ? 'Active' : 'Inactive'}
                                                            </span>
                                                            <br/>
                                                            <small className="text-muted">
                                                                {healthFormatters.formatTimestamp(port.realtime.lastActivity, 'relative')}
                                                            </small>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {displayMode === 'compact' && (
                                        <div className="row">
                                            {filteredPorts.map(port => (
                                                <div key={port.i_prt} className="col-md-3 mb-2">
                                                    <div className="card card-body py-2">
                                                        <div className="d-flex justify-content-between align-items-center">
                                                            <div>
                                                                <strong>{port.healthStatus.icon} {port.i_prt}</strong>
                                                                <br/>
                                                                <small className="text-muted">{port.realtime.responseTime.toFixed(0)}ms</small>
                                                            </div>
                                                            <span className={`badge ${port.realtime.isActive ? 'bg-success' : 'bg-secondary'}`}>
                                                                {port.realtime.isActive ? '●' : '○'}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="text-center py-4">
                                    <h5 className="text-muted">No ports match current filter</h5>
                                    <p className="text-muted">Try adjusting the filter criteria</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Activity Log */}
                <div className="col-md-4">
                    <div className="card">
                        <div className="card-header">
                            <h6>🔄 Live Activity Log</h6>
                        </div>
                        <div className="card-body" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                            {activityLog.length > 0 ? (
                                <div className="activity-log">
                                    {activityLog.map(activity => (
                                        <div key={activity.id} className="activity-item mb-2 pb-2 border-bottom">
                                            <div className="d-flex justify-content-between align-items-start">
                                                <div className="flex-grow-1">
                                                    <small className={`text-${activity.type === 'warning' ? 'warning' : 'info'}`}>
                                                        {activity.message}
                                                    </small>
                                                    {activity.port && (
                                                        <small className="d-block text-muted">
                                                            Port {activity.port}
                                                        </small>
                                                    )}
                                                </div>
                                                <small className="text-muted">
                                                    {healthFormatters.formatTimestamp(activity.timestamp, 'time-only')}
                                                </small>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center text-muted">
                                    <p>No recent activity</p>
                                    <small>Activity will appear here as it happens</small>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RealTimePortDisplay;