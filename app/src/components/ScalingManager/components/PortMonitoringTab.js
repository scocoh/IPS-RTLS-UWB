/* Name: PortMonitoringTab.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Port monitoring configuration management interface */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from 'react';
import { monitoringAPI } from '../services/monitoringAPI';
import { portHelpers } from '../utils/portHelpers';
import { healthFormatters } from '../utils/healthFormatters';

const PortMonitoringTab = ({ onRefresh }) => {
    const [monitoringData, setMonitoringData] = useState(null);
    const [selectedPort, setSelectedPort] = useState(null);
    const [editingPort, setEditingPort] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    // Load monitoring data on component mount
    useEffect(() => {
        fetchMonitoringData();
    }, []);

    const fetchMonitoringData = async () => {
        setIsLoading(true);
        setError(null);
        
        try {
            console.log('🔍 Fetching port monitoring configuration...');
            const data = await monitoringAPI.getPortMonitoring();
            setMonitoringData(data);
            console.log('✅ Port monitoring data loaded:', data);
        } catch (err) {
            console.error('❌ Error fetching monitoring data:', err);
            setError(`Failed to load monitoring data: ${err.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    const handlePortSelect = async (port) => {
        if (selectedPort?.i_prt === port.i_prt) {
            setSelectedPort(null);
            return;
        }

        try {
            console.log(`🔍 Fetching details for port ${port.i_prt}...`);
            const details = await monitoringAPI.getPortMonitoringDetails(port.i_prt);
            setSelectedPort({ ...port, ...details });
            console.log('✅ Port details loaded:', details);
        } catch (err) {
            console.error(`❌ Error fetching port ${port.i_prt} details:`, err);
            setError(`Failed to load port details: ${err.message}`);
        }
    };

    const handleEditPort = (port) => {
        setEditingPort({
            port: port.i_prt,
            monitor_enabled: port.monitor_enabled || false,
            auto_expand: port.auto_expand || false,
            monitor_interval: port.monitor_interval || 30,
            monitor_timeout: port.monitor_timeout || 5,
            monitor_threshold: port.monitor_threshold || 2
        });
    };

    const handleSaveEdit = async () => {
        if (!editingPort) return;

        setIsSaving(true);
        setError(null);

        try {
            console.log(`💾 Saving configuration for port ${editingPort.port}...`);
            const result = await monitoringAPI.updatePortMonitoringConfig(editingPort.port, editingPort);
            
            setSuccessMessage(`Port ${editingPort.port} configuration updated successfully`);
            setEditingPort(null);
            
            // Refresh data
            await fetchMonitoringData();
            if (onRefresh) onRefresh();
            
            console.log('✅ Port configuration saved:', result);
        } catch (err) {
            console.error(`❌ Error saving port ${editingPort.port} config:`, err);
            setError(`Failed to save configuration: ${err.message}`);
        } finally {
            setIsSaving(false);
        }
    };

    const handleCancelEdit = () => {
        setEditingPort(null);
    };

    // Clear messages after 5 seconds
    useEffect(() => {
        if (successMessage) {
            const timer = setTimeout(() => setSuccessMessage(null), 5000);
            return () => clearTimeout(timer);
        }
    }, [successMessage]);

    useEffect(() => {
        if (error) {
            const timer = setTimeout(() => setError(null), 8000);
            return () => clearTimeout(timer);
        }
    }, [error]);

    if (isLoading) {
        return (
            <div className="port-monitoring-tab">
                <div className="text-center py-5">
                    <div className="spinner-border text-primary" role="status">
                        <span className="visually-hidden">Loading monitoring configuration...</span>
                    </div>
                    <p className="mt-2">Loading port monitoring configuration...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="port-monitoring-tab">
            <div className="tab-header d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h3>👁️ Port Monitoring Configuration</h3>
                    <p className="text-muted">Configure monitoring settings for individual ports</p>
                </div>
                <button 
                    className="btn btn-outline-primary"
                    onClick={fetchMonitoringData}
                    disabled={isLoading}
                >
                    🔄 Refresh Config
                </button>
            </div>

            {/* Messages */}
            {error && (
                <div className="alert alert-danger alert-dismissible fade show">
                    <strong>Error:</strong> {error}
                    <button type="button" className="btn-close" onClick={() => setError(null)}></button>
                </div>
            )}

            {successMessage && (
                <div className="alert alert-success alert-dismissible fade show">
                    <strong>Success:</strong> {successMessage}
                    <button type="button" className="btn-close" onClick={() => setSuccessMessage(null)}></button>
                </div>
            )}

            {/* Monitoring Summary */}
            {monitoringData && (
                <div className="row mb-4">
                    <div className="col-md-3">
                        <div className="card text-center">
                            <div className="card-body">
                                <h4 className="text-primary">{monitoringData.total_ports}</h4>
                                <p className="card-text">Total Ports</p>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-3">
                        <div className="card text-center">
                            <div className="card-body">
                                <h4 className="text-success">{monitoringData.monitored_ports}</h4>
                                <p className="card-text">Monitored</p>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-3">
                        <div className="card text-center">
                            <div className="card-body">
                                <h4 className="text-info">{monitoringData.auto_expand_ports}</h4>
                                <p className="card-text">Auto-Expand</p>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-3">
                        <div className="card text-center">
                            <div className="card-body">
                                <h4 className="text-warning">{monitoringData.scaling_candidates?.length || 0}</h4>
                                <p className="card-text">Scaling Candidates</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <div className="row">
                {/* Port List */}
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-header">
                            <h5>Port Configuration List</h5>
                        </div>
                        <div className="card-body" style={{ maxHeight: '500px', overflowY: 'auto' }}>
                            {monitoringData?.inbound_ports && (
                                <div className="mb-4">
                                    <h6 className="text-primary">🔵 Inbound Ports ({monitoringData.inbound_ports.length})</h6>
                                    {monitoringData.inbound_ports.map(port => (
                                        <div 
                                            key={port.i_prt} 
                                            className={`port-item card mb-2 ${selectedPort?.i_prt === port.i_prt ? 'border-primary' : ''}`}
                                            style={{ cursor: 'pointer' }}
                                            onClick={() => handlePortSelect(port)}
                                        >
                                            <div className="card-body py-2">
                                                <div className="d-flex justify-content-between align-items-center">
                                                    <div>
                                                        <strong>Port {port.i_prt}</strong>
                                                        <small className="d-block text-muted">{port.x_nm_res}</small>
                                                    </div>
                                                    <div className="text-end">
                                                        <span className={`badge ${port.monitor_enabled ? 'bg-success' : 'bg-secondary'} me-1`}>
                                                            {port.monitor_enabled ? 'Monitored' : 'Unmonitored'}
                                                        </span>
                                                        {port.auto_expand && (
                                                            <span className="badge bg-warning">Auto-Expand</span>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {monitoringData?.outbound_ports && (
                                <div className="mb-4">
                                    <h6 className="text-success">🟢 Outbound Ports ({monitoringData.outbound_ports.length})</h6>
                                    {monitoringData.outbound_ports.map(port => (
                                        <div 
                                            key={port.i_prt} 
                                            className={`port-item card mb-2 ${selectedPort?.i_prt === port.i_prt ? 'border-primary' : ''}`}
                                            style={{ cursor: 'pointer' }}
                                            onClick={() => handlePortSelect(port)}
                                        >
                                            <div className="card-body py-2">
                                                <div className="d-flex justify-content-between align-items-center">
                                                    <div>
                                                        <strong>Port {port.i_prt}</strong>
                                                        <small className="d-block text-muted">{port.x_nm_res}</small>
                                                    </div>
                                                    <div className="text-end">
                                                        <span className={`badge ${port.monitor_enabled ? 'bg-success' : 'bg-secondary'} me-1`}>
                                                            {port.monitor_enabled ? 'Monitored' : 'Unmonitored'}
                                                        </span>
                                                        {port.auto_expand && (
                                                            <span className="badge bg-warning">Auto-Expand</span>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {monitoringData?.scaling_candidates && monitoringData.scaling_candidates.length > 0 && (
                                <div className="mb-4">
                                    <h6 className="text-warning">🟡 Scaling Candidates ({monitoringData.scaling_candidates.length})</h6>
                                    {monitoringData.scaling_candidates.map(port => (
                                        <div 
                                            key={port.i_prt} 
                                            className={`port-item card mb-2 border-warning ${selectedPort?.i_prt === port.i_prt ? 'border-primary' : ''}`}
                                            style={{ cursor: 'pointer' }}
                                            onClick={() => handlePortSelect(port)}
                                        >
                                            <div className="card-body py-2">
                                                <div className="d-flex justify-content-between align-items-center">
                                                    <div>
                                                        <strong>Port {port.i_prt}</strong>
                                                        <small className="d-block text-muted">{port.x_nm_res}</small>
                                                    </div>
                                                    <div className="text-end">
                                                        <span className="badge bg-warning">Scaling Candidate</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Port Details/Configuration */}
                <div className="col-md-6">
                    {selectedPort ? (
                        <div className="card">
                            <div className="card-header d-flex justify-content-between align-items-center">
                                <h5>Port {selectedPort.i_prt} Configuration</h5>
                                <button 
                                    className="btn btn-outline-secondary btn-sm"
                                    onClick={() => handleEditPort(selectedPort)}
                                    disabled={editingPort !== null}
                                >
                                    ✏️ Edit
                                </button>
                            </div>
                            <div className="card-body">
                                {editingPort && editingPort.port === selectedPort.i_prt ? (
                                    /* Edit Mode */
                                    <div className="edit-mode">
                                        <div className="mb-3">
                                            <div className="form-check">
                                                <input 
                                                    className="form-check-input"
                                                    type="checkbox"
                                                    checked={editingPort.monitor_enabled}
                                                    onChange={(e) => setEditingPort({
                                                        ...editingPort,
                                                        monitor_enabled: e.target.checked
                                                    })}
                                                    id="monitorEnabled"
                                                />
                                                <label className="form-check-label" htmlFor="monitorEnabled">
                                                    Enable Monitoring
                                                </label>
                                            </div>
                                        </div>

                                        <div className="mb-3">
                                            <div className="form-check">
                                                <input 
                                                    className="form-check-input"
                                                    type="checkbox"
                                                    checked={editingPort.auto_expand}
                                                    onChange={(e) => setEditingPort({
                                                        ...editingPort,
                                                        auto_expand: e.target.checked
                                                    })}
                                                    id="autoExpand"
                                                />
                                                <label className="form-check-label" htmlFor="autoExpand">
                                                    Enable Auto-Expansion
                                                </label>
                                            </div>
                                        </div>

                                        <div className="mb-3">
                                            <label className="form-label">Monitor Interval (seconds):</label>
                                            <input 
                                                type="number"
                                                className="form-control"
                                                value={editingPort.monitor_interval}
                                                onChange={(e) => setEditingPort({
                                                    ...editingPort,
                                                    monitor_interval: parseInt(e.target.value) || 30
                                                })}
                                                min="5"
                                                max="300"
                                            />
                                        </div>

                                        <div className="mb-3">
                                            <label className="form-label">Monitor Timeout (seconds):</label>
                                            <input 
                                                type="number"
                                                className="form-control"
                                                value={editingPort.monitor_timeout}
                                                onChange={(e) => setEditingPort({
                                                    ...editingPort,
                                                    monitor_timeout: parseInt(e.target.value) || 5
                                                })}
                                                min="1"
                                                max="30"
                                            />
                                        </div>

                                        <div className="mb-3">
                                            <label className="form-label">Health Check Threshold:</label>
                                            <input 
                                                type="number"
                                                className="form-control"
                                                value={editingPort.monitor_threshold}
                                                onChange={(e) => setEditingPort({
                                                    ...editingPort,
                                                    monitor_threshold: parseInt(e.target.value) || 2
                                                })}
                                                min="1"
                                                max="10"
                                            />
                                            <small className="text-muted">Failed checks before marking unhealthy</small>
                                        </div>

                                        <div className="d-flex gap-2">
                                            <button 
                                                className="btn btn-success"
                                                onClick={handleSaveEdit}
                                                disabled={isSaving}
                                            >
                                                {isSaving ? '💾 Saving...' : '💾 Save Changes'}
                                            </button>
                                            <button 
                                                className="btn btn-secondary"
                                                onClick={handleCancelEdit}
                                                disabled={isSaving}
                                            >
                                                ❌ Cancel
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    /* View Mode */
                                    <div className="view-mode">
                                        <div className="row mb-3">
                                            <div className="col-6">
                                                <small className="text-muted">Resource Name:</small><br/>
                                                <strong>{selectedPort.x_nm_res}</strong>
                                            </div>
                                            <div className="col-6">
                                                <small className="text-muted">Type:</small><br/>
                                                <span className="badge bg-secondary">
                                                    {healthFormatters.getPortTypeDescription(selectedPort.i_typ_res)}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="row mb-3">
                                            <div className="col-6">
                                                <small className="text-muted">Monitoring:</small><br/>
                                                <span className={`badge ${selectedPort.monitor_enabled ? 'bg-success' : 'bg-secondary'}`}>
                                                    {selectedPort.monitor_enabled ? 'Enabled' : 'Disabled'}
                                                </span>
                                            </div>
                                            <div className="col-6">
                                                <small className="text-muted">Auto-Expand:</small><br/>
                                                <span className={`badge ${selectedPort.auto_expand ? 'bg-warning' : 'bg-secondary'}`}>
                                                    {selectedPort.auto_expand ? 'Enabled' : 'Disabled'}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="row mb-3">
                                            <div className="col-6">
                                                <small className="text-muted">Monitor Interval:</small><br/>
                                                <span>{selectedPort.monitor_interval || 30} seconds</span>
                                            </div>
                                            <div className="col-6">
                                                <small className="text-muted">Monitor Timeout:</small><br/>
                                                <span>{selectedPort.monitor_timeout || 5} seconds</span>
                                            </div>
                                        </div>

                                        <div className="row mb-3">
                                            <div className="col-6">
                                                <small className="text-muted">Health Threshold:</small><br/>
                                                <span>{selectedPort.monitor_threshold || 2} failed checks</span>
                                            </div>
                                            <div className="col-6">
                                                <small className="text-muted">IP Address:</small><br/>
                                                <code>{selectedPort.x_ip || 'localhost'}</code>
                                            </div>
                                        </div>

                                        {selectedPort.can_scale && (
                                            <div className="scaling-info border-top pt-3">
                                                <small className="text-muted">Scaling Information:</small><br/>
                                                <span className="badge bg-info">Can Scale</span>
                                                {selectedPort.scaling_range && (
                                                    <span className="ms-2">
                                                        Range: <code>{selectedPort.scaling_range}</code>
                                                    </span>
                                                )}
                                            </div>
                                        )}

                                        <div className="actions mt-3">
                                            <button 
                                                className="btn btn-outline-info btn-sm me-2"
                                                onClick={() => window.open(`/components/port-monitoring/${selectedPort.i_prt}`, '_blank')}
                                            >
                                                📊 View API Details
                                            </button>
                                            {portHelpers.isScalingPort(selectedPort.i_prt) && (
                                                <button 
                                                    className="btn btn-outline-danger btn-sm"
                                                    onClick={() => {
                                                        if (window.confirm(`Remove scaling port ${selectedPort.i_prt}?`)) {
                                                            console.log(`Removing port ${selectedPort.i_prt}`);
                                                        }
                                                    }}
                                                >
                                                    🗑️ Remove Port
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="card">
                            <div className="card-body text-center py-5">
                                <h5 className="text-muted">Select a Port</h5>
                                <p className="text-muted">Choose a port from the list to view and edit its configuration</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Configuration Help */}
            <div className="card mt-4">
                <div className="card-header">
                    <h6>ℹ️ Configuration Help</h6>
                </div>
                <div className="card-body">
                    <div className="row">
                        <div className="col-md-3">
                            <strong>Monitor Interval:</strong>
                            <p className="small">How often to check port health (5-300 seconds)</p>
                        </div>
                        <div className="col-md-3">
                            <strong>Monitor Timeout:</strong>
                            <p className="small">Maximum wait time for health check response (1-30 seconds)</p>
                        </div>
                        <div className="col-md-3">
                            <strong>Health Threshold:</strong>
                            <p className="small">Number of consecutive failed checks before marking unhealthy (1-10)</p>
                        </div>
                        <div className="col-md-3">
                            <strong>Auto-Expand:</strong>
                            <p className="small">Allow automatic creation of scaling ports when needed</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PortMonitoringTab;