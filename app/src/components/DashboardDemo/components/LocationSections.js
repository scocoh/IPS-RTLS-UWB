/* Name: LocationSections.js */
/* Version: 0.1.3 */
/* Created: 250711 */
/* Modified: 250714 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Location sections component for dashboard with dynamic device categories and external data source integration */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/DashboardDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

const LocationSections = ({ 
  locations, 
  metrics, 
  deviceCategories, 
  externalPositions = [], 
  customerId = 1 
}) => {
  const getMetricValue = (metricName) => {
    const metric = metrics?.find(m => m.metric_name === metricName);
    return metric ? metric.metric_value : 0;
  };

  // Helper function to determine location from zone_id
  const getLocationFromZone = (zoneId) => {
    // This could be enhanced with actual zone-to-location mapping
    if (zoneId === 417) return 'Sample Customer';
    return 'Unknown Location';
  };

  // Use dynamic device categories from database
  const getLocationMetrics = () => {
    if (!deviceCategories || deviceCategories.length === 0) {
      return []; // Return empty array if no categories configured
    }

    // Use dynamic device categories from API
    return deviceCategories.map(category => ({
      key: category.category_key,
      label: category.category_label,
      value: category.metric_value || 0,
      icon: category.icon_name || 'device',
      metricName: category.metric_name
    }));
  };

  // Process external data source positions by zone/location
  const externalByLocation = externalPositions.reduce((acc, tag) => {
    const location = getLocationFromZone(tag.zone_id) || 'Unknown Location';
    if (!acc[location]) acc[location] = [];
    acc[location].push(tag);
    return acc;
  }, {});

  if (!locations || locations.length === 0) {
    return (
      <div className="location-sections">
        <div className="location-section">
          <div className="location-header">
            <h3 className="location-title">Loading locations...</h3>
          </div>
        </div>
      </div>
    );
  }

  const locationMetrics = getLocationMetrics();

  return (
    <div className="location-sections">
      {/* Existing ParcoRTLS Location Sections */}
      {locations.map((location) => (
        <div key={location.id} className="location-section">
          <div className="location-header">
            <h3 className="location-title">{location.location_name}</h3>
          </div>
          <div className="location-metrics">
            {locationMetrics.map((metric) => (
              <div key={metric.key} className="location-metric">
                <div className="location-metric-value">{metric.value}</div>
                <div className="location-metric-label">{metric.label}</div>
                {/* Optional: Add icon display if needed */}
                {metric.icon && (
                  <div className="location-metric-icon" data-icon={metric.icon}></div>
                )}
              </div>
            ))}
          </div>
          <div className="location-tags">
            <span className="tag-info">{getMetricValue('online_tags')} tags in selected area</span>
            {location.location_name === 'Sample Customer' && (
              <a href="#" className="view-tags-link">View all tags</a>
            )}
          </div>
        </div>
      ))}

      {/* External Data Source Section */}
      {Object.keys(externalByLocation).length > 0 && (
        <div className="location-section external-data-section">
          <div className="location-header">
            <h3 className="location-title">External RTLS Devices</h3>
            <span className="external-data-badge">Live Data</span>
          </div>
          
          {Object.entries(externalByLocation).map(([location, tags]) => (
            <div key={location} className="location-group">
              <h4 className="location-group-title">{location}</h4>
              <div className="external-devices-grid">
                {tags.map(tag => (
                  <div key={tag.tag_id} className="device-item external-device">
                    <div className="device-header">
                      <span className="device-id">{tag.tag_id}</span>
                      <span className="device-source">{tag.source}</span>
                    </div>
                    
                    <div className="device-details">
                      <div className="device-position">
                        <span className="position-label">Position:</span>
                        <span className="position-value">
                          X: {tag.x?.toFixed(1) || 'N/A'}, Y: {tag.y?.toFixed(1) || 'N/A'}
                        </span>
                      </div>
                      
                      {tag.battery && (
                        <div className="device-battery">
                          <span className="battery-label">Battery:</span>
                          <span className={`battery-value ${tag.battery < 20 ? 'low' : ''}`}>
                            {tag.battery}%
                          </span>
                        </div>
                      )}
                      
                      {tag.confidence && (
                        <div className="device-confidence">
                          <span className="confidence-label">Confidence:</span>
                          <span className="confidence-value">{tag.confidence}%</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="device-footer">
                      <span className="device-timestamp">
                        {tag.timestamp ? 
                          new Date(tag.timestamp).toLocaleTimeString() : 
                          'No timestamp'
                        }
                      </span>
                      {tag.gateway_id && (
                        <span className="device-gateway">via {tag.gateway_id}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
          
          <div className="external-data-summary">
            <span className="summary-info">
              {externalPositions.length} external device{externalPositions.length !== 1 ? 's' : ''} active
            </span>
            <a href="#external-devices" className="view-external-link">
              View external device details →
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default LocationSections;