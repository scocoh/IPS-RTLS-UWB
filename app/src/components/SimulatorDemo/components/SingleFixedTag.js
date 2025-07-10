/* Name: SingleFixedTag.js */
/* Version: 0.1.1 */
/* Created: 250707 */
/* Modified: 250708 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Single fixed tag simulation mode component - fixed ping rate input */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/SimulatorDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from 'react';

const SingleFixedTag = ({ onConfigChange, disabled }) => {
  const [config, setConfig] = useState({
    tagId: 'SIM3',
    position: { x: 5, y: 5, z: 5 },
    pingRate: 0.25
  });

  // Display value for ping rate to allow partial input
  const [pingRateDisplay, setPingRateDisplay] = useState('0.25');

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
  }, [config, onConfigChange]);

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

  const handlePingRateChange = (value) => {
    setPingRateDisplay(value);
    
    // Only update the actual config if the value is a valid number
    const numValue = parseFloat(value);
    if (!isNaN(numValue) && numValue > 0) {
      setConfig(prev => ({
        ...prev,
        pingRate: numValue
      }));
    }
  };

  const handlePingRateBlur = () => {
    // On blur, ensure we have a valid value
    const numValue = parseFloat(pingRateDisplay);
    if (isNaN(numValue) || numValue <= 0) {
      setPingRateDisplay('0.25');
      setConfig(prev => ({
        ...prev,
        pingRate: 0.25
      }));
    }
  };

  return (
    <div className="mode-component">
      <h3>Single Fixed Tag Configuration</h3>
      <p className="mode-description">
        Simulates a single tag at a fixed position sending regular position updates.
      </p>

      <div className="config-section">
        <div className="form-group">
          <label>Tag ID:</label>
          <input
            type="text"
            value={config.tagId}
            onChange={(e) => handleConfigChange('tagId', e.target.value)}
            disabled={disabled}
            placeholder="Enter tag ID (e.g., SIM3)"
          />
        </div>

        <div className="form-group">
          <label>Ping Rate (Hz):</label>
          <input
            type="text"
            inputMode="decimal"
            pattern="^\\d*\\.?\\d*$"
            value={pingRateDisplay}
            onChange={(e) => handlePingRateChange(e.target.value)}
            onBlur={handlePingRateBlur}
            disabled={disabled}
            placeholder="0.25"
          />
          <small>Messages per second (0.01 - 10 Hz)</small>
        </div>

        <div className="position-section">
          <h4>Position</h4>
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

        <div className="config-summary">
          <h4>Configuration Summary</h4>
          <ul>
            <li>Tag ID: <strong>{config.tagId}</strong></li>
            <li>Position: <strong>({config.position.x}, {config.position.y}, {config.position.z})</strong></li>
            <li>Ping Rate: <strong>{config.pingRate} Hz</strong> ({(1/config.pingRate).toFixed(2)}s interval)</li>
            <li>Type: <strong>Stationary</strong></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SingleFixedTag;