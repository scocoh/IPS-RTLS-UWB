/* Name: SingleMovingTag.js */
/* Version: 0.1.5 */
/* Created: 250708 */
/* Modified: 250708 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Single moving tag simulation mode component - fixed config passing to include feetPerInterval and movementBehavior */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/SimulatorDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from 'react';

const SingleMovingTag = ({ onConfigChange, disabled }) => {
  const [config, setConfig] = useState({
    tagId: 'SIM3',
    positions: [
      { x: 5, y: 5, z: 5 },    // Inside region
      { x: 100, y: 100, z: 1 }   // Outside region
    ],
    pingRate: 0.25,
    moveInterval: 0.25,
    feetPerInterval: 0.2,
    movementBehavior: 'bounce' // 'stop', 'bounce', 'restart'
  });

  // Display values for decimal inputs
  const [pingRateDisplay, setPingRateDisplay] = useState('0.25');
  const [moveIntervalDisplay, setMoveIntervalDisplay] = useState('0.25');
  const [feetPerIntervalDisplay, setFeetPerIntervalDisplay] = useState('0.2');

  // Update parent when config changes
  useEffect(() => {
    const tagConfig = {
      tagId: config.tagId,
      positions: config.positions,
      pingRate: config.pingRate,
      moveInterval: config.moveInterval,
      feetPerInterval: config.feetPerInterval,
      movementBehavior: config.movementBehavior,
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

  const handlePositionChange = (posIndex, axis, value) => {
    setConfig(prev => ({
      ...prev,
      positions: prev.positions.map((pos, index) => 
        index === posIndex 
          ? { ...pos, [axis]: parseFloat(value) || 0 }
          : pos
      )
    }));
  };

  const handlePingRateChange = (value) => {
    setPingRateDisplay(value);
    
    // Only update the actual config if the value is a valid number
    const numValue = parseFloat(value);
    if (!isNaN(numValue) && numValue > 0) {
      setConfig(prev => ({
        ...prev,
        pingRate: numValue,
        moveInterval: numValue  // Sync move interval with ping rate
      }));
      setMoveIntervalDisplay(value);  // Keep displays in sync
    }
  };

  const handlePingRateBlur = () => {
    // On blur, ensure we have a valid value
    const numValue = parseFloat(pingRateDisplay);
    if (isNaN(numValue) || numValue <= 0) {
      setPingRateDisplay('0.25');
      setMoveIntervalDisplay('0.25');
      setConfig(prev => ({
        ...prev,
        pingRate: 0.25,
        moveInterval: 0.25
      }));
    }
  };

  const handleMoveIntervalChange = (value) => {
    setMoveIntervalDisplay(value);
    
    // Only update the actual config if the value is a valid number
    const numValue = parseFloat(value);
    if (!isNaN(numValue) && numValue > 0) {
      setConfig(prev => ({
        ...prev,
        moveInterval: numValue
      }));
    }
  };

  const handleMoveIntervalBlur = () => {
    // On blur, ensure we have a valid value
    const numValue = parseFloat(moveIntervalDisplay);
    if (isNaN(numValue) || numValue <= 0) {
      setMoveIntervalDisplay('0.25');
      setConfig(prev => ({
        ...prev,
        moveInterval: 0.25
      }));
    }
  };

  const handleFeetPerIntervalChange = (value) => {
    setFeetPerIntervalDisplay(value);
    
    // Only update the actual config if the value is a valid number
    const numValue = parseFloat(value);
    if (!isNaN(numValue) && numValue > 0) {
      setConfig(prev => ({
        ...prev,
        feetPerInterval: numValue
      }));
    }
  };

  const handleFeetPerIntervalBlur = () => {
    // On blur, ensure we have a valid value
    const numValue = parseFloat(feetPerIntervalDisplay);
    if (isNaN(numValue) || numValue <= 0) {
      setFeetPerIntervalDisplay('0.2');
      setConfig(prev => ({
        ...prev,
        feetPerInterval: 0.2
      }));
    }
  };

  const calculateTotalDistance = () => {
    if (config.positions.length < 2) return 0;
    const dx = config.positions[1].x - config.positions[0].x;
    const dy = config.positions[1].y - config.positions[0].y;
    const dz = config.positions[1].z - config.positions[0].z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  };

  const calculateIntervalsToComplete = () => {
    const totalDistance = calculateTotalDistance();
    return Math.ceil(totalDistance / config.feetPerInterval);
  };

  const addPosition = () => {
    if (config.positions.length < 2) {
      setConfig(prev => ({
        ...prev,
        positions: [...prev.positions, { x: 0, y: 0, z: 0 }]
      }));
    }
  };

  const removePosition = (index) => {
    if (config.positions.length > 1) {
      setConfig(prev => ({
        ...prev,
        positions: prev.positions.filter((_, i) => i !== index)
      }));
    }
  };

  return (
    <div className="mode-component">
      <h3>Single Moving Tag Configuration</h3>
      <p className="mode-description">
        Simulates a single tag moving smoothly between two positions with linear interpolation.
        Useful for testing trigger entry/exit events.
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

        <div className="form-row">
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

          <div className="form-group">
            <label>Feet per Interval:</label>
            <input
              type="text"
              inputMode="decimal"
              pattern="^\\d*\\.?\\d*$"
              value={feetPerIntervalDisplay}
              onChange={(e) => handleFeetPerIntervalChange(e.target.value)}
              onBlur={handleFeetPerIntervalBlur}
              disabled={disabled}
              placeholder="0.2"
            />
            <small>Distance moved per ping</small>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Move Interval (seconds):</label>
            <input
              type="text"
              inputMode="decimal"
              pattern="^\\d*\\.?\\d*$"
              value={moveIntervalDisplay}
              onChange={(e) => handleMoveIntervalChange(e.target.value)}
              onBlur={handleMoveIntervalBlur}
              disabled={disabled}
              placeholder="0.25"
            />
            <small>Time to move between positions (synced with ping rate)</small>
          </div>

          <div className="form-group">
            <label>Movement Behavior:</label>
            <select
              value={config.movementBehavior}
              onChange={(e) => handleConfigChange('movementBehavior', e.target.value)}
              disabled={disabled}
              className="movement-behavior-select"
            >
              <option value="bounce">Bounce (ping-pong between points)</option>
              <option value="stop">Stop at end position</option>
              <option value="restart">Restart from point 1</option>
            </select>
            <small>What happens when reaching end position</small>
          </div>
        </div>

        <div className="position-section">
          <h4>Movement Positions</h4>
          {config.positions.map((position, index) => (
            <div key={index} className="position-group">
              <div className="position-header">
                <label>Position {index + 1} {index === 0 ? '(Start)' : '(End)'}:</label>
                {config.positions.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removePosition(index)}
                    disabled={disabled}
                    className="remove-position-btn"
                  >
                    Remove
                  </button>
                )}
              </div>
              <div className="position-inputs">
                <div className="position-input">
                  <label>X:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={position.x}
                    onChange={(e) => handlePositionChange(index, 'x', e.target.value)}
                    disabled={disabled}
                  />
                </div>
                <div className="position-input">
                  <label>Y:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={position.y}
                    onChange={(e) => handlePositionChange(index, 'y', e.target.value)}
                    disabled={disabled}
                  />
                </div>
                <div className="position-input">
                  <label>Z:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={position.z}
                    onChange={(e) => handlePositionChange(index, 'z', e.target.value)}
                    disabled={disabled}
                  />
                </div>
              </div>
            </div>
          ))}
          
          {config.positions.length < 2 && (
            <button 
              onClick={addPosition}
              disabled={disabled}
              className="add-position-btn"
            >
              Add End Position
            </button>
          )}
        </div>

        <div className="config-summary">
          <h4>Configuration Summary</h4>
          <ul>
            <li>Tag ID: <strong>{config.tagId}</strong></li>
            <li>Start Position: <strong>({config.positions[0]?.x}, {config.positions[0]?.y}, {config.positions[0]?.z})</strong></li>
            {config.positions[1] && (
              <li>End Position: <strong>({config.positions[1].x}, {config.positions[1].y}, {config.positions[1].z})</strong></li>
            )}
            <li>Total Distance: <strong>{calculateTotalDistance().toFixed(2)} feet</strong></li>
            <li>Feet per Interval: <strong>{config.feetPerInterval} feet</strong></li>
            <li>Intervals to Complete: <strong>{calculateIntervalsToComplete()} intervals</strong></li>
            <li>Ping Rate: <strong>{config.pingRate} Hz</strong> ({(1/config.pingRate).toFixed(2)}s interval)</li>
            <li>Movement Behavior: <strong>{config.movementBehavior}</strong></li>
            <li>Time to Complete: <strong>{(calculateIntervalsToComplete() / config.pingRate).toFixed(1)}s</strong></li>
            <li>Type: <strong>Moving with {config.movementBehavior} behavior</strong></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SingleMovingTag;