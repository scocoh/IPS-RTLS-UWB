/* Name: TetseDebugMode.js */
/* Version: 0.1.0 */
/* Created: 250708 */
/* Modified: 250708 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: TETSE Debug Mode simulation component */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/SimulatorDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from 'react';

const TetseDebugMode = ({ onConfigChange, disabled, zoneId, onZoneIdChange }) => {
  const [config, setConfig] = useState({
    tagId: '23001',
    position: { x: 100.5, y: 200.7, z: 1.0 },
    pingRate: 0.75,
    useDefaultSettings: true
  });

  // Update parent when config changes
  useEffect(() => {
    const tagConfig = {
      tagId: config.tagId,
      positions: [config.position],
      pingRate: config.pingRate,
      moveInterval: 0,
      sequenceNumber: 1
    };
    onConfigChange([tagConfig]);

    // Set zone to 422 (6005Campus) for TETSE testing
    if (config.useDefaultSettings && onZoneIdChange) {
      onZoneIdChange(422);
    }
  }, [config, onConfigChange, onZoneIdChange]);

  const handleConfigChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handlePositionChange = (axis, value) => {
    setConfig(prev => ({
      ...prev,
      position: {
        ...prev.position,
        [axis]: parseFloat(value) || 0
      }
    }));
  };

  const applyPreset = (preset) => {
    const presets = {
      default: {
        tagId: '23001',
        position: { x: 100.5, y: 200.7, z: 1.0 },
        pingRate: 0.75,
        useDefaultSettings: true
      },
      highFreq: {
        tagId: '23001',
        position: { x: 100.5, y: 200.7, z: 1.0 },
        pingRate: 2.0,
        useDefaultSettings: true
      },
      custom: {
        tagId: 'DEBUG1',
        position: { x: 50, y: 50, z: 2 },
        pingRate: 1.0,
        useDefaultSettings: false
      }
    };

    setConfig(prev => ({
      ...prev,
      ...presets[preset]
    }));
  };

  return (
    <div className="mode-component">
      <h3>TETSE Debug Mode Configuration</h3>
      <p className="mode-description">
        Special mode for testing TETSE rule evaluation with specific coordinates and zone settings.
        Uses zone 422 (6005Campus) by default for comprehensive trigger testing.
      </p>

      <div className="config-section">
        {/* Presets */}
        <div className="presets-section">
          <h4>TETSE Test Presets</h4>
          <div className="preset-buttons">
            <button 
              onClick={() => applyPreset('default')} 
              disabled={disabled} 
              className="preset-btn primary"
            >
              Default TETSE
            </button>
            <button 
              onClick={() => applyPreset('highFreq')} 
              disabled={disabled} 
              className="preset-btn"
            >
              High Frequency
            </button>
            <button 
              onClick={() => applyPreset('custom')} 
              disabled={disabled} 
              className="preset-btn"
            >
              Custom Test
            </button>
          </div>
        </div>

        {/* Configuration Controls */}
        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={config.useDefaultSettings}
              onChange={(e) => handleConfigChange('useDefaultSettings', e.target.checked)}
              disabled={disabled}
            />
            Use default TETSE settings (Zone 422, optimized coordinates)
          </label>
        </div>

        <div className="form-group">
          <label>Tag ID:</label>
          <input
            type="text"
            value={config.tagId}
            onChange={(e) => handleConfigChange('tagId', e.target.value)}
            disabled={disabled}
            placeholder="23001"
          />
          <small>Standard TETSE test tag ID</small>
        </div>

        <div className="form-group">
          <label>Ping Rate (Hz):</label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            max="10"
            value={config.pingRate}
            onChange={(e) => handleConfigChange('pingRate', parseFloat(e.target.value))}
            disabled={disabled}
          />
          <small>TETSE evaluation frequency ({(1/config.pingRate).toFixed(2)}s interval)</small>
        </div>

        <div className="position-section">
          <h4>Test Position</h4>
          <div className="position-inputs">
            <div className="position-input">
              <label>X:</label>
              <input
                type="number"
                step="0.1"
                value={config.position.x}
                onChange={(e) => handlePositionChange('x', e.target.value)}
                disabled={disabled}
              />
            </div>
            <div className="position-input">
              <label>Y:</label>
              <input
                type="number"
                step="0.1"
                value={config.position.y}
                onChange={(e) => handlePositionChange('y', e.target.value)}
                disabled={disabled}
              />
            </div>
            <div className="position-input">
              <label>Z:</label>
              <input
                type="number"
                step="0.1"
                value={config.position.z}
                onChange={(e) => handlePositionChange('z', e.target.value)}
                disabled={disabled}
              />
            </div>
          </div>
        </div>

        {/* TETSE Information */}
        <div className="tetse-info">
          <h4>TETSE Debug Information</h4>
          <div className="info-grid">
            <div className="info-item">
              <strong>Target Zone:</strong> {config.useDefaultSettings ? '422 (6005Campus)' : `${zoneId} (Current)`}
            </div>
            <div className="info-item">
              <strong>Test Duration:</strong> 10 seconds (default)
            </div>
            <div className="info-item">
              <strong>Expected Triggers:</strong> All active triggers in zone
            </div>
            <div className="info-item">
              <strong>Debug Logging:</strong> Enhanced TETSE evaluation logs
            </div>
          </div>
        </div>

        <div className="config-summary">
          <h4>Configuration Summary</h4>
          <ul>
            <li>Tag ID: <strong>{config.tagId}</strong></li>
            <li>Position: <strong>({config.position.x}, {config.position.y}, {config.position.z})</strong></li>
            <li>Ping Rate: <strong>{config.pingRate} Hz</strong> ({(1/config.pingRate).toFixed(2)}s interval)</li>
            <li>Zone: <strong>{config.useDefaultSettings ? '422 (6005Campus)' : `${zoneId} (Current)`}</strong></li>
            <li>Mode: <strong>TETSE Debug & Rule Evaluation</strong></li>
            <li>Purpose: <strong>Test trigger containment and rule processing</strong></li>
          </ul>
        </div>

        {/* Warning */}
        <div className="warning-section">
          <h4>⚠️ Debug Mode Notes</h4>
          <ul>
            <li>This mode generates enhanced logging for TETSE rule evaluation</li>
            <li>Monitor backend logs for detailed trigger processing information</li>
            <li>Zone 422 contains test triggers optimized for debugging</li>
            <li>Position coordinates are chosen to test boundary conditions</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TetseDebugMode;