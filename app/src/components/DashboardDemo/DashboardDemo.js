/* Name: DashboardDemo.js */
/* Version: 0.1.1 */
/* Created: 250711 */
/* Modified: 250712 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Main dashboard component for ParcoRTLS with dynamic device categories */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from 'react';
import './styles/DashboardDemo.css';

// Import dashboard components
import MetricsCards from './components/MetricCards';
import LocationSections from './components/LocationSections';
import ActivityFeed from './components/ActivityFeed';
import AutoclaveChart from './components/AutoclaveChart';
import AlertHistory from './components/AlertHistory';
import SensorReadings from './components/SensorReadings';

// Import hooks
import useDashboardData from './hooks/useDashboardData';

// Import services
import { dashboardApi } from './services/dashboardApi';

const DashboardDemo = () => {
  const [activeTab, setActiveTab] = useState('ACTIVITY');
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds
  const [isAutoRefresh, setIsAutoRefresh] = useState(true);
  const [customerId] = useState(1); // Default to Sample Customer
  
  // Custom hook for dashboard data
  const {
    dashboardData,
    isLoading,
    error,
    refreshData
  } = useDashboardData(refreshInterval, isAutoRefresh, customerId);

  const handleTabChange = (tabName) => {
    setActiveTab(tabName);
  };

  const handleRefresh = () => {
    refreshData();
  };

  const handleAutoRefreshToggle = () => {
    setIsAutoRefresh(!isAutoRefresh);
  };

  if (isLoading && !dashboardData) {
    return (
      <div className="dashboard-demo">
        <div className="dashboard-loading">
          <div className="loading-spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-demo">
        <div className="dashboard-error">
          <h2>Dashboard Error</h2>
          <p>{error}</p>
          <button onClick={handleRefresh} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-demo">
      {/* Dashboard Header */}
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>{dashboardData?.customer_config?.dashboard_title || 'ParcoRTLS Dashboard'}</h1>
          <span className="dashboard-subtitle">
            {dashboardData?.customer_config?.customer_name || 'Real-Time Location System Monitor'}
          </span>
        </div>
        <div className="dashboard-controls">
          <button 
            onClick={handleRefresh} 
            className="refresh-button"
            disabled={isLoading}
          >
            {isLoading ? '↻' : '⟳'} Refresh
          </button>
          <label className="auto-refresh-toggle">
            <input
              type="checkbox"
              checked={isAutoRefresh}
              onChange={handleAutoRefreshToggle}
            />
            Auto-refresh
          </label>
          <span className="last-updated">
            Last updated: {dashboardData?.last_updated ? 
              new Date(dashboardData.last_updated).toLocaleTimeString() : 
              'Never'
            }
          </span>
        </div>
      </div>

      {/* Top Metrics Row */}
      <MetricsCards metrics={dashboardData?.metrics || []} />

      {/* Main Dashboard Content */}
      <div className="dashboard-content">
        {/* Tab Navigation */}
        <div className="dashboard-tabs">
          <button 
            className={`tab-button ${activeTab === 'ACTIVITY' ? 'active' : ''}`}
            onClick={() => handleTabChange('ACTIVITY')}
          >
            ACTIVITY
          </button>
          <button 
            className={`tab-button ${activeTab === 'LOCATION' ? 'active' : ''}`}
            onClick={() => handleTabChange('LOCATION')}
          >
            LOCATION
          </button>
          <button 
            className={`tab-button ${activeTab === 'AUTOCLAVE' ? 'active' : ''}`}
            onClick={() => handleTabChange('AUTOCLAVE')}
          >
            AUTOCLAVE
          </button>
          <button 
            className={`tab-button ${activeTab === 'SENSORS' ? 'active' : ''}`}
            onClick={() => handleTabChange('SENSORS')}
          >
            SENSORS
          </button>
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === 'ACTIVITY' && (
            <div className="activity-tab">
              <div className="activity-left">
                <ActivityFeed 
                  activity={dashboardData?.recent_activity || []} 
                  isLoading={isLoading}
                />
              </div>
              <div className="activity-right">
                <AlertHistory 
                  alertSummary={dashboardData?.alert_summary || {}} 
                />
              </div>
            </div>
          )}

          {activeTab === 'LOCATION' && (
            <LocationSections 
              locations={dashboardData?.locations || []}
              metrics={dashboardData?.metrics || []}
              deviceCategories={dashboardData?.device_categories || []}
              customerId={customerId}
            />
          )}

          {activeTab === 'AUTOCLAVE' && (
            <AutoclaveChart 
              autoclaveData={dashboardData?.autoclave_data || []}
              isLoading={isLoading}
            />
          )}

          {activeTab === 'SENSORS' && (
            <SensorReadings 
              sensors={dashboardData?.sensor_readings || []}
              isLoading={isLoading}
            />
          )}
        </div>
      </div>

      {/* Dashboard Footer */}
      <div className="dashboard-footer">
        <span>ParcoRTLS Dashboard v0.1.1</span>
        <span>•</span>
        <span>{dashboardData?.metrics?.length || 0} metrics tracked</span>
        <span>•</span>
        <span>{dashboardData?.locations?.length || 0} locations monitored</span>
      </div>
    </div>
  );
};

export default DashboardDemo;