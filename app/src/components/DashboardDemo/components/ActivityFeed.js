/* Name: ActivityFeed.js */
/* Version: 0.1.1 */
/* Created: 250711 */
/* Modified: 250714 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Activity feed component for dashboard with external data source integration */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/DashboardDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from 'react';

const ActivityFeed = ({ activity = [], externalData = [], isLoading = false }) => {
  const [activities, setActivities] = useState([]);

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
  const getActivityIconClass = (severity, source) => {
    const baseClass = 'activity-icon';
    const sourceClass = source ? `source-${source.toLowerCase().replace(/[^a-z0-9]/g, '')}` : '';
    
    switch (severity?.toLowerCase()) {
      case 'critical':
        return `${baseClass} critical ${sourceClass}`;
      case 'error':
        return `${baseClass} error ${sourceClass}`;
      case 'warning':
        return `${baseClass} warning ${sourceClass}`;
      case 'info':
      default:
        return `${baseClass} info ${sourceClass}`;
    }
  };

  // Process external data source position updates into activity events
  useEffect(() => {
    if (externalData && externalData.length > 0) {
      const externalActivities = externalData.map(tag => ({
        id: `external-${tag.tag_id}-${Date.now()}-${Math.random()}`,
        type: 'position_update',
        device_id: tag.tag_id,
        description: `External device ${tag.tag_id} position update`,
        event_timestamp: tag.timestamp || new Date().toISOString(),
        severity: 'info',
        location_name: tag.zone_id ? `Zone ${tag.zone_id}` : 'Unknown Location',
        source: tag.source || 'External',
        position: {
          x: tag.x,
          y: tag.y,
          z: tag.z
        },
        metadata: {
          battery: tag.battery,
          confidence: tag.confidence,
          gateway_id: tag.gateway_id
        }
      }));

      // Merge external activities with existing activities
      setActivities(prev => {
        const combined = [...externalActivities, ...prev, ...activity];
        // Sort by timestamp (most recent first) and limit to 50 items
        return combined
          .sort((a, b) => new Date(b.event_timestamp) - new Date(a.event_timestamp))
          .slice(0, 50);
      });
    } else {
      // No external data, just use regular activity
      setActivities(prev => {
        const combined = [...activity];
        return combined
          .sort((a, b) => new Date(b.event_timestamp) - new Date(a.event_timestamp))
          .slice(0, 50);
      });
    }
  }, [externalData, activity]);

  // Sample activity data if none provided
  const sampleActivity = [
    {
      id: 1,
      description: 'No activity found for the selected date range.',
      event_timestamp: new Date().toISOString(),
      severity: 'info',
      device_id: null,
      location_name: null,
      source: 'System'
    }
  ];

  const displayActivity = activities.length > 0 ? activities : sampleActivity;

  return (
    <div className="activity-feed">
      <h3>Activity Feed</h3>
      
      {isLoading && activities.length === 0 ? (
        <div className="activity-loading">
          <div className="loading-spinner"></div>
          <p>Loading activity...</p>
        </div>
      ) : (
        <div className="activity-list">
          {displayActivity.map((item, index) => (
            <div key={item.id || index} className={`activity-item ${item.source?.toLowerCase() || ''}`}>
              <div className={getActivityIconClass(item.severity, item.source)}></div>
              
              <div className="activity-content">
                <div className="activity-description">
                  {item.description}
                  {item.device_id && (
                    <span className="activity-device"> ({item.device_id})</span>
                  )}
                  {item.position && (
                    <span className="activity-position">
                      {' '}at ({item.position.x?.toFixed(1)}, {item.position.y?.toFixed(1)})
                    </span>
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
                  {item.source && (
                    <>
                      {' • '}
                      <span className="activity-source">{item.source}</span>
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
                
                {/* Additional metadata for external devices */}
                {item.metadata && (
                  <div className="activity-metadata">
                    {item.metadata.battery && (
                      <span className="metadata-item">
                        Battery: {item.metadata.battery}%
                      </span>
                    )}
                    {item.metadata.confidence && (
                      <span className="metadata-item">
                        Confidence: {item.metadata.confidence}%
                      </span>
                    )}
                    {item.metadata.gateway_id && (
                      <span className="metadata-item">
                        Gateway: {item.metadata.gateway_id}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      
      {!isLoading && activities.length === 0 && (
        <div className="activity-empty">
          <p>No recent activity to display.</p>
          <small>Activity will appear here as events occur in the system.</small>
        </div>
      )}
      
      {activities.length > 0 && (
        <div className="activity-footer">
          <div className="activity-stats">
            {externalData.length > 0 && (
              <span className="external-activity-count">
                {externalData.length} external device{externalData.length !== 1 ? 's' : ''} active
              </span>
            )}
          </div>
          <a href="#view-all" className="view-all-link">
            View all activity →
          </a>
        </div>
      )}
    </div>
  );
};

export default ActivityFeed;