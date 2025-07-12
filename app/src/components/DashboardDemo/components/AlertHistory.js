/* Name: AlertHistory.js */
/* Version: 0.1.0 */
/* Created: 250711 */
/* Modified: 250711 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Alert history component for dashboard */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/DashboardDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

const AlertHistory = ({ alertSummary = {} }) => {
  // Default values if no data provided
  const {
    today_count = 0,
    month_count = 0,
    year_count = 0
  } = alertSummary;

  // Helper function to get percentage change (mock data for now)
  const getPercentageChange = (period) => {
    switch (period) {
      case 'today':
        return '(0%)';
      case 'month':
        return '(0%)';
      case 'year':
        return '(0%)';
      default:
        return '(0%)';
    }
  };

  // Helper function to get trend indicator
  const getTrendClass = (count) => {
    if (count === 0) return 'trend-neutral';
    if (count < 5) return 'trend-good';
    if (count < 20) return 'trend-warning';
    return 'trend-critical';
  };

  return (
    <div className="alert-history">
      <h3>Alert History</h3>
      
      <div className="alert-summary">
        <div className={`alert-period ${getTrendClass(today_count)}`}>
          <div className="alert-period-content">
            <div className="alert-period-label">Today</div>
            <div className="alert-period-count">{today_count}</div>
          </div>
          <div className="alert-period-change">
            {getPercentageChange('today')}
          </div>
        </div>

        <div className={`alert-period ${getTrendClass(month_count)}`}>
          <div className="alert-period-content">
            <div className="alert-period-label">This Month</div>
            <div className="alert-period-count">{month_count}</div>
          </div>
          <div className="alert-period-change">
            {getPercentageChange('month')}
          </div>
        </div>

        <div className={`alert-period ${getTrendClass(year_count)}`}>
          <div className="alert-period-content">
            <div className="alert-period-label">This Year</div>
            <div className="alert-period-count">{year_count}</div>
          </div>
          <div className="alert-period-change">
            {getPercentageChange('year')}
          </div>
        </div>
      </div>

      {/* Alert Management Links */}
      <div className="alert-actions">
        <a href="#alert-history" className="alert-link">
          View alert history
        </a>
        <span className="alert-separator">•</span>
        <a href="#alert-settings" className="alert-link">
          Edit alert settings
        </a>
      </div>

      {/* Current Alerts Status */}
      {(today_count > 0 || month_count > 0) && (
        <div className="current-alerts-status">
          <div className="status-indicator">
            <div className="status-dot active"></div>
            <span>Active alerts require attention</span>
          </div>
        </div>
      )}

      {today_count === 0 && month_count === 0 && year_count === 0 && (
        <div className="no-alerts-message">
          <div className="status-indicator">
            <div className="status-dot success"></div>
            <span>No active alerts</span>
          </div>
          <small>System is operating normally</small>
        </div>
      )}
    </div>
  );
};

export default AlertHistory;