/* Name: StatusPanel.js */
/* Version: 0.1.0 */
/* Created: 250725 */
/* Modified: 250725 */
/* Creator: ParcoAdmin + Claude */
/* Description: Status panel component extracted from TDZ_index.js for modularity */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/components */
/* Role: Frontend Component */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

/**
 * Status Panel Component - Displays system status information
 */
const StatusPanel = ({
  selectedCampusId,
  selectedCampusName,
  availableCampuses,
  loading,
  campusesLoading,
  totalZones,
  selectedMapId,
  zoneSettings,
  tagConnectionEnabled,
  tagIsConnected,
  displayTags,
  devicesLoading,
  devicesError,
  availableDevices,
  selectedTagDeviceTypes,
  deviceTypeStats,
  alltraqTags,
  campusTags,
  tagConfig,
  tagStats,
  showZoneLabels,
  showCornerMarkers,
  useCascadeVisibility,
  error,
  showDatabaseDebug,
  setShowDatabaseDebug
}) => {
  return (
    <div className="status-panel">
      <h3>📊 Status</h3>
      <div className="status-grid">
        <div className="status-item">
          <strong>Campus Selected:</strong>
          <span className="status-value">
            {selectedCampusId ? `✅ ${selectedCampusName} (${selectedCampusId})` : '❌ None'}
          </span>
        </div>
        <div className="status-item">
          <strong>Available Campuses:</strong>
          <span className="status-value">{availableCampuses.length}</span>
        </div>
        <div className="status-item">
          <strong>Loading:</strong>
          <span className="status-value">{loading || campusesLoading ? '⏳ Yes' : '✅ No'}</span>
        </div>
        <div className="status-item">
          <strong>Total Zones:</strong>
          <span className="status-value">{totalZones}</span>
        </div>
        <div className="status-item">
          <strong>Selected Map:</strong>
          <span className="status-value">{selectedMapId || 'None'}</span>
        </div>
        <div className="status-item">
          <strong>Zone Settings:</strong>
          <span className="status-value">{Object.keys(zoneSettings).length} zones</span>
        </div>
        <div className="status-item">
          <strong>Real-Time Tags:</strong>
          <span className="status-value">
            {tagConnectionEnabled ? 
              (tagIsConnected ? `🔗 ${Object.keys(displayTags).length} shown` : '⏳ Connecting') : 
              '🚫 Disabled'
            }
          </span>
        </div>
        <div className="status-item">
          <strong>Available Devices:</strong>
          <span className="status-value">
            {devicesLoading ? '⏳ Loading' : 
              devicesError ? '❌ Error' : 
              `📱 ${availableDevices.length} loaded`
            }
            {/* Debug toggle button */}
            {selectedCampusId && availableDevices.length > 0 && (
              <button
                onClick={() => setShowDatabaseDebug(!showDatabaseDebug)}
                style={{
                  marginLeft: '8px',
                  padding: '2px 6px',
                  fontSize: '10px',
                  backgroundColor: showDatabaseDebug ? '#007bff' : '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '3px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
                title={showDatabaseDebug ? 'Hide device debug info' : 'Show device debug info'}
              >
                🔍 {showDatabaseDebug ? 'Hide' : 'Debug'}
              </button>
            )}
          </span>
        </div>
        <div className="status-item">
          <strong>Selected Device Types:</strong>
          <span className="status-value">
            {selectedTagDeviceTypes.length} types ({selectedTagDeviceTypes.join(', ')})
          </span>
        </div>
        <div className="status-item">
          <strong>Device Breakdown:</strong>
          <span className="status-value">
            {Object.entries(deviceTypeStats).map(([typeId, stats]) => 
              `${stats.description}: ${stats.count}`
            ).join(', ') || 'None loaded'}
          </span>
        </div>
        <div className="status-item">
          <strong>Active Tags:</strong>
          <span className="status-value">
            {tagConnectionEnabled ? `📈 ${Object.keys(alltraqTags).length} alltraq, ${Object.keys(campusTags).length} campus` : '➖ N/A'}
          </span>
        </div>
        <div className="status-item">
          <strong>Tag Height Mode:</strong>
          <span className="status-value">
            {tagConfig.useActualHeight ? '📏 Actual Z-coord' : '🔧 Fixed Offset'}
          </span>
        </div>
        <div className="status-item">
          <strong>Tag Rate:</strong>
          <span className="status-value">
            {tagIsConnected ? `📈 ${tagStats.tagRate.toFixed(1)}/s` : '➖ N/A'}
          </span>
        </div>
        <div className="status-item">
          <strong>Zone Labels:</strong>
          <span className="status-value">{showZoneLabels ? '📋 ON' : '🚫 OFF'}</span>
        </div>
        <div className="status-item">
          <strong>Corner Markers:</strong>
          <span className="status-value">{showCornerMarkers ? '🔴🔵 ON' : '🚫 OFF'}</span>
        </div>
        <div className="status-item">
          <strong>Cascade Visibility:</strong>
          <span className="status-value">{useCascadeVisibility ? '🔗 ON' : '🚫 OFF'}</span>
        </div>
      </div>
      
      {error && (
        <div className="error-message">
          ❌ <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
};

export default StatusPanel;