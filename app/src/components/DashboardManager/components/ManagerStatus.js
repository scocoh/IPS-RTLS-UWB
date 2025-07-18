// File: /home/parcoadmin/parco_fastapi/app/src/components/DashboardManager/components/ManagerStatus.js
/* Name: ManagerStatus.js */
/* Version: 0.1.0 */
/* Created: 250713 */
/* Modified: 250713 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Dashboard Manager status display component */

import React from 'react';

const ManagerStatus = ({ status, onRefresh }) => {
  if (!status) {
    return (
      <div className="manager-status-container">
        <div className="alert alert-warning">
          No manager status data available
        </div>
      </div>
    );
  }

  const getStatusColor = (state) => {
    switch (state) {
      case 'Started': return 'success';
      case 'Starting': return 'warning';
      case 'Stopped': return 'danger';
      case 'Stopping': return 'warning';
      default: return 'secondary';
    }
  };

  const getHealthColor = (isHealthy) => {
    return isHealthy ? 'success' : 'danger';
  };

  return (
    <div className="manager-status-container">
      <div className="row">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5>Manager Information</h5>
            </div>
            <div className="card-body">
              <table className="table table-borderless">
                <tbody>
                  <tr>
                    <td><strong>Name:</strong></td>
                    <td>{status.manager_info?.name || 'Unknown'}</td>
                  </tr>
                  <tr>
                    <td><strong>Zone ID:</strong></td>
                    <td>{status.manager_info?.zone_id || 'Unknown'}</td>
                  </tr>
                  <tr>
                    <td><strong>Run State:</strong></td>
                    <td>
                      <span className={`badge badge-${getStatusColor(status.manager_info?.run_state)}`}>
                        {status.manager_info?.run_state || 'Unknown'}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Averaging:</strong></td>
                    <td>{status.manager_info?.is_averaging ? 'Enabled' : 'Disabled'}</td>
                  </tr>
                  <tr>
                    <td><strong>Mode:</strong></td>
                    <td>{status.manager_info?.mode || 'Unknown'}</td>
                  </tr>
                  <tr>
                    <td><strong>SDK IP:</strong></td>
                    <td>{status.manager_info?.sdk_ip || 'Unknown'}</td>
                  </tr>
                  <tr>
                    <td><strong>SDK Port:</strong></td>
                    <td>{status.manager_info?.sdk_port || 'Unknown'}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5>System Health</h5>
            </div>
            <div className="card-body">
              <div className="health-indicators">
                <div className="health-item">
                  <span className="health-label">Overall Health:</span>
                  <span className={`badge badge-${getHealthColor(status.healthy)}`}>
                    {status.healthy ? 'Healthy' : 'Unhealthy'}
                  </span>
                </div>
                <div className="health-item">
                  <span className="health-label">Database:</span>
                  <span className={`badge badge-${getHealthColor(status.database?.ready)}`}>
                    {status.database?.ready ? 'Ready' : 'Not Ready'}
                  </span>
                </div>
                <div className="health-item">
                  <span className="health-label">Heartbeat:</span>
                  <span className={`badge badge-${getHealthColor(status.heartbeat?.running)}`}>
                    {status.heartbeat?.running ? 'Running' : 'Stopped'}
                  </span>
                </div>
                <div className="health-item">
                  <span className="health-label">Data Processing:</span>
                  <span className={`badge badge-${getHealthColor(status.data?.processing)}`}>
                    {status.data?.processing ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div className="health-item">
                  <span className="health-label">Triggers:</span>
                  <span className="badge badge-info">
                    {status.triggers?.total_triggers || 0} Loaded
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="card mt-3">
            <div className="card-header">
              <h5>Dashboard Specific</h5>
            </div>
            <div className="card-body">
              <table className="table table-borderless">
                <tbody>
                  <tr>
                    <td><strong>Customers Configured:</strong></td>
                    <td>{status.dashboard_manager?.customers_configured || 0}</td>
                  </tr>
                  <tr>
                    <td><strong>Customers Active:</strong></td>
                    <td>{status.dashboard_manager?.customers_active || 0}</td>
                  </tr>
                  <tr>
                    <td><strong>Messages Processed:</strong></td>
                    <td>{status.dashboard_manager?.messages_processed || 0}</td>
                  </tr>
                  <tr>
                    <td><strong>Messages Routed:</strong></td>
                    <td>{status.dashboard_manager?.messages_routed || 0}</td>
                  </tr>
                  <tr>
                    <td><strong>Queue Size:</strong></td>
                    <td>{status.dashboard_manager?.queue_size || 0}</td>
                  </tr>
                  <tr>
                    <td><strong>Routing Rate:</strong></td>
                    <td>{status.dashboard_manager?.routing_rate?.toFixed(1) || 0}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div className="row mt-3">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5>Start Time Information</h5>
            </div>
            <div className="card-body">
              <p>
                <strong>Started:</strong> {
                  status.manager_info?.start_date 
                    ? new Date(status.manager_info.start_date).toLocaleString()
                    : 'Not started'
                }
              </p>
              <p>
                <strong>Uptime:</strong> {
                  status.manager_info?.start_date 
                    ? Math.floor((new Date() - new Date(status.manager_info.start_date)) / 1000 / 60) + ' minutes'
                    : 'N/A'
                }
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManagerStatus;