// File: /home/parcoadmin/parco_fastapi/app/src/components/DashboardManager/components/DataSourceManager.js
/* Name: DataSourceManager.js */
/* Version: 0.1.0 */
/* Created: 250713 */
/* Modified: 250713 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Data source discovery and management component for Dashboard Manager */

import React, { useState, useEffect } from 'react';
import useDataSources from '../hooks/useDataSources';

const DataSourceManager = ({ onRefresh }) => {
  const {
    dataSources,
    isLoading,
    error,
    refreshSources,
    getSourceStatus,
    checkHealth,
    startSource,
    stopSource,
    restartSource
  } = useDataSources();

  const [sourceStatuses, setSourceStatuses] = useState({});
  const [actionLoading, setActionLoading] = useState({});

  useEffect(() => {
    // Initial load of data sources
    refreshSources();
  }, [refreshSources]);

  useEffect(() => {
    // Load status for all discovered sources
    const loadStatuses = async () => {
      if (dataSources.length > 0) {
        const statuses = {};
        for (const source of dataSources) {
          try {
            const status = await getSourceStatus(source.id);
            statuses[source.id] = status;
          } catch (err) {
            console.error(`Failed to get status for ${source.id}:`, err);
            statuses[source.id] = { status: 'error', error_message: err.message };
          }
        }
        setSourceStatuses(statuses);
      }
    };

    loadStatuses();
  }, [dataSources, getSourceStatus]);

  const handleServiceAction = async (sourceId, action) => {
    try {
      setActionLoading(prev => ({ ...prev, [sourceId]: action }));
      
      let result;
      switch (action) {
        case 'start':
          result = await startSource(sourceId);
          break;
        case 'stop':
          result = await stopSource(sourceId);
          break;
        case 'restart':
          result = await restartSource(sourceId);
          break;
        default:
          throw new Error(`Unknown action: ${action}`);
      }

      // Refresh status after action
      setTimeout(async () => {
        try {
          const status = await getSourceStatus(sourceId);
          setSourceStatuses(prev => ({ ...prev, [sourceId]: status }));
        } catch (err) {
          console.error(`Failed to refresh status for ${sourceId}:`, err);
        }
      }, 2000);

      return result;
    } catch (err) {
      console.error(`Service action ${action} failed for ${sourceId}:`, err);
      throw err;
    } finally {
      setActionLoading(prev => ({ ...prev, [sourceId]: null }));
    }
  };

  const handleHealthCheck = async (sourceId) => {
    try {
      setActionLoading(prev => ({ ...prev, [sourceId]: 'health' }));
      const healthResult = await checkHealth(sourceId);
      
      // Show health result in a simple alert for now
      const healthStatus = healthResult.healthy ? 'Healthy' : 'Unhealthy';
      const checks = Object.entries(healthResult.checks || {})
        .map(([check, status]) => `${check}: ${status ? '✓' : '✗'}`)
        .join('\n');
      
      alert(`Health Check for ${sourceId}\n\nStatus: ${healthStatus}\n\n${checks}`);
      
    } catch (err) {
      console.error(`Health check failed for ${sourceId}:`, err);
      alert(`Health check failed for ${sourceId}: ${err.message}`);
    } finally {
      setActionLoading(prev => ({ ...prev, [sourceId]: null }));
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return 'success';
      case 'offline': return 'danger';
      case 'timeout': return 'warning';
      case 'error': return 'danger';
      default: return 'secondary';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'online': return '●';
      case 'offline': return '●';
      case 'timeout': return '●';
      case 'error': return '●';
      default: return '●';
    }
  };

  const isActionDisabled = (sourceId, action) => {
    const loading = actionLoading[sourceId];
    const status = sourceStatuses[sourceId]?.status;
    
    if (loading) return true;
    
    switch (action) {
      case 'start':
        return status === 'online';
      case 'stop':
        return status === 'offline' || status === 'error';
      case 'restart':
      case 'health':
        return false;
      default:
        return false;
    }
  };

  if (isLoading) {
    return (
      <div className="data-source-manager-container">
        <div className="loading-spinner">Loading data sources...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="data-source-manager-container">
        <div className="error-message">
          Error: {error}
          <button onClick={refreshSources} className="retry-button">Retry</button>
        </div>
      </div>
    );
  }

  if (dataSources.length === 0) {
    return (
      <div className="data-source-manager-container">
        <div className="alert alert-info">
          <h5>No data sources discovered</h5>
          <p>No data sources were found in the database or directory structure.</p>
          <button onClick={refreshSources} className="btn btn-primary">
            Refresh Discovery
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="data-source-manager-container">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5>Data Source Discovery & Management</h5>
        <button onClick={refreshSources} className="btn btn-info btn-sm">
          Refresh Discovery
        </button>
      </div>

      {/* Data Source Statistics */}
      <div className="row mb-3">
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-value">{dataSources.length}</div>
            <div className="stat-label">Total Sources</div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-value">
              {Object.values(sourceStatuses).filter(s => s.status === 'online').length}
            </div>
            <div className="stat-label">Online</div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-value">
              {dataSources.filter(s => s.directory_exists && s.config_found).length}
            </div>
            <div className="stat-label">Configured</div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-value">
              {dataSources.filter(s => s.service_file).length}
            </div>
            <div className="stat-label">Service Ready</div>
          </div>
        </div>
      </div>

      {/* Data Source Cards */}
      <div className="row">
        {dataSources.map((source) => {
          const status = sourceStatuses[source.id];
          const loading = actionLoading[source.id];
          
          return (
            <div key={source.id} className="col-md-6 col-lg-4 mb-3">
              <div className="card data-source-card">
                <div className="card-header d-flex justify-content-between align-items-center">
                  <h6 className="mb-0">
                    🔗 {source.name}
                  </h6>
                  {status && (
                    <span className={`badge badge-${getStatusColor(status.status)}`}>
                      {getStatusIcon(status.status)} {status.status.toUpperCase()}
                    </span>
                  )}
                </div>
                <div className="card-body">
                  <table className="table table-sm table-borderless">
                    <tbody>
                      <tr>
                        <td><strong>Type:</strong></td>
                        <td>{source.type}</td>
                      </tr>
                      <tr>
                        <td><strong>Host:</strong></td>
                        <td>{source.host}</td>
                      </tr>
                      <tr>
                        <td><strong>Port:</strong></td>
                        <td>{source.port}</td>
                      </tr>
                      {status && status.response_time && (
                        <tr>
                          <td><strong>Response:</strong></td>
                          <td>{status.response_time}ms</td>
                        </tr>
                      )}
                    </tbody>
                  </table>

                  {/* Configuration Status */}
                  <div className="config-status mb-2">
                    <small className="text-muted">Configuration Status:</small>
                    <div className="config-indicators">
                      <span className={`badge badge-${source.directory_exists ? 'success' : 'danger'} mr-1`}>
                        {source.directory_exists ? '✅' : '❌'} Directory
                      </span>
                      <span className={`badge badge-${source.config_found ? 'success' : 'danger'} mr-1`}>
                        {source.config_found ? '✅' : '❌'} Config
                      </span>
                      <span className={`badge badge-${source.service_file ? 'success' : 'danger'} mr-1`}>
                        {source.service_file ? '✅' : '❌'} Service
                      </span>
                    </div>
                  </div>

                  {/* Service Actions */}
                  <div className="data-source-actions">
                    <button
                      className="btn btn-success btn-sm mr-1"
                      onClick={() => handleServiceAction(source.id, 'start')}
                      disabled={isActionDisabled(source.id, 'start')}
                    >
                      {loading === 'start' ? 'Starting...' : 'Start'}
                    </button>
                    <button
                      className="btn btn-danger btn-sm mr-1"
                      onClick={() => handleServiceAction(source.id, 'stop')}
                      disabled={isActionDisabled(source.id, 'stop')}
                    >
                      {loading === 'stop' ? 'Stopping...' : 'Stop'}
                    </button>
                    <button
                      className="btn btn-warning btn-sm mr-1"
                      onClick={() => handleServiceAction(source.id, 'restart')}
                      disabled={isActionDisabled(source.id, 'restart')}
                    >
                      {loading === 'restart' ? 'Restarting...' : 'Restart'}
                    </button>
                    <button
                      className="btn btn-info btn-sm"
                      onClick={() => handleHealthCheck(source.id)}
                      disabled={isActionDisabled(source.id, 'health')}
                    >
                      {loading === 'health' ? 'Checking...' : 'Health'}
                    </button>
                  </div>

                  {/* Error Message */}
                  {status && status.error_message && (
                    <div className="alert alert-warning mt-2 mb-0">
                      <small>{status.error_message}</small>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default DataSourceManager;