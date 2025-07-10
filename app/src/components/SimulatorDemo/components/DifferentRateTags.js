/* Name: DifferentRateTags.js */
/* Version: 0.1.1 */
/* Created: 250708 */
/* Modified: 250708 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Different rate tags simulation mode component - fixed ping rate input */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/SimulatorDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from 'react';

const DifferentRateTags = ({ onConfigChange, disabled }) => {
  const [config, setConfig] = useState({
    tag1: {
      tagId: 'SIM3',
      position: { x: 5, y: 5, z: 5 },
      pingRate: 0.25,
      pingRateDisplay: '0.25'
    },
    tag2: {
      tagId: 'SIM4',
      position: { x: 5, y: 5, z: 5 },
      pingRate: 0.5,
      pingRateDisplay: '0.5'
    }
  });

  // Update parent when config changes
  useEffect(() => {
    const tagConfigs = [
      {
        tagId: config.tag1.tagId,
        positions: [config.tag1.position],
        pingRate: config.tag1.pingRate,
        moveInterval: 0,
        sequenceNumber: 1
      },
      {
        tagId: config.tag2.tagId,
        positions: [config.tag2.position],
        pingRate: config.tag2.pingRate,
        moveInterval: 0,
        sequenceNumber: 1
      }
    ];
    onConfigChange(tagConfigs);
  }, [config, onConfigChange]);

  const updateTag = (tagKey, field, value) => {
    setConfig(prev => ({
      ...prev,
      [tagKey]: {
        ...prev[tagKey],
        [field]: value
      }
    }));
  };

  const updateTagPosition = (tagKey, axis, value) => {
    setConfig(prev => ({
      ...prev,
      [tagKey]: {
        ...prev[tagKey],
        position: {
          ...prev[tagKey].position,
          [axis]: parseFloat(value) || 0
        }
      }
    }));
  };

  const handlePingRateChange = (tagKey, value) => {
    setConfig(prev => ({
      ...prev,
      [tagKey]: {
        ...prev[tagKey],
        pingRateDisplay: value,
        pingRate: !isNaN(parseFloat(value)) && parseFloat(value) > 0 ? parseFloat(value) : prev[tagKey].pingRate
      }
    }));
  };

  const handlePingRateBlur = (tagKey) => {
    setConfig(prev => {
      const numValue = parseFloat(prev[tagKey].pingRateDisplay);
      if (isNaN(numValue) || numValue <= 0) {
        return {
          ...prev,
          [tagKey]: {
            ...prev[tagKey],
            pingRateDisplay: '0.25',
            pingRate: 0.25
          }
        };
      }
      return prev;
    });
  };

  const copyPosition = (fromTag, toTag) => {
    setConfig(prev => ({
      ...prev,
      [toTag]: {
        ...prev[toTag],
        position: { ...prev[fromTag].position }
      }
    }));
  };

  const generatePresets = () => {
    return {
      sameLocation: () => {
        const position = { x: 5, y: 5, z: 5 };
        setConfig(prev => ({
          tag1: { ...prev.tag1, position: { ...position }, pingRate: 0.25, pingRateDisplay: '0.25' },
          tag2: { ...prev.tag2, position: { ...position }, pingRate: 0.5, pingRateDisplay: '0.5' }
        }));
      },
      differentLocations: () => {
        setConfig(prev => ({
          tag1: { ...prev.tag1, position: { x: 5, y: 5, z: 5 }, pingRate: 0.25, pingRateDisplay: '0.25' },
          tag2: { ...prev.tag2, position: { x: 15, y: 15, z: 5 }, pingRate: 0.5, pingRateDisplay: '0.5' }
        }));
      },
      highFrequency: () => {
        setConfig(prev => ({
          tag1: { ...prev.tag1, pingRate: 1.0, pingRateDisplay: '1.0' },
          tag2: { ...prev.tag2, pingRate: 2.0, pingRateDisplay: '2.0' }
        }));
      },
      lowFrequency: () => {
        setConfig(prev => ({
          tag1: { ...prev.tag1, pingRate: 0.1, pingRateDisplay: '0.1' },
          tag2: { ...prev.tag2, pingRate: 0.05, pingRateDisplay: '0.05' }
        }));
      }
    };
  };

  const presets = generatePresets();

  return (
    <div className="mode-component">
      <h3>Different Rate Tags Configuration</h3>
      <p className="mode-description">
        Simulates two tags with different ping rates at the same or different locations.
        Useful for testing system performance with mixed update frequencies.
      </p>

      <div className="config-section">
        {/* Presets */}
        <div className="presets-section">
          <h4>Quick Presets</h4>
          <div className="preset-buttons">
            <button onClick={presets.sameLocation} disabled={disabled} className="preset-btn">
              Same Location
            </button>
            <button onClick={presets.differentLocations} disabled={disabled} className="preset-btn">
              Different Locations
            </button>
            <button onClick={presets.highFrequency} disabled={disabled} className="preset-btn">
              High Frequency
            </button>
            <button onClick={presets.lowFrequency} disabled={disabled} className="preset-btn">
              Low Frequency
            </button>
          </div>
        </div>

        {/* Tag 1 Configuration */}
        <div className="tag-group">
          <h4>Tag 1 (Lower Rate)</h4>
          <div className="tag-config">
            <div className="form-row">
              <div className="form-group">
                <label>Tag ID:</label>
                <input
                  type="text"
                  value={config.tag1.tagId}
                  onChange={(e) => updateTag('tag1', 'tagId', e.target.value)}
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
                  value={config.tag1.pingRateDisplay}
                  onChange={(e) => handlePingRateChange('tag1', e.target.value)}
                  onBlur={() => handlePingRateBlur('tag1')}
                  disabled={disabled}
                  placeholder="0.25"
                />
                <small>Interval: {(1/config.tag1.pingRate).toFixed(2)}s</small>
              </div>
            </div>

            <div className="position-section">
              <div className="position-header">
                <label>Position:</label>
                <button 
                  onClick={() => copyPosition('tag1', 'tag2')} 
                  disabled={disabled}
                  className="copy-btn"
                >
                  Copy to Tag 2
                </button>
              </div>
              <div className="position-inputs">
                <div className="position-input">
                  <label>X:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.tag1.position.x}
                    onChange={(e) => updateTagPosition('tag1', 'x', e.target.value)}
                    disabled={disabled}
                  />
                </div>
                <div className="position-input">
                  <label>Y:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.tag1.position.y}
                    onChange={(e) => updateTagPosition('tag1', 'y', e.target.value)}
                    disabled={disabled}
                  />
                </div>
                <div className="position-input">
                  <label>Z:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.tag1.position.z}
                    onChange={(e) => updateTagPosition('tag1', 'z', e.target.value)}
                    disabled={disabled}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tag 2 Configuration */}
        <div className="tag-group">
          <h4>Tag 2 (Higher Rate)</h4>
          <div className="tag-config">
            <div className="form-row">
              <div className="form-group">
                <label>Tag ID:</label>
                <input
                  type="text"
                  value={config.tag2.tagId}
                  onChange={(e) => updateTag('tag2', 'tagId', e.target.value)}
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
                  value={config.tag2.pingRateDisplay}
                  onChange={(e) => handlePingRateChange('tag2', e.target.value)}
                  onBlur={() => handlePingRateBlur('tag2')}
                  disabled={disabled}
                  placeholder="0.5"
                />
                <small>Interval: {(1/config.tag2.pingRate).toFixed(2)}s</small>
              </div>
            </div>

            <div className="position-section">
              <div className="position-header">
                <label>Position:</label>
                <button 
                  onClick={() => copyPosition('tag2', 'tag1')} 
                  disabled={disabled}
                  className="copy-btn"
                >
                  Copy to Tag 1
                </button>
              </div>
              <div className="position-inputs">
                <div className="position-input">
                  <label>X:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.tag2.position.x}
                    onChange={(e) => updateTagPosition('tag2', 'x', e.target.value)}
                    disabled={disabled}
                  />
                </div>
                <div className="position-input">
                  <label>Y:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.tag2.position.y}
                    onChange={(e) => updateTagPosition('tag2', 'y', e.target.value)}
                    disabled={disabled}
                  />
                </div>
                <div className="position-input">
                  <label>Z:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.tag2.position.z}
                    onChange={(e) => updateTagPosition('tag2', 'z', e.target.value)}
                    disabled={disabled}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="config-summary">
          <h4>Configuration Summary</h4>
          <ul>
            <li>Tag 1: <strong>{config.tag1.tagId}</strong> at {config.tag1.pingRate}Hz ({(1/config.tag1.pingRate).toFixed(2)}s interval)</li>
            <li>Tag 2: <strong>{config.tag2.tagId}</strong> at {config.tag2.pingRate}Hz ({(1/config.tag2.pingRate).toFixed(2)}s interval)</li>
            <li>Rate Ratio: <strong>1:{(config.tag2.pingRate/config.tag1.pingRate).toFixed(1)}</strong></li>
            <li>Total Messages/sec: <strong>{(config.tag1.pingRate + config.tag2.pingRate).toFixed(2)}</strong></li>
            <li>Same Location: <strong>{JSON.stringify(config.tag1.position) === JSON.stringify(config.tag2.position) ? 'Yes' : 'No'}</strong></li>
            <li>Type: <strong>Different Rate Stationary</strong></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default DifferentRateTags;