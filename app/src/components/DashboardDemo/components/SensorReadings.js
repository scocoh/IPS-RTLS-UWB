/* Name: SensorReadings.js */
/* Version: 0.1.1 */
/* Created: 250711 */
/* Modified: 250712 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Sensor readings component for dashboard */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/DashboardDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

const SensorReadings = ({ sensors = [], isLoading = false }) => {
  // Helper function to format last reading time
  const formatLastReading = (timestamp) => {
    if (!timestamp) return 'No data';
    
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMins / 60);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      
      return date.toLocaleDateString();
    } catch (error) {
      return 'Invalid date';
    }
  };

  // Sample sensor data if none provided
  const sampleSensors = [
    {
      sensor_id: 'TEMP_01',
      sensor_type: 'Temperature',
      reading_value: 22.5,
      unit_of_measure: '°C',
      status: 'online',
      location_name: 'Sample Customer',
      last_reading: new Date().toISOString()
    },
    {
      sensor_id: 'HUMID_01', 
      sensor_type: 'Humidity',
      reading_value: 45.2,
      unit_of_measure: '%',
      status: 'online',
      location_name: 'Surgical Center',
      last_reading: new Date(Date.now() - 300000).toISOString()
    },
    {
      sensor_id: 'PRESS_01',
      sensor_type: 'Pressure',
      reading_value: 1013.25,
      unit_of_measure: 'hPa',
      status: 'offline',
      location_name: 'Transport Van',
      last_reading: new Date(Date.now() - 3600000).toISOString()
    }
  ];

  const displaySensors = sensors.length > 0 ? sensors : sampleSensors;

  if (isLoading) {
    return (
      <div className="sensor-readings">
        <h2>Current Readings</h2>
        <div className="sensor-loading">
          <div className="loading-indicators">
            ████████
          </div>
          <p>Loading sensor data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="sensor-readings">
      <h2>Current Readings</h2>
      <div className="daily-sensor-report">
        <a href="#daily-report" className="sensor-report-link">
          Daily Sensor Report
        </a>
      </div>

      {displaySensors.length > 0 ? (
        <div className="sensor-grid">
          {displaySensors.map((sensor, index) => (
            <div key={sensor.sensor_id || index} className="sensor-card">
              <div className="sensor-header">
                <div className="sensor-info">
                  <div className="sensor-name">{sensor.sensor_id}</div>
                  <div className="sensor-type">{sensor.sensor_type}</div>
                </div>
                <div className={`sensor-status ${sensor.status}`}>
                  {sensor.status}
                </div>
              </div>

              <div className="sensor-reading">
                {sensor.reading_value !== null && sensor.reading_value !== undefined ? (
                  <>
                    <span className="reading-value">
                      {typeof sensor.reading_value === 'number' 
                        ? sensor.reading_value.toFixed(1)
                        : sensor.reading_value
                      }
                    </span>
                    <span className="sensor-unit">
                      {sensor.unit_of_measure || ''}
                    </span>
                  </>
                ) : (
                  <span className="reading-value no-data">--</span>
                )}
              </div>

              <div className="sensor-meta">
                {sensor.location_name && (
                  <div className="sensor-location">
                    📍 {sensor.location_name}
                  </div>
                )}
                <div className="sensor-last-reading">
                  Last: {formatLastReading(sensor.last_reading)}
                </div>
              </div>

              {/* Optional: Sensor trend indicator */}
              {sensor.status === 'online' && (
                <div className="sensor-trend">
                  <div className="trend-indicator stable">
                    📈 Stable
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="no-sensors-message">
          <p>No sensor data available</p>
          <small>Sensor readings will appear here when available.</small>
        </div>
      )}

      {/* Footer with additional info */}
      <div className="sensor-footer">
        <div className="sensor-summary">
          <span>
            {displaySensors.filter(s => s.status === 'online').length} online
          </span>
          <span>•</span>
          <span>
            {displaySensors.filter(s => s.status === 'offline').length} offline
          </span>
          <span>•</span>
          <span>
            {displaySensors.length} total sensors
          </span>
        </div>
      </div>
    </div>
  );
};

export default SensorReadings;