/* Name: CampusControls.js */
/* Version: 0.1.0 */
/* Created: 250725 */
/* Modified: 250725 */
/* Creator: ParcoAdmin + Claude */
/* Description: Campus selection controls extracted from TDZ_index.js for modularity */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/components */
/* Role: Frontend Component */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

/**
 * Campus Controls Component - Handles campus selection
 */
const CampusControls = ({
  selectedCampusId,
  availableCampuses,
  campusesLoading,
  handleCampusChange
}) => {
  return (
    <div className="controls-panel">
      <h3>🏫 Campus Selection (Required First)</h3>
      <div className="controls-grid">
        
        <div className="control-group">
          <label>Select Campus:</label>
          <select 
            value={selectedCampusId || ""} 
            onChange={(e) => handleCampusChange(e.target.value)}
            disabled={campusesLoading}
          >
            <option value="">-- Select Campus First --</option>
            {availableCampuses.map(campus => (
              <option key={campus.zone_id} value={campus.zone_id}>
                🏫 {campus.zone_name} (ID: {campus.zone_id}, Map: {campus.map_id})
              </option>
            ))}
          </select>
        </div>

        {campusesLoading && (
          <div style={{ color: '#666', fontStyle: 'italic' }}>
            ⏳ Loading available campuses...
          </div>
        )}

        {!selectedCampusId && (
          <div style={{ 
            color: '#856404', 
            backgroundColor: '#fff3cd', 
            border: '1px solid #ffeaa7', 
            borderRadius: '4px', 
            padding: '8px',
            marginTop: '10px'
          }}>
            ⚠️ Please select a campus first to view zones and real-time tags
          </div>
        )}
      </div>
    </div>
  );
};

export default CampusControls;