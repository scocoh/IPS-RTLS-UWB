/* Name: LocationSections.js */
/* Version: 0.1.2 */
/* Created: 250711 */
/* Modified: 250712 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Location sections component for dashboard with dynamic device categories */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/DashboardDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

const LocationSections = ({ locations, metrics, deviceCategories, customerId = 1 }) => {
  const getMetricValue = (metricName) => {
    const metric = metrics?.find(m => m.metric_name === metricName);
    return metric ? metric.metric_value : 0;
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
    </div>
  );
};

export default LocationSections;