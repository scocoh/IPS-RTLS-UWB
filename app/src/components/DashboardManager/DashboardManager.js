// File: /home/parcoadmin/parco_fastapi/app/src/components/DashboardManager/DashboardManager.js
/* Name: DashboardManager.js */
/* Version: 0.1.2 */
/* Created: 250713 */
/* Modified: 250713 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Dashboard Manager UI component for ParcoRTLS - Complete with Data Sources tab integration */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/DashboardManager */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from 'react';
import './styles/DashboardManager.css';
import ManagerStatus from './components/ManagerStatus';
import CustomerConfig from './components/CustomerConfig';
import MessageFlow from './components/MessageFlow';
import PerformanceMetrics from './components/PerformanceMetrics';
import ClientConnections from './components/ClientConnections';
import DataSourceManager from './components/DataSourceManager';
import useDashboardManagerData from './hooks/useDashboardManagerData';

const DashboardManager = () => {
  const [activeTab, setActiveTab] = useState('status');
  const {
    managerStatus,
    customerStats,
    messageStats,
    clientConnections,
    isLoading,
    error,
    refreshData,
    startManager,
    stopManager,
    restartManager
  } = useDashboardManagerData();

  useEffect(() => {
    // Refresh data every 30 seconds (reduced frequency)
    const interval = setInterval(refreshData, 30000);
    return () => clearInterval(interval);
  }, [refreshData]);

  if (isLoading) {
    return (
      <div className="dashboard-manager-container">
        <div className="loading-spinner">Loading Dashboard Manager...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-manager-container">
        <div className="error-message">
          Error: {error}
          <button onClick={refreshData} className="retry-button">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-manager-container">
      <div className="dashboard-manager-header">
        <h2>Dashboard Manager Control Panel</h2>
        <div className="manager-actions">
          <button 
            onClick={startManager} 
            className="btn btn-success"
            disabled={managerStatus?.manager_info?.run_state === 'Started'}
          >
            Start Manager
          </button>
          <button 
            onClick={stopManager} 
            className="btn btn-danger"
            disabled={managerStatus?.manager_info?.run_state === 'Stopped'}
          >
            Stop Manager
          </button>
          <button 
            onClick={restartManager} 
            className="btn btn-warning"
          >
            Restart Manager
          </button>
          <button onClick={refreshData} className="btn btn-info">
            Manual Refresh
          </button>
        </div>
      </div>

      <div className="dashboard-manager-tabs">
        <nav className="nav nav-tabs">
          <button 
            className={`nav-link ${activeTab === 'status' ? 'active' : ''}`}
            onClick={() => setActiveTab('status')}
          >
            Manager Status
          </button>
          <button 
            className={`nav-link ${activeTab === 'customers' ? 'active' : ''}`}
            onClick={() => setActiveTab('customers')}
          >
            Customer Config
          </button>
          <button 
            className={`nav-link ${activeTab === 'messages' ? 'active' : ''}`}
            onClick={() => setActiveTab('messages')}
          >
            Message Flow
          </button>
          <button 
            className={`nav-link ${activeTab === 'performance' ? 'active' : ''}`}
            onClick={() => setActiveTab('performance')}
          >
            Performance
          </button>
          <button 
            className={`nav-link ${activeTab === 'clients' ? 'active' : ''}`}
            onClick={() => setActiveTab('clients')}
          >
            Client Connections
          </button>
          <button 
            className={`nav-link ${activeTab === 'datasources' ? 'active' : ''}`}
            onClick={() => setActiveTab('datasources')}
          >
            Data Sources
          </button>
        </nav>
      </div>

      <div className="dashboard-manager-content">
        {activeTab === 'status' && (
          <ManagerStatus 
            status={managerStatus}
            onRefresh={refreshData}
          />
        )}
        {activeTab === 'customers' && (
          <CustomerConfig 
            customers={customerStats}
            onRefresh={refreshData}
          />
        )}
        {activeTab === 'messages' && (
          <MessageFlow 
            messageStats={messageStats}
            onRefresh={refreshData}
          />
        )}
        {activeTab === 'performance' && (
          <PerformanceMetrics 
            stats={managerStatus}
            messageStats={messageStats}
            onRefresh={refreshData}
          />
        )}
        {activeTab === 'clients' && (
          <ClientConnections 
            connections={clientConnections}
            onRefresh={refreshData}
          />
        )}
        {activeTab === 'datasources' && (
          <DataSourceManager 
            onRefresh={refreshData}
          />
        )}
      </div>

      <div className="dashboard-manager-footer">
        <div className="footer-content">
          <div className="footer-item">
            <span>Dashboard Manager v0.1.2</span>
          </div>
          <span className="footer-separator">•</span>
          <div className="footer-item">
            <span>Status:</span>
            <span className={`status-indicator ${managerStatus?.manager_info?.run_state?.toLowerCase() || 'unknown'}`}>
              {managerStatus?.manager_info?.run_state || 'Unknown'}
            </span>
          </div>
          <span className="footer-separator">•</span>
          <div className="footer-item">
            <span>Last Updated: {new Date().toLocaleTimeString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardManager;