/* Name: ScalingPortCard.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Port information card component for scaling candidates and active ports */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/modules */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState } from 'react';
import { portHelpers } from '../utils/portHelpers';
import { healthFormatters } from '../utils/healthFormatters';

const ScalingPortCard = ({ 
    port, 
    type = 'active', // 'candidate', 'active', 'scaling'
    isHealthy = true,
    responseTime = null,
    showActions = true,
    compact = false,
    onAction = null 
}) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    // Determine card styling based on type and health
    const getCardStyle = () => {
        const baseStyle = 'scaling-port-card card h-100';
        
        if (!isHealthy) {
            return `${baseStyle} border-danger`;
        }
        
        switch (type) {
            case 'candidate':
                return `${baseStyle} border-primary`;
            case 'scaling':
                return `${baseStyle} border-warning`;
            default:
                return `${baseStyle} border-success`;
        }
    };

    // Get port type information
    const portInfo = portHelpers.getPortRangeInfo(port.i_prt || port.port);
    
    // Get health indicator
    const getHealthIndicator = () => {
        if (responseTime === null) return { icon: '⚪', color: 'secondary', label: 'Unknown' };
        if (!isHealthy) return { icon: '🔴', color: 'danger', label: 'Unhealthy' };
        
        const time = typeof responseTime === 'number' ? responseTime : parseFloat(responseTime);
        if (time <= 750) return { icon: '🟢', color: 'success', label: 'Healthy' };
        if (time <= 1000) return { icon: '🟡', color: 'warning', label: 'Warning' };
        return { icon: '🔴', color: 'danger', label: 'Critical' };
    };

    const healthIndicator = getHealthIndicator();

    // Handle action buttons
    const handleAction = async (action) => {
        if (onAction) {
            setIsLoading(true);
            try {
                await onAction(action, port);
            } finally {
                setIsLoading(false);
            }
        }
    };

    if (compact) {
        return (
            <div className={`${getCardStyle()} compact-card`}>
                <div className="card-body py-2">
                    <div className="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>Port {port.i_prt || port.port}</strong>
                            <small className="d-block text-muted">
                                {port.x_nm_res || port.name || portInfo.description}
                            </small>
                        </div>
                        <div className="text-end">
                            <span className={`badge bg-${healthIndicator.color}`}>
                                {healthIndicator.icon}
                            </span>
                            {responseTime && (
                                <small className="d-block text-muted">
                                    {typeof responseTime === 'number' ? `${responseTime.toFixed(0)}ms` : responseTime}
                                </small>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={getCardStyle()}>
            {/* Card Header */}
            <div className="card-header d-flex justify-content-between align-items-center">
                <div>
                    <h6 className="mb-0">
                        <span className="me-2">{healthIndicator.icon}</span>
                        Port {port.i_prt || port.port}
                    </h6>
                    <small className="text-muted">
                        {portInfo.description}
                    </small>
                </div>
                {type === 'candidate' && (
                    <span className="badge bg-primary">Candidate</span>
                )}
                {type === 'scaling' && (
                    <span className="badge bg-warning">Scaling</span>
                )}
                {port.f_auto_expand && (
                    <span className="badge bg-info">Auto-Expand</span>
                )}
            </div>

            {/* Card Body */}
            <div className="card-body">
                {/* Basic Information */}
                <div className="row mb-3">
                    <div className="col-6">
                        <small className="text-muted">Resource Name:</small><br/>
                        <span className="fw-bold">
                            {port.x_nm_res || port.name || 'N/A'}
                        </span>
                    </div>
                    <div className="col-6">
                        <small className="text-muted">Type:</small><br/>
                        <span className="badge bg-secondary">
                            {healthFormatters.getPortTypeDescription(port.i_typ_res || port.type)}
                        </span>
                    </div>
                </div>

                {/* Health Status */}
                <div className="row mb-3">
                    <div className="col-6">
                        <small className="text-muted">Health Status:</small><br/>
                        <span className={`badge bg-${healthIndicator.color}`}>
                            {healthIndicator.label}
                        </span>
                    </div>
                    <div className="col-6">
                        <small className="text-muted">Response Time:</small><br/>
                        <strong className={responseTime ? `text-${healthIndicator.color}` : 'text-muted'}>
                            {responseTime ? 
                                (typeof responseTime === 'number' ? `${responseTime.toFixed(0)}ms` : responseTime) : 
                                'N/A'
                            }
                        </strong>
                    </div>
                </div>

                {/* Monitoring Configuration */}
                <div className="row mb-3">
                    <div className="col-6">
                        <small className="text-muted">Monitoring:</small><br/>
                        <span className={`badge ${port.f_monitor_enabled || port.monitor_enabled ? 'bg-success' : 'bg-secondary'}`}>
                            {port.f_monitor_enabled || port.monitor_enabled ? 'Enabled' : 'Disabled'}
                        </span>
                    </div>
                    <div className="col-6">
                        <small className="text-muted">Rank:</small><br/>
                        <span className="fw-bold">{port.i_rnk || port.rank || 'N/A'}</span>
                    </div>
                </div>

                {/* Scaling Information (for candidates) */}
                {type === 'candidate' && (
                    <div className="scaling-info border-top pt-3">
                        <div className="row">
                            <div className="col-6">
                                <small className="text-muted">Scaling Range:</small><br/>
                                <code>{port.scaling_range || portInfo.scalingRange || 'N/A'}</code>
                            </div>
                            <div className="col-6">
                                <small className="text-muted">Scaling Type:</small><br/>
                                <span className="badge bg-info">
                                    {port.scaling_type || portInfo.scalingType || 'Generic'}
                                </span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Expanded Details */}
                {isExpanded && (
                    <div className="expanded-details border-top pt-3 mt-3">
                        <div className="row">
                            <div className="col-6">
                                <small className="text-muted">IP Address:</small><br/>
                                <code>{port.x_ip || port.ip || 'localhost'}</code>
                            </div>
                            <div className="col-6">
                                <small className="text-muted">Full Stream:</small><br/>
                                <span className={`badge ${port.f_fs ? 'bg-success' : 'bg-secondary'}`}>
                                    {port.f_fs ? 'Yes' : 'No'}
                                </span>
                            </div>
                        </div>
                        <div className="row mt-2">
                            <div className="col-6">
                                <small className="text-muted">Averaging:</small><br/>
                                <span className={`badge ${port.f_avg ? 'bg-success' : 'bg-secondary'}`}>
                                    {port.f_avg ? 'Enabled' : 'Disabled'}
                                </span>
                            </div>
                            <div className="col-6">
                                <small className="text-muted">Monitor Interval:</small><br/>
                                <span>{port.i_monitor_interval || port.monitor_interval || 30}s</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Card Footer with Actions */}
            <div className="card-footer">
                <div className="d-flex justify-content-between align-items-center">
                    {/* Expand/Collapse Button */}
                    <button 
                        className="btn btn-outline-secondary btn-sm"
                        onClick={() => setIsExpanded(!isExpanded)}
                    >
                        {isExpanded ? '🔼 Less' : '🔽 More'}
                    </button>

                    {/* Action Buttons */}
                    {showActions && (
                        <div className="btn-group btn-group-sm">
                            <button 
                                className="btn btn-outline-primary"
                                onClick={() => window.open(`/components/port-monitoring/${port.i_prt || port.port}`, '_blank')}
                                title="View port details"
                            >
                                📊
                            </button>
                            
                            {type === 'candidate' && (
                                <button 
                                    className="btn btn-outline-success"
                                    onClick={() => handleAction('create_scaling')}
                                    disabled={isLoading}
                                    title="Create scaling port"
                                >
                                    {isLoading ? '⏳' : '➕'}
                                </button>
                            )}
                            
                            {type === 'scaling' && (
                                <button 
                                    className="btn btn-outline-danger"
                                    onClick={() => handleAction('remove_port')}
                                    disabled={isLoading}
                                    title="Remove scaling port"
                                >
                                    {isLoading ? '⏳' : '🗑️'}
                                </button>
                            )}
                            
                            <button 
                                className="btn btn-outline-info"
                                onClick={() => handleAction('health_check')}
                                disabled={isLoading}
                                title="Perform health check"
                            >
                                {isLoading ? '⏳' : '🔄'}
                            </button>
                        </div>
                    )}
                </div>

                {/* Last Updated Info */}
                <div className="text-center mt-2">
                    <small className="text-muted">
                        Last updated: {healthFormatters.formatTimestamp(new Date())}
                    </small>
                </div>
            </div>
        </div>
    );
};

export default ScalingPortCard;