/* Name: SM_index.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Main Scaling Manager component for ParcoRTLS port health and scaling management */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from 'react';
import PortHealthTab from './components/PortHealthTab';
import ManualScalingTab from './components/ManualScalingTab';
import ScalingStatusTab from './components/ScalingStatusTab';
import PortMonitoringTab from './components/PortMonitoringTab';
import RealTimePortDisplay from './components/RealTimePortDisplay';
import { usePortHealth } from './hooks/usePortHealth';
import { useScalingAPI } from './hooks/useScalingAPI';
import { useRealTimeUpdates } from './hooks/useRealTimeUpdates';
import AlertSystem from './modules/AlertSystem';
import './styles/ScalingManager.css';

const ScalingManager = () => {
    const [activeTab, setActiveTab] = useState('status');
    const [refreshTrigger, setRefreshTrigger] = useState(0);
    
    // Custom hooks for data management
    const { 
        portHealth, 
        unhealthyPorts, 
        refreshPortHealth, 
        isLoading: healthLoading 
    } = usePortHealth(refreshTrigger);
    
    const {
        scalingStatus,
        scalingCandidates,
        createPort,
        removePort,
        getNextPort,
        isLoading: scalingLoading
    } = useScalingAPI(refreshTrigger);
    
    const {
        realTimeData,
        isConnected: realtimeConnected
    } = useRealTimeUpdates();

    // Manual refresh function
    const handleRefresh = () => {
        setRefreshTrigger(prev => prev + 1);
        refreshPortHealth();
    };

    // Tab configuration
    const tabs = [
        { id: 'status', label: 'Scaling Status', icon: '📊' },
        { id: 'health', label: 'Port Health', icon: '💚' },
        { id: 'scaling', label: 'Manual Scaling', icon: '⚡' },
        { id: 'monitoring', label: 'Port Monitoring', icon: '👁️' },
        { id: 'realtime', label: 'Real-Time Display', icon: '📡' }
    ];

    return (
        <div className="scaling-manager">
            <div className="scaling-header">
                <h2>
                    <span className="header-icon">🛠️</span>
                    Conductor Scaling Management
                </h2>
                <div className="header-controls">
                    <div className="status-indicators">
                        <span className={`indicator ${realtimeConnected ? 'connected' : 'disconnected'}`}>
                            {realtimeConnected ? '🟢' : '🔴'} Real-Time
                        </span>
                        <span className={`indicator ${unhealthyPorts?.length === 0 ? 'healthy' : 'unhealthy'}`}>
                            {unhealthyPorts?.length === 0 ? '🟢' : '🟡'} Health
                        </span>
                    </div>
                    <button 
                        className="refresh-btn"
                        onClick={handleRefresh}
                        disabled={healthLoading || scalingLoading}
                    >
                        {healthLoading || scalingLoading ? '🔄' : '🔄'} Refresh
                    </button>
                </div>
            </div>

            {/* Alert System */}
            <AlertSystem 
                unhealthyPorts={unhealthyPorts}
                scalingStatus={scalingStatus}
                realTimeConnected={realtimeConnected}
            />

            {/* Tab Navigation */}
            <div className="tab-navigation">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        <span className="tab-icon">{tab.icon}</span>
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="tab-content">
                {activeTab === 'status' && (
                    <ScalingStatusTab
                        scalingStatus={scalingStatus}
                        scalingCandidates={scalingCandidates}
                        portHealth={portHealth}
                        isLoading={scalingLoading}
                        onRefresh={handleRefresh}
                    />
                )}

                {activeTab === 'health' && (
                    <PortHealthTab
                        portHealth={portHealth}
                        unhealthyPorts={unhealthyPorts}
                        isLoading={healthLoading}
                        onRefresh={refreshPortHealth}
                    />
                )}

                {activeTab === 'scaling' && (
                    <ManualScalingTab
                        scalingCandidates={scalingCandidates}
                        createPort={createPort}
                        removePort={removePort}
                        getNextPort={getNextPort}
                        isLoading={scalingLoading}
                        onSuccess={handleRefresh}
                    />
                )}

                {activeTab === 'monitoring' && (
                    <PortMonitoringTab
                        onRefresh={handleRefresh}
                    />
                )}

                {activeTab === 'realtime' && (
                    <RealTimePortDisplay
                        realTimeData={realTimeData}
                        isConnected={realtimeConnected}
                        portHealth={portHealth}
                    />
                )}
            </div>

            {/* Footer with version and connection info */}
            <div className="scaling-footer">
                <span>Scaling Manager v0.1.0</span>
                <span>|</span>
                <span>Conductor System: Thread 3 Manual Scaling</span>
                <span>|</span>
                <span>Port Range: 8200-8299</span>
            </div>
        </div>
    );
};

export default ScalingManager;