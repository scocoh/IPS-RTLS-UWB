// File: /home/parcoadmin/parco_fastapi/app/src/components/DashboardManager/components/MessageFlow.js
/* Name: MessageFlow.js */
/* Version: 0.1.0 */
/* Created: 250713 */
/* Modified: 250713 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Message flow monitoring and statistics component */

import React, { useState, useEffect } from 'react';

const MessageFlow = ({ messageStats, onRefresh }) => {
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5);

  useEffect(() => {
    let interval;
    if (autoRefresh) {
      interval = setInterval(() => {
        onRefresh();
      }, refreshInterval * 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, refreshInterval, onRefresh]);

  if (!messageStats) {
    return (
      <div className="message-flow-container">
        <div className="alert alert-warning">
          No message flow data available
        </div>
      </div>
    );
  }

  const getFlowColor = (rate) => {
    if (rate > 80) return 'success';
    if (rate > 60) return 'warning';
    return 'danger';
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  return (
    <div className="message-flow-container">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5>Message Flow Monitoring</h5>
        <div className="flow-controls">
          <div className="form-check form-check-inline">
            <input
              className="form-check-input"
              type="checkbox"
              id="autoRefresh"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            <label className="form-check-label" htmlFor="autoRefresh">
              Auto Refresh
            </label>
          </div>
          <select
            className="form-control form-control-sm ml-2"
            style={{ width: 'auto', display: 'inline-block' }}
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
            disabled={!autoRefresh}
          >
            <option value={1}>1s</option>
            <option value={5}>5s</option>
            <option value={10}>10s</option>
            <option value={30}>30s</option>
          </select>
        </div>
      </div>

      <div className="row">
        {/* Message Processing Overview */}
        <div className="col-md-8">
          <div className="card">
            <div className="card-header">
              <h6>Message Processing Pipeline</h6>
            </div>
            <div className="card-body">
              <div className="pipeline-flow">
                <div className="flow-stage">
                  <div className="stage-box">
                    <h6>Input</h6>
                    <div className="stage-metric">
                      {formatNumber(messageStats.total_received || 0)}
                    </div>
                    <small>Messages Received</small>
                  </div>
                  <div className="flow-arrow">→</div>
                </div>

                <div className="flow-stage">
                  <div className="stage-box">
                    <h6>Processing</h6>
                    <div className="stage-metric">
                      {formatNumber(messageStats.total_processed || 0)}
                    </div>
                    <small>Messages Processed</small>
                  </div>
                  <div className="flow-arrow">→</div>
                </div>

                <div className="flow-stage">
                  <div className="stage-box">
                    <h6>Routing</h6>
                    <div className="stage-metric">
                      {formatNumber(messageStats.total_routed || 0)}
                    </div>
                    <small>Messages Routed</small>
                  </div>
                  <div className="flow-arrow">→</div>
                </div>

                <div className="flow-stage">
                  <div className="stage-box">
                    <h6>Dashboard</h6>
                    <div className="stage-metric">
                      {formatNumber(messageStats.dashboard_sent || 0)}
                    </div>
                    <small>Sent to Dashboard</small>
                  </div>
                </div>
              </div>

              <div className="pipeline-stats mt-3">
                <div className="row">
                  <div className="col-md-3">
                    <div className="stat-item">
                      <span className="stat-label">Processing Rate:</span>
                      <span className={`badge badge-${getFlowColor(messageStats.processing_rate || 0)}`}>
                        {(messageStats.processing_rate || 0).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="stat-item">
                      <span className="stat-label">Routing Rate:</span>
                      <span className={`badge badge-${getFlowColor(messageStats.routing_rate || 0)}`}>
                        {(messageStats.routing_rate || 0).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="stat-item">
                      <span className="stat-label">Queue Size:</span>
                      <span className="badge badge-info">
                        {messageStats.queue_size || 0}
                      </span>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="stat-item">
                      <span className="stat-label">Errors:</span>
                      <span className="badge badge-danger">
                        {messageStats.error_count || 0}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Real-time Metrics */}
        <div className="col-md-4">
          <div className="card">
            <div className="card-header">
              <h6>Real-time Metrics</h6>
            </div>
            <div className="card-body">
              <div className="metric-item">
                <span className="metric-label">Messages/Second:</span>
                <span className="metric-value">
                  {(messageStats.messages_per_second || 0).toFixed(2)}
                </span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Avg Processing Time:</span>
                <span className="metric-value">
                  {(messageStats.avg_processing_time || 0).toFixed(2)}ms
                </span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Active Customers:</span>
                <span className="metric-value">
                  {messageStats.active_customers || 0}
                </span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Connected Clients:</span>
                <span className="metric-value">
                  {messageStats.connected_clients || 0}
                </span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Last Message:</span>
                <span className="metric-value">
                  {messageStats.last_message_time 
                    ? new Date(messageStats.last_message_time).toLocaleTimeString()
                    : 'Never'
                  }
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Message Categories Breakdown */}
      <div className="row mt-3">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h6>Message Categories Breakdown</h6>
            </div>
            <div className="card-body">
              {messageStats.category_breakdown ? (
                <div className="category-grid">
                  {Object.entries(messageStats.category_breakdown).map(([category, count]) => (
                    <div key={category} className="category-item">
                      <div className="category-name">{category}</div>
                      <div className="category-count">{formatNumber(count)}</div>
                      <div className="category-bar">
                        <div 
                          className="category-bar-fill"
                          style={{
                            width: `${(count / Math.max(...Object.values(messageStats.category_breakdown))) * 100}%`
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-muted">No category data available</div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Errors */}
      {messageStats.recent_errors && messageStats.recent_errors.length > 0 && (
        <div className="row mt-3">
          <div className="col-12">
            <div className="card">
              <div className="card-header bg-danger text-white">
                <h6 className="mb-0">Recent Errors</h6>
              </div>
              <div className="card-body">
                <div className="error-list">
                  {messageStats.recent_errors.slice(0, 5).map((error, index) => (
                    <div key={index} className="error-item">
                      <div className="error-time">
                        {new Date(error.timestamp).toLocaleString()}
                      </div>
                      <div className="error-message">{error.message}</div>
                      {error.details && (
                        <div className="error-details">
                          <small className="text-muted">{error.details}</small>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MessageFlow;