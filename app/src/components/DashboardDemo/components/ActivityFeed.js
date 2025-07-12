/* Name: ActivityFeed.js */
/* Version: 0.1.0 */
/* Created: 250711 */
/* Modified: 250711 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Activity feed component for dashboard */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/DashboardDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

const ActivityFeed = ({ activity = [], isLoading = false }) => {
  // Helper function to format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown time';
    
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMins / 60);
      const diffDays = Math.floor(diffHours / 24);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays < 7) return `${diffDays}d ago`;
      
      return date.toLocaleDateString();
    } catch (error) {
      return 'Invalid date';
    }
  };

  // Helper function to get activity icon class
  const getActivityIconClass = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'activity-icon critical';
      case 'error':
        return 'activity-icon error';
      case 'warning':
        return 'activity-icon warning';
      case 'info':
      default:
        return 'activity-icon info';
    }
  };

  // Sample activity data if none provided
  const sampleActivity = [
    {
      id: 1,
      description: 'No activity found for the selected date range.',
      event_timestamp: new Date().toISOString(),
      severity: 'info',
      device_id: null,
      location_name: null
    }
  ];

  const displayActivity = activity.length > 0 ? activity : sampleActivity;

  return (
    <div className="activity-feed">
      <h3>Activity Feed</h3>
      
      {isLoading && activity.length === 0 ? (
        <div className="activity-loading">
          <div className="loading-spinner"></div>
          <p>Loading activity...</p>
        </div>
      ) : (
        <div className="activity-list">
          {displayActivity.map((item, index) => (
            <div key={item.id || index} className="activity-item">
              <div className={getActivityIconClass(item.severity)}></div>
              
              <div className="activity-content">
                <div className="activity-description">
                  {item.description}
                  {item.device_id && (
                    <span className="activity-device"> ({item.device_id})</span>
                  )}
                </div>
                
                <div className="activity-meta">
                  {formatTimestamp(item.event_timestamp)}
                  {item.location_name && (
                    <>
                      {' • '}
                      <span className="activity-location">{item.location_name}</span>
                    </>
                  )}
                  {item.severity && item.severity !== 'info' && (
                    <>
                      {' • '}
                      <span className={`activity-severity severity-${item.severity}`}>
                        {item.severity.toUpperCase()}
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {!isLoading && activity.length === 0 && (
        <div className="activity-empty">
          <p>No recent activity to display.</p>
          <small>Activity will appear here as events occur in the system.</small>
        </div>
      )}
      
      {activity.length > 0 && (
        <div className="activity-footer">
          <a href="#view-all" className="view-all-link">
            View all activity →
          </a>
        </div>
      )}
    </div>
  );
};

export default ActivityFeed;