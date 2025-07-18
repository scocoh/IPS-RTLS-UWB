/* Name: ScalingStatusTab.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Scaling status overview dashboard with comprehensive scaling metrics */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useMemo } from 'react';
import ScalingPortCard from '../modules/ScalingPortCard';
import { portHelpers } from '../utils/portHelpers';

const ScalingStatusTab = ({ 
    scalingStatus, 
    scalingCandidates, 
    portHealth, 
    isLoading, 
    onRefresh 
}) => {
    // Calculate comprehensive scaling metrics
    const scalingMetrics = useMemo(() => {
        if (!scalingStatus) {
            return {
                candidates: 0,
                availableSlots: 0,
                activeInstances: 0,
                utilizationPercentage: 0,
                capacity: 'unknown',
                recommendations: []
            };
        }

        const candidates = scalingStatus.scaling_candidates?.length || 0;
        const availableSlots = scalingStatus.available_scaling_ports?.length || 0;
        const activeInstances = scalingStatus.active_scaling_ports?.length || 0;
        const totalSlots = availableSlots + activeInstances;
        
        const utilizationPercentage = totalSlots > 0 ? Math.round((activeInstances / totalSlots) * 100) : 0;
        
        let capacity = 'unknown';
        if (utilizationPercentage < 25) capacity = 'low';
        else if (utilizationPercentage < 50) capacity = 'moderate';
        else if (utilizationPercentage < 75) capacity = 'high';
        else capacity = 'critical';

        // Generate recommendations
        const recommendations = [];
        if (availableSlots < 5) {
            recommendations.push({
                type: 'warning',
                message: `Only ${availableSlots} scaling slots remaining`,
                action: 'monitor_capacity'
            });
        }
        if (activeInstances === 0 && candidates > 0) {
            recommendations.push({
                type: 'info',
                message: 'No active scaling instances - system ready for scaling',
                action: 'ready_to_scale'
            });
        }
        if (portHealth?.fallback_mode) {
            recommendations.push({
                type: 'warning',
                message: 'Heartbeat integration unavailable - limited health monitoring',
                action: 'check_integration'
            });
        }

        return {
            candidates,
            availableSlots,
            activeInstances,
            totalSlots,
            utilizationPercentage,
            capacity,
            recommendations
        };
    }, [scalingStatus, portHealth]);

    // Process port ranges for visualization
    const portRanges = useMemo(() => {
        const ranges = {
            inbound: { start: 18000, end: 18999, active: [] },
            outbound: { start: 8000, end: 8199, active: [] },
            scaling: { start: 8200, end: 8299, active: [] }
        };

        if (scalingStatus?.active_scaling_ports) {
            scalingStatus.active_scaling_ports.forEach(port => {
                if (port >= 18000) ranges.inbound.active.push(port);
                else if (port >= 8200) ranges.scaling.active.push(port);
                else if (port >= 8000) ranges.outbound.active.push(port);
            });
        }

        return ranges;
    }, [scalingStatus]);

    if (isLoading) {
        return (
            <div className="scaling-status-tab">
                <div className="text-center py-5">
                    <div className="spinner-border text-primary" role="status">
                        <span className="visually-hidden">Loading scaling status...</span>
                    </div>
                    <p className="mt-2">Loading scaling status...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="scaling-status-tab">
            <div className="tab-header d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h3>📊 Scaling Status Overview</h3>
                    <p className="text-muted">Comprehensive view of conductor scaling system status</p>
                </div>
                <button 
                    className="btn btn-outline-primary"
                    onClick={onRefresh}
                    disabled={isLoading}
                >
                    🔄 Refresh Status
                </button>
            </div>

            {/* Key Metrics Cards */}
            <div className="row mb-4">
                <div className="col-md-3">
                    <div className="card text-center h-100">
                        <div className="card-body">
                            <h3 className="text-primary">{scalingMetrics.candidates}</h3>
                            <p className="card-text">Scaling Candidates</p>
                            <small className="text-muted">Ports configured for auto-expansion</small>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center h-100">
                        <div className="card-body">
                            <h3 className="text-success">{scalingMetrics.availableSlots}</h3>
                            <p className="card-text">Available Slots</p>
                            <small className="text-muted">Ready for new scaling instances</small>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center h-100">
                        <div className="card-body">
                            <h3 className="text-warning">{scalingMetrics.activeInstances}</h3>
                            <p className="card-text">Active Instances</p>
                            <small className="text-muted">Currently running scaling ports</small>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center h-100">
                        <div className="card-body">
                            <h3 className={`text-${scalingMetrics.capacity === 'critical' ? 'danger' : 
                                scalingMetrics.capacity === 'high' ? 'warning' : 'success'}`}>
                                {scalingMetrics.utilizationPercentage}%
                            </h3>
                            <p className="card-text">Utilization</p>
                            <small className="text-muted">Capacity: {scalingMetrics.capacity}</small>
                        </div>
                    </div>
                </div>
            </div>

            {/* Recommendations */}
            {scalingMetrics.recommendations.length > 0 && (
                <div className="row mb-4">
                    <div className="col-12">
                        <div className="card">
                            <div className="card-header">
                                <h5>💡 System Recommendations</h5>
                            </div>
                            <div className="card-body">
                                {scalingMetrics.recommendations.map((rec, index) => (
                                    <div 
                                        key={index}
                                        className={`alert alert-${rec.type === 'warning' ? 'warning' : 
                                            rec.type === 'info' ? 'info' : 'primary'} mb-2`}
                                    >
                                        <strong>{rec.message}</strong>
                                        <small className="d-block mt-1">Action: {rec.action}</small>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Port Range Visualization */}
            <div className="row mb-4">
                <div className="col-md-4">
                    <div className="card">
                        <div className="card-header">
                            <h6>🔵 Inbound Ports (18000+)</h6>
                        </div>
                        <div className="card-body">
                            <div className="d-flex justify-content-between mb-2">
                                <span>Range:</span>
                                <code>{portRanges.inbound.start}-{portRanges.inbound.end}</code>
                            </div>
                            <div className="d-flex justify-content-between mb-2">
                                <span>Active:</span>
                                <span className="badge bg-primary">{portRanges.inbound.active.length}</span>
                            </div>
                            <div className="progress">
                                <div 
                                    className="progress-bar bg-primary"
                                    style={{ width: `${Math.min((portRanges.inbound.active.length / 100) * 100, 100)}%` }}
                                />
                            </div>
                        </div>
                    </div>
                </div>
                <div className="col-md-4">
                    <div className="card">
                        <div className="card-header">
                            <h6>🟢 Outbound Ports (8000-8199)</h6>
                        </div>
                        <div className="card-body">
                            <div className="d-flex justify-content-between mb-2">
                                <span>Range:</span>
                                <code>{portRanges.outbound.start}-{portRanges.outbound.end}</code>
                            </div>
                            <div className="d-flex justify-content-between mb-2">
                                <span>Active:</span>
                                <span className="badge bg-success">{portRanges.outbound.active.length}</span>
                            </div>
                            <div className="progress">
                                <div 
                                    className="progress-bar bg-success"
                                    style={{ width: `${Math.min((portRanges.outbound.active.length / 200) * 100, 100)}%` }}
                                />
                            </div>
                        </div>
                    </div>
                </div>
                <div className="col-md-4">
                    <div className="card">
                        <div className="card-header">
                            <h6>🟡 Scaling Ports (8200-8299)</h6>
                        </div>
                        <div className="card-body">
                            <div className="d-flex justify-content-between mb-2">
                                <span>Range:</span>
                                <code>{portRanges.scaling.start}-{portRanges.scaling.end}</code>
                            </div>
                            <div className="d-flex justify-content-between mb-2">
                                <span>Active:</span>
                                <span className="badge bg-warning">{portRanges.scaling.active.length}</span>
                            </div>
                            <div className="progress">
                                <div 
                                    className="progress-bar bg-warning"
                                    style={{ width: `${Math.min((portRanges.scaling.active.length / 100) * 100, 100)}%` }}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Scaling Candidates Details */}
            <div className="row mb-4">
                <div className="col-12">
                    <div className="card">
                        <div className="card-header">
                            <h5>🎯 Scaling Candidates</h5>
                        </div>
                        <div className="card-body">
                            {scalingCandidates && scalingCandidates.length > 0 ? (
                                <div className="row">
                                    {scalingCandidates.map(candidate => (
                                        <div key={candidate.i_prt} className="col-md-6 mb-3">
                                            <ScalingPortCard 
                                                port={candidate}
                                                type="candidate"
                                                showActions={false}
                                                compact={false}
                                            />
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-4 text-muted">
                                    <h5>No Scaling Candidates</h5>
                                    <p>No ports are currently configured for auto-expansion.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Active Scaling Instances */}
            {scalingStatus?.active_scaling_ports && scalingStatus.active_scaling_ports.length > 0 && (
                <div className="row mb-4">
                    <div className="col-12">
                        <div className="card">
                            <div className="card-header">
                                <h5>⚡ Active Scaling Instances</h5>
                            </div>
                            <div className="card-body">
                                <div className="row">
                                    {scalingStatus.active_scaling_ports.map(port => (
                                        <div key={port} className="col-md-3 mb-2">
                                            <div className="card bg-light">
                                                <div className="card-body text-center py-2">
                                                    <h6 className="mb-1">Port {port}</h6>
                                                    <small className="text-muted">
                                                        {portHelpers.getPortTypeDescription(port)}
                                                    </small>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* System Health Integration Status */}
            <div className="card">
                <div className="card-header">
                    <h5>🔧 System Integration Status</h5>
                </div>
                <div className="card-body">
                    <div className="row">
                        <div className="col-md-3">
                            <div className="text-center">
                                <div className={`badge ${portHealth?.fallback_mode ? 'bg-warning' : 'bg-success'} mb-2 p-2`}>
                                    {portHealth?.fallback_mode ? '⚠️' : '✅'}
                                </div>
                                <h6>Heartbeat Integration</h6>
                                <small className="text-muted">
                                    {portHealth?.fallback_mode ? 'Fallback Mode' : 'Active'}
                                </small>
                            </div>
                        </div>
                        <div className="col-md-3">
                            <div className="text-center">
                                <div className="badge bg-success mb-2 p-2">✅</div>
                                <h6>Database Connection</h6>
                                <small className="text-muted">Connected</small>
                            </div>
                        </div>
                        <div className="col-md-3">
                            <div className="text-center">
                                <div className="badge bg-success mb-2 p-2">✅</div>
                                <h6>Scaling API</h6>
                                <small className="text-muted">Operational</small>
                            </div>
                        </div>
                        <div className="col-md-3">
                            <div className="text-center">
                                <div className="badge bg-info mb-2 p-2">ℹ️</div>
                                <h6>Thread 3 Status</h6>
                                <small className="text-muted">Manual Scaling Active</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ScalingStatusTab;