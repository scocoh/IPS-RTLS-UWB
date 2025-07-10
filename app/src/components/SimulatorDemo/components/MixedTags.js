/* Name: MixedTags.js */
/* Version: 0.1.2 */
/* Created: 250708 */
/* Modified: 250708 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Mixed tags simulation mode component (one stationary, one moving) - fixed ping rate input, move interval synced */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/SimulatorDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from 'react';

const MixedTags = ({ onConfigChange, disabled }) => {
  const [config, setConfig] = useState({
    stationaryTag: {
      tagId: 'SIM3',
      position: { x: 105, y: 140, z: 5 },
      pingRate: 0.1,
      pingRateDisplay: '0.1'
    },
    movingTag: {
      tagId: 'SIM4',
      positions: [
        { x: 114, y: 126, z: 5 },  // Inside region
        { x: 105, y: 140, z: 1 }   // Outside region
      ],
      pingRate: 0.1,
      pingRateDisplay: '0.1',
      moveInterval: 0.1,
      moveIntervalDisplay: '0.1'
    }
  });

  // Update parent when config changes
  useEffect(() => {
    const tagConfigs = [
      // Stationary tag
      {
        tagId: config.stationaryTag.tagId,
        positions: [config.stationaryTag.position],
        pingRate: config.stationaryTag.pingRate,
        moveInterval: 0,
        sequenceNumber: 1
      },
      // Moving tag
      {
        tagId: config.movingTag.tagId,
        positions: config.movingTag.positions,
        pingRate: config.movingTag.pingRate,
        moveInterval: config.movingTag.moveInterval,
        sequenceNumber: 1
      }
    ];
    onConfigChange(tagConfigs);
  }, [config, onConfigChange]);

  const updateStationaryTag = (field, value) => {
    setConfig(prev => ({
      ...prev,
      stationaryTag: {
        ...prev.stationaryTag,
        [field]: value
      }
    }));
  };

  const updateStationaryPosition = (axis, value) => {
    setConfig(prev => ({
      ...prev,
      stationaryTag: {
        ...prev.stationaryTag,
        position: {
          ...prev.stationaryTag.position,
          [axis]: parseFloat(value) || 0
        }
      }
    }));
  };

  const updateMovingTag = (field, value) => {
    setConfig(prev => ({
      ...prev,
      movingTag: {
        ...prev.movingTag,
        [field]: value
      }
    }));
  };

  const updateMovingPosition = (posIndex, axis, value) => {
    setConfig(prev => ({
      ...prev,
      movingTag: {
        ...prev.movingTag,
        positions: prev.movingTag.positions.map((pos, index) => 
          index === posIndex 
            ? { ...pos, [axis]: parseFloat(value) || 0 }
            : pos
        )
      }
    }));
  };

  const handleStationaryPingRateChange = (value) => {
    setConfig(prev => ({
      ...prev,
      stationaryTag: {
        ...prev.stationaryTag,
        pingRateDisplay: value,
        pingRate: !isNaN(parseFloat(value)) && parseFloat(value) > 0 ? parseFloat(value) : prev.stationaryTag.pingRate
      }
    }));
  };

  const handleStationaryPingRateBlur = () => {
    setConfig(prev => {
      const numValue = parseFloat(prev.stationaryTag.pingRateDisplay);
      if (isNaN(numValue) || numValue <= 0) {
        return {
          ...prev,
          stationaryTag: {
            ...prev.stationaryTag,
            pingRateDisplay: '0.1',
            pingRate: 0.1
          }
        };
      }
      return prev;
    });
  };

  const handleMovingPingRateChange = (value) => {
    setConfig(prev => ({
      ...prev,
      movingTag: {
        ...prev.movingTag,
        pingRateDisplay: value,
        pingRate: !isNaN(parseFloat(value)) && parseFloat(value) > 0 ? parseFloat(value) : prev.movingTag.pingRate,
        moveInterval: !isNaN(parseFloat(value)) && parseFloat(value) > 0 ? parseFloat(value) : prev.movingTag.moveInterval,
        moveIntervalDisplay: value
      }
    }));
  };

  const handleMovingPingRateBlur = () => {
    setConfig(prev => {
      const numValue = parseFloat(prev.movingTag.pingRateDisplay);
      if (isNaN(numValue) || numValue <= 0) {
        return {
          ...prev,
          movingTag: {
            ...prev.movingTag,
            pingRateDisplay: '0.1',
            pingRate: 0.1,
            moveInterval: 0.1,
            moveIntervalDisplay: '0.1'
          }
        };
      }
      return prev;
    });
  };

  const handleMoveIntervalChange = (value) => {
    setConfig(prev => ({
      ...prev,
      movingTag: {
        ...prev.movingTag,
        moveIntervalDisplay: value,
        moveInterval: !isNaN(parseFloat(value)) && parseFloat(value) > 0 ? parseFloat(value) : prev.movingTag.moveInterval
      }
    }));
  };

  const handleMoveIntervalBlur = () => {
    setConfig(prev => {
      const numValue = parseFloat(prev.movingTag.moveIntervalDisplay);
      if (isNaN(numValue) || numValue <= 0) {
        return {
          ...prev,
          movingTag: {
            ...prev.movingTag,
            moveIntervalDisplay: '0.1',
            moveInterval: 0.1
          }
        };
      }
      return prev;
    });
  };

  return (
    <div className="mode-component">
      <h3>Mixed Tags Configuration</h3>
      <p className="mode-description">
        Simulates one stationary tag and one moving tag. This mode is useful for testing 
        scenarios where some assets are fixed (equipment) and others are mobile (personnel).
      </p>

      <div className="config-section">
        {/* Stationary Tag Configuration */}
        <div className="tag-group">
          <h4>Stationary Tag</h4>
          <div className="tag-config">
            <div className="form-row">
              <div className="form-group">
                <label>Tag ID:</label>
                <input
                  type="text"
                  value={config.stationaryTag.tagId}
                  onChange={(e) => updateStationaryTag('tagId', e.target.value)}
                  disabled={disabled}
                  placeholder="SIM3"
                />
              </div>
              
              <div className="form-group">
                <label>Ping Rate (Hz):</label>
                <input
                  type="text"
                  inputMode="decimal"
                  pattern="^\\d*\\.?\\d*$"
                  value={config.stationaryTag.pingRateDisplay}
                  onChange={(e) => handleStationaryPingRateChange(e.target.value)}
                  onBlur={handleStationaryPingRateBlur}
                  disabled={disabled}
                  placeholder="0.1"
                />
              </div>
            </div>

            <div className="position-section">
              <label>Position:</label>
              <div className="position-inputs">
                <div className="position-input">
                  <label>X:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.stationaryTag.position.x}
                    onChange={(e) => updateStationaryPosition('x', e.target.value)}
                    disabled={disabled}
                  />
                </div>
                <div className="position-input">
                  <label>Y:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.stationaryTag.position.y}
                    onChange={(e) => updateStationaryPosition('y', e.target.value)}
                    disabled={disabled}
                  />
                </div>
                <div className="position-input">
                  <label>Z:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.stationaryTag.position.z}
                    onChange={(e) => updateStationaryPosition('z', e.target.value)}
                    disabled={disabled}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Moving Tag Configuration */}
        <div className="tag-group">
          <h4>Moving Tag</h4>
          <div className="tag-config">
            <div className="form-row">
              <div className="form-group">
                <label>Tag ID:</label>
                <input
                  type="text"
                  value={config.movingTag.tagId}
                  onChange={(e) => updateMovingTag('tagId', e.target.value)}
                  disabled={disabled}
                  placeholder="SIM4"
                />
              </div>
              
              <div className="form-group">
                <label>Ping Rate (Hz):</label>
                <input
                  type="text"
                  inputMode="decimal"
                  pattern="^\\d*\\.?\\d*$"
                  value={config.movingTag.pingRateDisplay}
                  onChange={(e) => handleMovingPingRateChange(e.target.value)}
                  onBlur={handleMovingPingRateBlur}
                  disabled={disabled}
                  placeholder="0.1"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Move Interval (seconds):</label>
              <input
                type="text"
                inputMode="decimal"
                pattern="^\\d*\\.?\\d*$"
                value={config.movingTag.moveIntervalDisplay}
                onChange={(e) => handleMoveIntervalChange(e.target.value)}
                onBlur={handleMoveIntervalBlur}
                disabled={disabled}
                placeholder="0.1"
              />
              <small>Time to move between positions (synced with ping rate)</small>
            </div>

            <div className="position-section">
              <h5>Movement Positions</h5>
              {config.movingTag.positions.map((position, index) => (
                <div key={index} className="position-group">
                  <label>Position {index + 1} {index === 0 ? '(Start)' : '(End)'}:</label>
                  <div className="position-inputs">
                    <div className="position-input">
                      <label>X:</label>
                      <input
                        type="number"
                        step="0.1"
                        value={position.x}
                        onChange={(e) => updateMovingPosition(index, 'x', e.target.value)}
                        disabled={disabled}
                      />
                    </div>
                    <div className="position-input">
                      <label>Y:</label>
                      <input
                        type="number"
                        step="0.1"
                        value={position.y}
                        onChange={(e) => updateMovingPosition(index, 'y', e.target.value)}
                        disabled={disabled}
                      />
                    </div>
                    <div className="position-input">
                      <label>Z:</label>
                      <input
                        type="number"
                        step="0.1"
                        value={position.z}
                        onChange={(e) => updateMovingPosition(index, 'z', e.target.value)}
                        disabled={disabled}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="config-summary">
          <h4>Configuration Summary</h4>
          <ul>
            <li>Stationary Tag: <strong>{config.stationaryTag.tagId}</strong> at ({config.stationaryTag.position.x}, {config.stationaryTag.position.y}, {config.stationaryTag.position.z})</li>
            <li>Moving Tag: <strong>{config.movingTag.tagId}</strong> between positions</li>
            <li>Ping Rates: <strong>{config.stationaryTag.pingRate}Hz / {config.movingTag.pingRate}Hz</strong></li>
            <li>Move Cycle: <strong>{(config.movingTag.moveInterval * 2).toFixed(1)}s</strong></li>
            <li>Total Messages/sec: <strong>{(config.stationaryTag.pingRate + config.movingTag.pingRate).toFixed(2)}</strong></li>
            <li>Type: <strong>Mixed (1 stationary, 1 moving)</strong></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default MixedTags;