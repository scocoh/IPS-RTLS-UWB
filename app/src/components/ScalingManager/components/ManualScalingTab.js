/* Name: ManualScalingTab.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Manual scaling controls for port creation and removal */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from 'react';
import ScalingPortCard from '../modules/ScalingPortCard';
import { portHelpers } from '../utils/portHelpers';

const ManualScalingTab = ({ 
    scalingCandidates, 
    createPort, 
    removePort, 
    getNextPort, 
    isLoading, 
    onSuccess 
}) => {
    const [selectedBasePort, setSelectedBasePort] = useState(8002);
    const [nextAvailablePort, setNextAvailablePort] = useState(null);
    const [portToRemove, setPortToRemove] = useState('');
    const [batchCount, setBatchCount] = useState(1);
    const [operationResult, setOperationResult] = useState(null);
    const [isGettingNext, setIsGettingNext] = useState(false);

    // Get next available port when base port changes
    useEffect(() => {
        const fetchNextPort = async () => {
            if (selectedBasePort) {
                setIsGettingNext(true);
                try {
                    const result = await getNextPort(selectedBasePort);
                    setNextAvailablePort(result.next_available_port);
                } catch (error) {
                    console.error('Error getting next port:', error);
                    setNextAvailablePort(null);
                } finally {
                    setIsGettingNext(false);
                }
            }
        };

        fetchNextPort();
    }, [selectedBasePort, getNextPort]);

    // Handle creating a single port
    const handleCreatePort = async () => {
        if (!nextAvailablePort) return;

        try {
            const result = await createPort(nextAvailablePort);
            
            if (result.success) {
                setOperationResult({
                    type: 'success',
                    message: `Port ${nextAvailablePort} created successfully!`,
                    details: result.data
                });
                
                // Refresh next available port
                const nextResult = await getNextPort(selectedBasePort);
                setNextAvailablePort(nextResult.next_available_port);
                
                if (onSuccess) onSuccess();
            } else {
                setOperationResult({
                    type: 'error',
                    message: `Failed to create port ${nextAvailablePort}`,
                    details: result.error
                });
            }
        } catch (error) {
            setOperationResult({
                type: 'error',
                message: `Error creating port: ${error.message}`
            });
        }
    };

    // Handle removing a port
    const handleRemovePort = async () => {
        const port = parseInt(portToRemove);
        if (!port || port < 8200 || port > 8299) {
            setOperationResult({
                type: 'error',
                message: 'Please enter a valid port number (8200-8299)'
            });
            return;
        }

        try {
            const result = await removePort(port);
            
            if (result.success) {
                setOperationResult({
                    type: 'success',
                    message: `Port ${port} removed successfully!`,
                    details: result.data
                });
                setPortToRemove('');
                
                if (onSuccess) onSuccess();
            } else {
                setOperationResult({
                    type: 'error',
                    message: `Failed to remove port ${port}`,
                    details: result.error
                });
            }
        } catch (error) {
            setOperationResult({
                type: 'error',
                message: `Error removing port: ${error.message}`
            });
        }
    };

    // Handle batch port creation
    const handleBatchCreate = async () => {
        if (!nextAvailablePort || batchCount < 1 || batchCount > 10) {
            setOperationResult({
                type: 'error',
                message: 'Please enter a valid batch count (1-10)'
            });
            return;
        }

        try {
            const results = [];
            let currentNextPort = nextAvailablePort;
            
            for (let i = 0; i < batchCount; i++) {
                const result = await createPort(currentNextPort);
                results.push({ port: currentNextPort, result });
                
                if (result.success && i < batchCount - 1) {
                    // Get next port for next iteration
                    const nextResult = await getNextPort(selectedBasePort);
                    currentNextPort = nextResult.next_available_port;
                } else if (!result.success) {
                    break; // Stop on first failure
                }
            }
            
            const successful = results.filter(r => r.result.success).length;
            const failed = results.length - successful;
            
            setOperationResult({
                type: successful === batchCount ? 'success' : 'warning',
                message: `Batch creation: ${successful} successful, ${failed} failed`,
                details: results
            });
            
            // Refresh next available port
            const nextResult = await getNextPort(selectedBasePort);
            setNextAvailablePort(nextResult.next_available_port);
            
            if (onSuccess) onSuccess();
        } catch (error) {
            setOperationResult({
                type: 'error',
                message: `Batch creation error: ${error.message}`
            });
        }
    };

    // Clear operation result after 5 seconds
    useEffect(() => {
        if (operationResult) {
            const timer = setTimeout(() => {
                setOperationResult(null);
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [operationResult]);

    return (
        <div className="manual-scaling-tab">
            <div className="tab-header">
                <h3>🚀 Manual Scaling Controls</h3>
                <p>Create and remove scaling ports in the 8200-8299 range</p>
            </div>

            {/* Operation Result Alert */}
            {operationResult && (
                <div className={`alert alert-${operationResult.type === 'success' ? 'success' : operationResult.type === 'warning' ? 'warning' : 'danger'}`}>
                    <strong>{operationResult.message}</strong>
                    {operationResult.details && (
                        <div className="mt-2">
                            <small>{JSON.stringify(operationResult.details, null, 2)}</small>
                        </div>
                    )}
                </div>
            )}

            <div className="row">
                {/* Scaling Candidates */}
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-header">
                            <h5>📊 Scaling Candidates</h5>
                        </div>
                        <div className="card-body">
                            {scalingCandidates && scalingCandidates.length > 0 ? (
                                <div>
                                    {scalingCandidates.map(candidate => (
                                        <ScalingPortCard 
                                            key={candidate.i_prt}
                                            port={candidate}
                                            type="candidate"
                                        />
                                    ))}
                                </div>
                            ) : (
                                <p className="text-muted">No scaling candidates configured</p>
                            )}
                        </div>
                    </div>
                </div>

                {/* Port Creation Controls */}
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-header">
                            <h5>➕ Create Scaling Port</h5>
                        </div>
                        <div className="card-body">
                            {/* Base Port Selection */}
                            <div className="mb-3">
                                <label className="form-label">Base Port:</label>
                                <select 
                                    className="form-select"
                                    value={selectedBasePort}
                                    onChange={(e) => setSelectedBasePort(parseInt(e.target.value))}
                                    disabled={isLoading}
                                >
                                    {scalingCandidates?.map(candidate => (
                                        <option key={candidate.i_prt} value={candidate.i_prt}>
                                            {candidate.i_prt} - {candidate.x_nm_res}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Next Available Port */}
                            <div className="mb-3">
                                <label className="form-label">Next Available Port:</label>
                                <div className="input-group">
                                    <input 
                                        type="text"
                                        className="form-control"
                                        value={isGettingNext ? 'Loading...' : (nextAvailablePort || 'N/A')}
                                        readOnly
                                    />
                                    <span className="input-group-text">
                                        {portHelpers.getPortRangeInfo(selectedBasePort).range}
                                    </span>
                                </div>
                            </div>

                            {/* Single Port Creation */}
                            <div className="mb-3">
                                <button 
                                    className="btn btn-primary w-100"
                                    onClick={handleCreatePort}
                                    disabled={isLoading || !nextAvailablePort || isGettingNext}
                                >
                                    {isLoading ? '🔄 Creating...' : '➕ Create Single Port'}
                                </button>
                            </div>

                            {/* Batch Creation */}
                            <div className="border-top pt-3">
                                <label className="form-label">Batch Create:</label>
                                <div className="input-group mb-2">
                                    <input 
                                        type="number"
                                        className="form-control"
                                        value={batchCount}
                                        onChange={(e) => setBatchCount(parseInt(e.target.value) || 1)}
                                        min="1"
                                        max="10"
                                        disabled={isLoading}
                                    />
                                    <span className="input-group-text">ports</span>
                                </div>
                                <button 
                                    className="btn btn-warning w-100"
                                    onClick={handleBatchCreate}
                                    disabled={isLoading || !nextAvailablePort || batchCount < 1 || batchCount > 10}
                                >
                                    {isLoading ? '🔄 Creating...' : `➕ Create ${batchCount} Ports`}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="row mt-4">
                {/* Port Removal Controls */}
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-header">
                            <h5>🗑️ Remove Scaling Port</h5>
                        </div>
                        <div className="card-body">
                            <div className="mb-3">
                                <label className="form-label">Port to Remove:</label>
                                <input 
                                    type="number"
                                    className="form-control"
                                    value={portToRemove}
                                    onChange={(e) => setPortToRemove(e.target.value)}
                                    placeholder="Enter port number (8200-8299)"
                                    min="8200"
                                    max="8299"
                                    disabled={isLoading}
                                />
                            </div>
                            <button 
                                className="btn btn-danger w-100"
                                onClick={handleRemovePort}
                                disabled={isLoading || !portToRemove}
                            >
                                {isLoading ? '🔄 Removing...' : '🗑️ Remove Port'}
                            </button>
                            <small className="text-muted d-block mt-2">
                                ⚠️ Only ports in range 8200-8299 can be removed
                            </small>
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-header">
                            <h5>⚡ Quick Actions</h5>
                        </div>
                        <div className="card-body">
                            <div className="d-grid gap-2">
                                <button 
                                    className="btn btn-outline-primary"
                                    onClick={() => window.open(`/components/scaling/status`, '_blank')}
                                >
                                    📊 View Full Status (API)
                                </button>
                                <button 
                                    className="btn btn-outline-info"
                                    onClick={() => window.open(`/components/scaling-candidates`, '_blank')}
                                >
                                    📋 View Candidates (API)
                                </button>
                                <button 
                                    className="btn btn-outline-secondary"
                                    onClick={() => window.open(`/components/menu/scaling`, '_blank')}
                                >
                                    📜 Scaling Menu (API)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Help Section */}
            <div className="card mt-4">
                <div className="card-header">
                    <h6>ℹ️ Manual Scaling Help</h6>
                </div>
                <div className="card-body">
                    <div className="row">
                        <div className="col-md-4">
                            <strong>Scaling Range:</strong>
                            <p className="small">Ports 8200-8299 are reserved for scaling instances of RealTime WebSocket (port 8002).</p>
                        </div>
                        <div className="col-md-4">
                            <strong>Creation Process:</strong>
                            <p className="small">New ports inherit configuration from base port but are marked as non-auto-expanding.</p>
                        </div>
                        <div className="col-md-4">
                            <strong>Health Thresholds:</strong>
                            <p className="small">Response times: 200-750ms healthy, above 750ms unhealthy.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ManualScalingTab;