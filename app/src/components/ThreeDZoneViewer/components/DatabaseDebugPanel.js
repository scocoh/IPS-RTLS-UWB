/* Name: DatabaseDebugPanel.js */
/* Version: 0.1.0 */
/* Created: 250724 */
/* Modified: 250724 */
/* Creator: ParcoAdmin + Claude */
/* Description: Debug panel to validate database device loading before WebSocket integration */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/components */
/* Role: Frontend Debug Component */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useMemo } from 'react';

/**
 * Database Debug Panel - Validates device loading from database
 * @param {Object} props - Component props
 * @param {Array} props.availableDevices - Devices loaded from database
 * @param {Array} props.availableDeviceTypes - Device types from database
 * @param {Object} props.deviceTypeStats - Device type statistics
 * @param {boolean} props.devicesLoading - Loading state
 * @param {string} props.devicesError - Error message if any
 * @param {Function} props.refreshDevices - Function to refresh device list
 * @param {Array} props.selectedDeviceTypes - Currently selected device types
 * @returns {JSX.Element} Debug panel component
 */
const DatabaseDebugPanel = ({
  availableDevices = [],
  availableDeviceTypes = [],
  deviceTypeStats = {},
  devicesLoading = false,
  devicesError = null,
  refreshDevices = null,
  selectedDeviceTypes = []
}) => {
  const [expandedSections, setExpandedSections] = useState({
    summary: true,
    deviceTypes: false,
    devices: false,
    tagIds: false,
    validation: true
  });
  
  const [showAllDevices, setShowAllDevices] = useState(false);
  
  // Extract tag IDs from devices (matching WebSocket integration logic)
  const extractedTagIds = useMemo(() => {
    return availableDevices
      .map(device => device.x_id_dev || device.deviceId || device.id)
      .filter(id => id) // Remove null/undefined
      .map(id => String(id)) // Ensure strings
      .sort(); // Sort for easier validation
  }, [availableDevices]);
  
  // Group devices by type for analysis
  const devicesByType = useMemo(() => {
    const grouped = {};
    availableDevices.forEach(device => {
      const typeId = device.i_typ_dev || device.deviceTypeId || 'unknown';
      if (!grouped[typeId]) {
        grouped[typeId] = [];
      }
      grouped[typeId].push(device);
    });
    return grouped;
  }, [availableDevices]);
  
  // Validate device structure
  const deviceValidation = useMemo(() => {
    const validation = {
      totalDevices: availableDevices.length,
      devicesWithTagIds: 0,
      devicesWithoutTagIds: 0,
      uniqueTagIds: new Set(),
      duplicateTagIds: [],
      fieldAnalysis: {},
      deviceTypeBreakdown: {}
    };
    
    // Analyze each device
    availableDevices.forEach(device => {
      // Check for tag ID
      const tagId = device.x_id_dev || device.deviceId || device.id;
      if (tagId) {
        validation.devicesWithTagIds++;
        const tagIdStr = String(tagId);
        if (validation.uniqueTagIds.has(tagIdStr)) {
          validation.duplicateTagIds.push(tagIdStr);
        } else {
          validation.uniqueTagIds.add(tagIdStr);
        }
      } else {
        validation.devicesWithoutTagIds++;
      }
      
      // Analyze field structure
      Object.keys(device).forEach(field => {
        if (!validation.fieldAnalysis[field]) {
          validation.fieldAnalysis[field] = { count: 0, sampleValues: [] };
        }
        validation.fieldAnalysis[field].count++;
        if (validation.fieldAnalysis[field].sampleValues.length < 3) {
          validation.fieldAnalysis[field].sampleValues.push(device[field]);
        }
      });
      
      // Device type breakdown
      const typeId = device.i_typ_dev || device.deviceTypeId || 'unknown';
      validation.deviceTypeBreakdown[typeId] = (validation.deviceTypeBreakdown[typeId] || 0) + 1;
    });
    
    return validation;
  }, [availableDevices]);
  
  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  
  const SectionHeader = ({ title, section, count = null }) => (
    <div 
      onClick={() => toggleSection(section)}
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 12px',
        backgroundColor: '#f8f9fa',
        border: '1px solid #dee2e6',
        borderRadius: '4px',
        cursor: 'pointer',
        marginBottom: expandedSections[section] ? '10px' : '5px',
        fontWeight: 'bold'
      }}
    >
      <span>
        {expandedSections[section] ? '▼' : '▶'} {title}
        {count !== null && <span style={{ fontWeight: 'normal', marginLeft: '8px' }}>({count})</span>}
      </span>
      <span style={{ fontSize: '12px', color: '#666' }}>
        Click to {expandedSections[section] ? 'collapse' : 'expand'}
      </span>
    </div>
  );
  
  return (
    <div style={{
      border: '2px solid #007bff',
      borderRadius: '8px',
      padding: '15px',
      backgroundColor: '#ffffff',
      marginBottom: '20px'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '15px'
      }}>
        <h4 style={{ margin: 0, color: '#007bff' }}>
          🔍 Database Debug Panel - Device Validation
        </h4>
        {refreshDevices && (
          <button
            onClick={refreshDevices}
            disabled={devicesLoading}
            style={{
              padding: '6px 12px',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: devicesLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {devicesLoading ? '⏳ Loading...' : '🔄 Refresh'}
          </button>
        )}
      </div>
      
      {/* Loading State */}
      {devicesLoading && (
        <div style={{
          textAlign: 'center',
          padding: '20px',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffeaa7',
          borderRadius: '4px',
          marginBottom: '15px'
        }}>
          ⏳ Loading devices from database...
        </div>
      )}
      
      {/* Error State */}
      {devicesError && (
        <div style={{
          padding: '15px',
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          borderRadius: '4px',
          color: '#721c24',
          marginBottom: '15px'
        }}>
          <strong>❌ Error loading devices:</strong> {devicesError}
        </div>
      )}
      
      {/* Summary Section */}
      <SectionHeader 
        title="📊 Summary" 
        section="summary" 
      />
      {expandedSections.summary && (
        <div style={{
          padding: '12px',
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '4px',
          marginBottom: '15px'
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
            <div>
              <strong>📱 Total Devices:</strong> {availableDevices.length}
              <br />
              <strong>🏷️ Valid Tag IDs:</strong> {deviceValidation.devicesWithTagIds}
              <br />
              <strong>❌ Missing Tag IDs:</strong> {deviceValidation.devicesWithoutTagIds}
            </div>
            <div>
              <strong>🎯 Device Types:</strong> {availableDeviceTypes.length}
              <br />
              <strong>✅ Selected Types:</strong> {selectedDeviceTypes.length}
              <br />
              <strong>🔢 Unique Tag IDs:</strong> {extractedTagIds.length}
            </div>
            <div>
              <strong>🔄 Loading:</strong> {devicesLoading ? 'YES' : 'NO'}
              <br />
              <strong>⚠️ Errors:</strong> {devicesError ? 'YES' : 'NO'}
              <br />
              <strong>🔍 Duplicates:</strong> {deviceValidation.duplicateTagIds.length}
            </div>
          </div>
        </div>
      )}
      
      {/* Validation Section */}
      <SectionHeader 
        title="✅ Validation Results" 
        section="validation" 
      />
      {expandedSections.validation && (
        <div style={{
          padding: '12px',
          backgroundColor: extractedTagIds.length > 0 ? '#d4edda' : '#f8d7da',
          border: `1px solid ${extractedTagIds.length > 0 ? '#c3e6cb' : '#f5c6cb'}`,
          borderRadius: '4px',
          marginBottom: '15px'
        }}>
          <div style={{ fontSize: '14px' }}>
            <div style={{ marginBottom: '10px' }}>
              <strong>🎯 WebSocket Integration Ready:</strong>{' '}
              <span style={{ 
                color: extractedTagIds.length > 0 ? '#155724' : '#721c24',
                fontWeight: 'bold'
              }}>
                {extractedTagIds.length > 0 ? 'YES' : 'NO'}
              </span>
            </div>
            
            <div style={{ fontSize: '13px', color: '#333' }}>
              • <strong>Extracted Tag IDs:</strong> {extractedTagIds.length} (from x_id_dev field)
              <br />
              • <strong>Tag ID Range:</strong> {extractedTagIds.length > 0 ? 
                  `${extractedTagIds[0]} to ${extractedTagIds[extractedTagIds.length - 1]}` : 'N/A'}
              <br />
              • <strong>Sample Tag IDs:</strong> {extractedTagIds.slice(0, 10).join(', ')}
              {extractedTagIds.length > 10 && '...'}
              <br />
              • <strong>Ready for WebSocket:</strong> {extractedTagIds.length > 0 ? 
                  '✅ Can replace hardcoded list' : '❌ Will use fallback'}
            </div>
            
            {deviceValidation.duplicateTagIds.length > 0 && (
              <div style={{ 
                marginTop: '10px', 
                padding: '8px', 
                backgroundColor: '#fff3cd', 
                borderRadius: '3px' 
              }}>
                <strong>⚠️ Duplicate Tag IDs Found:</strong> {deviceValidation.duplicateTagIds.join(', ')}
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Device Types Section */}
      <SectionHeader 
        title="🎯 Device Types" 
        section="deviceTypes" 
        count={availableDeviceTypes.length}
      />
      {expandedSections.deviceTypes && (
        <div style={{
          padding: '12px',
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '4px',
          marginBottom: '15px'
        }}>
          {availableDeviceTypes.length > 0 ? (
            <div style={{ fontSize: '13px' }}>
              {availableDeviceTypes.map(deviceType => (
                <div key={deviceType.i_typ_dev} style={{ 
                  marginBottom: '8px',
                  padding: '6px',
                  backgroundColor: selectedDeviceTypes.includes(deviceType.i_typ_dev) ? '#d4edda' : '#ffffff',
                  border: '1px solid #dee2e6',
                  borderRadius: '3px'
                }}>
                  <strong>ID {deviceType.i_typ_dev}:</strong> {deviceType.x_dsc_dev}
                  {deviceTypeStats[deviceType.i_typ_dev] && (
                    <span style={{ marginLeft: '10px', color: '#666' }}>
                      ({deviceTypeStats[deviceType.i_typ_dev].count} devices)
                    </span>
                  )}
                  {selectedDeviceTypes.includes(deviceType.i_typ_dev) && (
                    <span style={{ marginLeft: '10px', color: '#155724', fontWeight: 'bold' }}>
                      ✅ SELECTED
                    </span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: '#666', fontStyle: 'italic' }}>
              No device types loaded
            </div>
          )}
        </div>
      )}
      
      {/* Extracted Tag IDs Section */}
      <SectionHeader 
        title="🏷️ Extracted Tag IDs" 
        section="tagIds" 
        count={extractedTagIds.length}
      />
      {expandedSections.tagIds && (
        <div style={{
          padding: '12px',
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '4px',
          marginBottom: '15px'
        }}>
          {extractedTagIds.length > 0 ? (
            <div>
              <div style={{ marginBottom: '10px', fontSize: '13px' }}>
                <strong>Ready for WebSocket Subscription:</strong> {extractedTagIds.length} tag IDs extracted
              </div>
              <div style={{
                fontFamily: 'monospace',
                fontSize: '12px',
                backgroundColor: '#ffffff',
                padding: '10px',
                border: '1px solid #dee2e6',
                borderRadius: '3px',
                maxHeight: '200px',
                overflowY: 'auto'
              }}>
                {extractedTagIds.join(', ')}
              </div>
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                💡 These tag IDs can be used directly in WebSocket subscription (replacing hardcoded list)
              </div>
            </div>
          ) : (
            <div style={{ color: '#666', fontStyle: 'italic' }}>
              No valid tag IDs extracted from devices
            </div>
          )}
        </div>
      )}
      
      {/* Raw Devices Section */}
      <SectionHeader 
        title="📱 Raw Device Data" 
        section="devices" 
        count={availableDevices.length}
      />
      {expandedSections.devices && (
        <div style={{
          padding: '12px',
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '4px',
          marginBottom: '15px'
        }}>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ fontSize: '13px' }}>
              <input
                type="checkbox"
                checked={showAllDevices}
                onChange={(e) => setShowAllDevices(e.target.checked)}
                style={{ marginRight: '6px' }}
              />
              Show all devices (currently showing first {showAllDevices ? availableDevices.length : Math.min(5, availableDevices.length)})
            </label>
          </div>
          
          {availableDevices.length > 0 ? (
            <div style={{
              maxHeight: '300px',
              overflowY: 'auto',
              fontSize: '12px'
            }}>
              {(showAllDevices ? availableDevices : availableDevices.slice(0, 5)).map((device, index) => (
                <div key={index} style={{
                  marginBottom: '10px',
                  padding: '8px',
                  backgroundColor: '#ffffff',
                  border: '1px solid #dee2e6',
                  borderRadius: '3px'
                }}>
                  <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                    Device #{index + 1}
                    {device.x_id_dev && (
                      <span style={{ color: '#28a745', marginLeft: '10px' }}>
                        ✅ Tag ID: {device.x_id_dev}
                      </span>
                    )}
                  </div>
                  <div style={{ fontFamily: 'monospace', fontSize: '11px', color: '#666' }}>
                    {JSON.stringify(device, null, 2)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: '#666', fontStyle: 'italic' }}>
              No devices loaded
            </div>
          )}
        </div>
      )}
      
      {/* Integration Instructions */}
      <div style={{
        padding: '12px',
        backgroundColor: '#e7f3ff',
        border: '1px solid #b3d9ff',
        borderRadius: '4px',
        fontSize: '13px'
      }}>
        <strong>📋 Next Steps for WebSocket Integration:</strong>
        <ol style={{ marginTop: '8px', marginBottom: 0 }}>
          <li>✅ Verify "Extracted Tag IDs" section shows {extractedTagIds.length} valid tag IDs</li>
          <li>✅ Confirm tag IDs match expected format (e.g., "26070", "26071", etc.)</li>
          <li>✅ Check that selected device types contain the devices you want to track</li>
          <li>🔄 Once validated, integrate these tag IDs into useWebSocketConnection.js</li>
          <li>🧪 Test WebSocket subscription with database tag IDs vs hardcoded fallback</li>
        </ol>
      </div>
    </div>
  );
};

export default DatabaseDebugPanel;