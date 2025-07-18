/* Name: AlertSystem.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Alert system for port health issues and scaling notifications */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/modules */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect, useMemo } from 'react';
import { healthFormatters } from '../utils/healthFormatters';

const AlertSystem = ({ 
    unhealthyPorts = [], 
    scalingStatus = null, 
    realTimeConnected = false,
    onDismiss = null,
    autoHide = true 
}) => {
    const [dismissedAlerts, setDismissedAlerts] = useState(new Set());
    const [alertHistory, setAlertHistory] = useState([]);

    // Generate alerts based on system status
    const alerts = useMemo(() => {
        const alertList = [];

        // Critical: Unhealthy ports
        if (unhealthyPorts.length > 0) {
            alertList.push({
                id: 'unhealthy-ports',
                type: 'danger',
                priority: 'critical',
                icon: '🚨',
                title: 'Unhealthy Ports Detected',
                message: `${unhealthyPorts.length} port${unhealthyPorts.length > 1 ? 's are' : ' is'} experiencing health issues`,
                details: unhealthyPorts.map(p => `Port ${p.port}: ${p.reason || 'Health check failed'}`),
                actions: [
                    { label: 'View Details', action: 'view_unhealthy' },
                    { label: 'Refresh Health', action: 'refresh_health' }
                ],
                timestamp: new Date()
            });
        }

        // Warning: Real-time connection issues
        if (!realTimeConnected) {
            alertList.push({
                id: 'realtime-disconnected',
                type: 'warning',
                priority: 'high',
                icon: '📡',
                title: 'Real-Time Connection Lost',
                message: 'Live monitoring is not available',
                details: ['WebSocket connection to real-time monitoring is down', 'Some features may not work correctly'],
                actions: [
                    { label: 'Retry Connection', action: 'retry_connection' }
                ],
                timestamp: new Date()
            });
        }

        // Warning: Low scaling capacity
        if (scalingStatus?.available_scaling_ports?.length <= 5) {
            alertList.push({
                id: 'low-scaling-capacity',
                type: 'warning',
                priority: 'medium',
                icon: '⚠️',
                title: 'Low Scaling Capacity',
                message: `Only ${scalingStatus.available_scaling_ports?.length || 0} scaling slots remaining`,
                details: ['Consider monitoring capacity usage', 'Plan for additional scaling resources if needed'],
                actions: [
                    { label: 'View Scaling Status', action: 'view_scaling' }
                ],
                timestamp: new Date()
            });
        }

        // Info: Heartbeat integration fallback
        if (scalingStatus?.port_health?.fallback_mode) {
            alertList.push({
                id: 'heartbeat-fallback',
                type: 'info',
                priority: 'low',
                icon: 'ℹ️',
                title: 'Heartbeat Integration Unavailable',
                message: 'Using fallback mode for port monitoring',
                details: ['Real-time health monitoring is limited', 'Database-based monitoring is active'],
                actions: [
                    { label: 'Check Integration', action: 'check_integration' }
                ],
                timestamp: new Date()
            });
        }

        // Success: All systems operational
        if (alertList.length === 0 && realTimeConnected && unhealthyPorts.length === 0) {
            alertList.push({
                id: 'all-systems-operational',
                type: 'success',
                priority: 'info',
                icon: '✅',
                title: 'All Systems Operational',
                message: 'Port health monitoring is functioning normally',
                details: ['All ports are healthy', 'Real-time monitoring is active', 'Scaling system is ready'],
                actions: [],
                timestamp: new Date(),
                autoHide: true
            });
        }

        return alertList.filter(alert => !dismissedAlerts.has(alert.id));
    }, [unhealthyPorts, scalingStatus, realTimeConnected, dismissedAlerts]);

    // Auto-hide success alerts
    useEffect(() => {
        if (autoHide) {
            const successAlerts = alerts.filter(alert => alert.type === 'success' && alert.autoHide);
            if (successAlerts.length > 0) {
                const timer = setTimeout(() => {
                    successAlerts.forEach(alert => handleDismiss(alert.id));
                }, 5000);
                return () => clearTimeout(timer);
            }
        }
    }, [alerts, autoHide]);

    // Update alert history
    useEffect(() => {
        const newAlerts = alerts.filter(alert => 
            !alertHistory.some(historical => historical.id === alert.id)
        );
        
        if (newAlerts.length > 0) {
            setAlertHistory(prev => [...prev, ...newAlerts].slice(-20)); // Keep last 20 alerts
        }
    }, [alerts, alertHistory]);

    // Handle alert dismissal
    const handleDismiss = (alertId) => {
        setDismissedAlerts(prev => new Set([...prev, alertId]));
        if (onDismiss) {
            onDismiss(alertId);
        }
    };

    // Handle alert actions
    const handleAction = (action, alert) => {
        console.log(`Alert action triggered: ${action} for alert ${alert.id}`);
        
        switch (action) {
            case 'view_unhealthy':
                // Trigger view change to unhealthy ports
                window.dispatchEvent(new CustomEvent('scalingManager:showUnhealthy'));
                break;
            case 'refresh_health':
                // Trigger health refresh
                window.dispatchEvent(new CustomEvent('scalingManager:refreshHealth'));
                break;
            case 'view_scaling':
                // Switch to scaling status tab
                window.dispatchEvent(new CustomEvent('scalingManager:showScaling'));
                break;
            case 'retry_connection':
                // Attempt to reconnect real-time monitoring
                window.dispatchEvent(new CustomEvent('scalingManager:retryConnection'));
                break;
            case 'check_integration':
                // Open integration status
                window.open('/components/port-health', '_blank');
                break;
            default:
                console.warn(`Unknown alert action: ${action}`);
        }
        
        // Auto-dismiss after action
        handleDismiss(alert.id);
    };

    // Get alert styling
    const getAlertClasses = (alert) => {
        const baseClasses = 'alert alert-dismissible fade show';
        const typeClasses = {
            danger: 'alert-danger',
            warning: 'alert-warning',
            info: 'alert-info',
            success: 'alert-success'
        };
        return `${baseClasses} ${typeClasses[alert.type] || 'alert-secondary'}`;
    };

    // Sort alerts by priority
    const sortedAlerts = [...alerts].sort((a, b) => {
        const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1, info: 0 };
        return (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0);
    });

    if (sortedAlerts.length === 0) {
        return null;
    }

    return (
        <div className="alert-system mb-4">
            {sortedAlerts.map(alert => (
                <div key={alert.id} className={getAlertClasses(alert)}>
                    <div className="d-flex align-items-start">
                        <div className="alert-icon me-3" style={{ fontSize: '1.5rem' }}>
                            {alert.icon}
                        </div>
                        <div className="flex-grow-1">
                            <div className="d-flex justify-content-between align-items-start mb-2">
                                <h6 className="alert-heading mb-0">
                                    {alert.title}
                                </h6>
                                <div className="d-flex align-items-center">
                                    <small className="text-muted me-2">
                                        {healthFormatters.formatTimestamp(alert.timestamp)}
                                    </small>
                                    <button
                                        type="button"
                                        className="btn-close"
                                        onClick={() => handleDismiss(alert.id)}
                                        aria-label="Close"
                                    />
                                </div>
                            </div>
                            
                            <p className="mb-2">{alert.message}</p>
                            
                            {/* Alert Details */}
                            {alert.details && alert.details.length > 0 && (
                                <div className="alert-details mb-3">
                                    {alert.details.length === 1 ? (
                                        <small className="text-muted">{alert.details[0]}</small>
                                    ) : (
                                        <details className="small">
                                            <summary className="text-muted" style={{ cursor: 'pointer' }}>
                                                Show details ({alert.details.length} items)
                                            </summary>
                                            <ul className="mb-0 mt-2">
                                                {alert.details.map((detail, index) => (
                                                    <li key={index} className="text-muted">{detail}</li>
                                                ))}
                                            </ul>
                                        </details>
                                    )}
                                </div>
                            )}
                            
                            {/* Alert Actions */}
                            {alert.actions && alert.actions.length > 0 && (
                                <div className="alert-actions">
                                    {alert.actions.map((action, index) => (
                                        <button
                                            key={index}
                                            className={`btn btn-sm me-2 ${
                                                alert.type === 'danger' ? 'btn-outline-danger' :
                                                alert.type === 'warning' ? 'btn-outline-warning' :
                                                alert.type === 'success' ? 'btn-outline-success' :
                                                'btn-outline-info'
                                            }`}
                                            onClick={() => handleAction(action.action, alert)}
                                        >
                                            {action.label}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            ))}
            
            {/* Alert History Toggle */}
            {alertHistory.length > 0 && (
                <div className="alert-history mt-3">
                    <details>
                        <summary className="text-muted small" style={{ cursor: 'pointer' }}>
                            📜 Alert History ({alertHistory.length} recent alerts)
                        </summary>
                        <div className="mt-2 p-2 bg-light rounded">
                            {alertHistory.slice(-5).map((alert, index) => (
                                <div key={`${alert.id}-${index}`} className="d-flex justify-content-between align-items-center py-1 border-bottom">
                                    <div>
                                        <span className="me-2">{alert.icon}</span>
                                        <small>{alert.title}</small>
                                    </div>
                                    <small className="text-muted">
                                        {healthFormatters.formatTimestamp(alert.timestamp)}
                                    </small>
                                </div>
                            ))}
                            {alertHistory.length > 5 && (
                                <div className="text-center mt-2">
                                    <small className="text-muted">
                                        ... and {alertHistory.length - 5} more alerts
                                    </small>
                                </div>
                            )}
                        </div>
                    </details>
                </div>
            )}
        </div>
    );
};

export default AlertSystem;