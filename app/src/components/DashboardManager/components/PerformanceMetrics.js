// File: /home/parcoadmin/parco_fastapi/app/src/components/DashboardManager/components/PerformanceMetrics.js
/* Name: PerformanceMetrics.js */
/* Version: 0.1.0 */
/* Created: 250713 */
/* Modified: 250713 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Performance metrics and monitoring component */

import React, { useState, useEffect } from 'react';

const PerformanceMetrics = ({ stats, messageStats, onRefresh }) => {
  const [timeRange, setTimeRange] = useState('1h');
  const [metricHistory, setMetricHistory] = useState([]);

  useEffect(() => {
    // Simulate adding current metrics to history
    if (stats && messageStats) {
      const currentMetric = {
        timestamp: new Date(),
        messages_per_second: messageStats.messages_per_second || 0,
        processing_rate: messageStats.processing_rate || 0,
        memory_usage: Math.random() * 100, // Placeholder
        cpu_usage: Math.random() * 100,    // Placeholder
        queue_size: messageStats.queue_size || 0
      };

      setMetricHistory(prev => {
        const newHistory = [...prev, currentMetric];
        // Keep only last 100 points
        return newHistory.slice(-100);
      });
    }
  }, [stats, messageStats]);

  const getPerformanceGrade = (value, thresholds) => {
    if (value >= thresholds.excellent) return { grade: 'A', color: 'success' };
    if (value >= thresholds.good) return { grade: 'B', color: 'info' };
    if (value >= thresholds.fair) return { grade: 'C', color: 'warning' };
    return { grade: 'D', color: 'danger' };
  };

  const formatUptime = (startDate) => {
    if (!startDate) return 'Unknown';
    const now = new Date();
    const start = new Date(startDate);
    const uptimeMs = now - start;
    const hours = Math.floor(uptimeMs / (1000 * 60 * 60));
    const minutes = Math.floor((uptimeMs % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  const calculateAverage = (values) => {
    if (!values.length) return 0;
    return values.reduce((sum, val) => sum + val, 0) / values.length;
  };

  if (!stats) {
    return (
      <div className="performance-metrics-container">
        <div className="alert alert-warning">
          No performance data available
        </div>
      </div>
    );
  }

  const processingRate = messageStats?.processing_rate || 0;
  const messagesPerSecond = messageStats?.messages_per_second || 0;
  const queueSize = messageStats?.queue_size || 0;
  
  // Calculate performance grades
  const processingGrade = getPerformanceGrade(processingRate, {
    excellent: 95, good: 85, fair: 70
  });
  const throughputGrade = getPerformanceGrade(messagesPerSecond, {
    excellent: 100, good: 50, fair: 20
  });

  return (
    <div className="performance-metrics-container">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5>Performance Metrics</h5>
        <div className="metric-controls">
          <select
            className="form-control form-control-sm"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
          </select>
        </div>
      </div>

      {/* Performance Overview Cards */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="performance-card">
            <div className="card-icon bg-primary">
              <i className="fas fa-tachometer-alt"></i>
            </div>
            <div className="card-content">
              <h6>Processing Rate</h6>
              <div className="metric-value">
                {processingRate.toFixed(1)}%
                <span className={`grade grade-${processingGrade.color}`}>
                  {processingGrade.grade}
                </span>
              </div>
              <small className="text-muted">Message processing efficiency</small>
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="performance-card">
            <div className="card-icon bg-success">
              <i className="fas fa-stream"></i>
            </div>
            <div className="card-content">
              <h6>Throughput</h6>
              <div className="metric-value">
                {messagesPerSecond.toFixed(1)}/s
                <span className={`grade grade-${throughputGrade.color}`}>
                  {throughputGrade.grade}
                </span>
              </div>
              <small className="text-muted">Messages per second</small>
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="performance-card">
            <div className="card-icon bg-info">
              <i className="fas fa-clock"></i>
            </div>
            <div className="card-content">
              <h6>Uptime</h6>
              <div className="metric-value">
                {formatUptime(stats.manager_info?.start_date)}
              </div>
              <small className="text-muted">System availability</small>
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="performance-card">
            <div className="card-icon bg-warning">
              <i className="fas fa-layer-group"></i>
            </div>
            <div className="card-content">
              <h6>Queue Size</h6>
              <div className="metric-value">
                {queueSize}
                <span className={`status ${queueSize > 100 ? 'high' : queueSize > 50 ? 'medium' : 'low'}`}>
                  {queueSize > 100 ? 'HIGH' : queueSize > 50 ? 'MED' : 'LOW'}
                </span>
              </div>
              <small className="text-muted">Pending messages</small>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="row">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h6>System Resource Usage</h6>
            </div>
            <div className="card-body">
              <div className="resource-metrics">
                <div className="resource-item">
                  <div className="resource-label">
                    <span>Memory Usage</span>
                    <span className="resource-value">
                      {Math.random() * 100 > 50 ? '34%' : '67%'} {/* Placeholder */}
                    </span>
                  </div>
                  <div className="progress">
                    <div className="progress-bar bg-info" style={{width: '34%'}}></div>
                  </div>
                </div>

                <div className="resource-item">
                  <div className="resource-label">
                    <span>CPU Usage</span>
                    <span className="resource-value">
                      {Math.random() * 100 > 50 ? '12%' : '45%'} {/* Placeholder */}
                    </span>
                  </div>
                  <div className="progress">
                    <div className="progress-bar bg-success" style={{width: '12%'}}></div>
                  </div>
                </div>

                <div className="resource-item">
                  <div className="resource-label">
                    <span>Database Connections</span>
                    <span className="resource-value">
                      {stats.clients?.total_sdk_clients || 0} / 100
                    </span>
                  </div>
                  <div className="progress">
                    <div 
                      className="progress-bar bg-warning" 
                      style={{width: `${((stats.clients?.total_sdk_clients || 0) / 100) * 100}%`}}
                    ></div>
                  </div>
                </div>

                <div className="resource-item">
                  <div className="resource-label">
                    <span>WebSocket Connections</span>
                    <span className="resource-value">
                      {stats.clients?.total_websocket_clients || 0} / 1000
                    </span>
                  </div>
                  <div className="progress">
                    <div 
                      className="progress-bar bg-primary" 
                      style={{width: `${((stats.clients?.total_websocket_clients || 0) / 1000) * 100}%`}}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h6>Performance Statistics</h6>
            </div>
            <div className="card-body">
              <table className="table table-sm table-borderless">
                <tbody>
                  <tr>
                    <td><strong>Total Messages Processed:</strong></td>
                    <td>{stats.dashboard_manager?.messages_processed || 0}</td>
                  </tr>
                  <tr>
                    <td><strong>Total Messages Routed:</strong></td>
                    <td>{stats.dashboard_manager?.messages_routed || 0}</td>
                  </tr>
                  <tr>
                    <td><strong>Average Processing Time:</strong></td>
                    <td>{messageStats?.avg_processing_time?.toFixed(2) || 0}ms</td>
                  </tr>
                  <tr>
                    <td><strong>Peak Messages/Second:</strong></td>
                    <td>
                      {metricHistory.length > 0 
                        ? Math.max(...metricHistory.map(h => h.messages_per_second)).toFixed(1)
                        : 0
                      }
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Average Queue Size:</strong></td>
                    <td>
                      {metricHistory.length > 0 
                        ? calculateAverage(metricHistory.map(h => h.queue_size)).toFixed(0)
                        : 0
                      }
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Error Rate:</strong></td>
                    <td>
                      <span className="badge badge-success">
                        {((messageStats?.error_count || 0) / Math.max(messageStats?.total_processed || 1, 1) * 100).toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Active Customers:</strong></td>
                    <td>{stats.dashboard_manager?.customers_active || 0}</td>
                  </tr>
                  <tr>
                    <td><strong>Triggers Loaded:</strong></td>
                    <td>{stats.triggers?.total_triggers || 0}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Alerts */}
      <div className="row mt-3">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h6>Performance Alerts</h6>
            </div>
            <div className="card-body">
              <div className="alert-list">
                {queueSize > 100 && (
                  <div className="alert alert-warning">
                    <strong>High Queue Size:</strong> Message queue has {queueSize} pending items
                  </div>
                )}
                {processingRate < 70 && (
                  <div className="alert alert-danger">
                    <strong>Low Processing Rate:</strong> Processing efficiency is below 70%
                  </div>
                )}
                {messagesPerSecond < 1 && (
                  <div className="alert alert-info">
                    <strong>Low Throughput:</strong> Message throughput is below 1/second
                  </div>
                )}
                {stats.dashboard_manager?.customers_active === 0 && (
                  <div className="alert alert-warning">
                    <strong>No Active Customers:</strong> No customers are currently configured
                  </div>
                )}
                {processingRate >= 95 && queueSize < 10 && messagesPerSecond > 10 && (
                  <div className="alert alert-success">
                    <strong>Excellent Performance:</strong> All metrics are performing optimally
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetrics;