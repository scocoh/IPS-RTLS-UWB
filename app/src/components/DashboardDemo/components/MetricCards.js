/* Name: MetricsCards.js */
/* Version: 0.1.0 */
/* Created: 250711 */
/* Modified: 250711 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Metrics cards component for dashboard */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/DashboardDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

const MetricsCards = ({ metrics }) => {
  const getMetricClass = (metricName) => {
    if (metricName.includes('online')) return 'metric-online';
    if (metricName.includes('offline') || metricName.includes('low_battery')) return 'metric-offline';
    if (metricName.includes('battery')) return 'metric-warning';
    return 'metric-info';
  };

  const formatMetricName = (name) => {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (!metrics || metrics.length === 0) {
    return (
      <div className="metrics-container">
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value">--</div>
            <div className="metric-label">Loading...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="metrics-container">
      <div className="metrics-grid">
        {metrics.map((metric) => (
          <div key={metric.metric_name} className={`metric-card ${getMetricClass(metric.metric_name)}`}>
            <div className="metric-value">{metric.metric_value}</div>
            <div className="metric-label">{formatMetricName(metric.metric_name)}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MetricsCards;