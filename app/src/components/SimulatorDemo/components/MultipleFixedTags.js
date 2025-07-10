/* Name: MultipleFixedTags.js */
/* Version: 0.1.1 */
/* Created: 250708 */
/* Modified: 250708 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Multiple fixed tags simulation mode component - fixed ping rate input */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/SimulatorDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from 'react';

const MultipleFixedTags = ({ onConfigChange, disabled }) => {
  const [tags, setTags] = useState([
    {
      tagId: 'SIM3',
      position: { x: 5, y: 5, z: 5 },
      pingRate: 0.25,
      pingRateDisplay: '0.25'
    },
    {
      tagId: 'SIM4',
      position: { x: 15, y: 5, z: 5 },
      pingRate: 0.25,
      pingRateDisplay: '0.25'
    }
  ]);

  // Update parent when config changes
  useEffect(() => {
    const tagConfigs = tags.map(tag => ({
      tagId: tag.tagId,
      positions: [tag.position],
      pingRate: tag.pingRate,
      moveInterval: 0,
      sequenceNumber: 1
    }));
    onConfigChange(tagConfigs);
  }, [tags, onConfigChange]);

  const updateTag = (index, field, value) => {
    setTags(prev => prev.map((tag, i) => 
      i === index ? { ...tag, [field]: value } : tag
    ));
  };

  const updateTagPosition = (tagIndex, axis, value) => {
    setTags(prev => prev.map((tag, i) => 
      i === tagIndex 
        ? { ...tag, position: { ...tag.position, [axis]: parseFloat(value) || 0 } }
        : tag
    ));
  };

  const handlePingRateChange = (tagIndex, value) => {
    setTags(prev => prev.map((tag, i) => {
      if (i === tagIndex) {
        const numValue = parseFloat(value);
        return {
          ...tag,
          pingRateDisplay: value,
          pingRate: !isNaN(numValue) && numValue > 0 ? numValue : tag.pingRate
        };
      }
      return tag;
    }));
  };

  const handlePingRateBlur = (tagIndex) => {
    setTags(prev => prev.map((tag, i) => {
      if (i === tagIndex) {
        const numValue = parseFloat(tag.pingRateDisplay);
        if (isNaN(numValue) || numValue <= 0) {
          return {
            ...tag,
            pingRateDisplay: '0.25',
            pingRate: 0.25
          };
        }
      }
      return tag;
    }));
  };

  const addTag = () => {
    const newTagId = `SIM${tags.length + 3}`;
    const newTag = {
      tagId: newTagId,
      position: { x: 5 + (tags.length * 10), y: 5, z: 5 },
      pingRate: 0.25,
      pingRateDisplay: '0.25'
    };
    setTags(prev => [...prev, newTag]);
  };

  const removeTag = (index) => {
    if (tags.length > 1) {
      setTags(prev => prev.filter((_, i) => i !== index));
    }
  };

  const applyToAll = (field, value) => {
    if (field === 'pingRate') {
      const numValue = parseFloat(value);
      if (!isNaN(numValue) && numValue > 0) {
        setTags(prev => prev.map(tag => ({
          ...tag,
          pingRate: numValue,
          pingRateDisplay: value
        })));
      }
    } else {
      setTags(prev => prev.map(tag => ({
        ...tag,
        [field]: value
      })));
    }
  };

  return (
    <div className="mode-component">
      <h3>Multiple Fixed Tags Configuration</h3>
      <p className="mode-description">
        Simulates multiple tags at different fixed positions. Each tag can have its own ping rate.
        Useful for testing multi-tag scenarios and system performance.
      </p>

      <div className="config-section">
        <div className="bulk-actions">
          <h4>Bulk Actions</h4>
          <div className="bulk-controls">
            <div className="bulk-control">
              <label>Set all ping rates:</label>
              <div className="bulk-input-group">
                <input
                  type="text"
                  inputMode="decimal"
                  pattern="^\\d*\\.?\\d*$"
                  placeholder="0.25"
                  disabled={disabled}
                  id="bulk-ping-rate"
                />
                <button
                  onClick={() => {
                    const value = document.getElementById('bulk-ping-rate').value;
                    if (value) applyToAll('pingRate', value);
                  }}
                  disabled={disabled}
                  className="apply-btn"
                >
                  Apply
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="tags-section">
          <div className="tags-header">
            <h4>Tags ({tags.length})</h4>
            <button
              onClick={addTag}
              disabled={disabled || tags.length >= 10}
              className="add-tag-btn"
            >
              Add Tag
            </button>
          </div>

          {tags.map((tag, index) => (
            <div key={index} className="tag-config">
              <div className="tag-header">
                <h5>Tag {index + 1}</h5>
                {tags.length > 1 && (
                  <button
                    onClick={() => removeTag(index)}
                    disabled={disabled}
                    className="remove-tag-btn"
                  >
                    Remove
                  </button>
                )}
              </div>

              <div className="tag-controls">
                <div className="form-group">
                  <label>Tag ID:</label>
                  <input
                    type="text"
                    value={tag.tagId}
                    onChange={(e) => updateTag(index, 'tagId', e.target.value)}
                    disabled={disabled}
                    placeholder={`SIM${index + 3}`}
                  />
                </div>

                <div className="form-group">
                  <label>Ping Rate (Hz):</label>
                  <input
                    type="text"
                    inputMode="decimal"
                    pattern="^\\d*\\.?\\d*$"
                    value={tag.pingRateDisplay}
                    onChange={(e) => handlePingRateChange(index, e.target.value)}
                    onBlur={() => handlePingRateBlur(index)}
                    disabled={disabled}
                    placeholder="0.25"
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
                      value={tag.position.x}
                      onChange={(e) => updateTagPosition(index, 'x', e.target.value)}
                      disabled={disabled}
                    />
                  </div>
                  <div className="position-input">
                    <label>Y:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={tag.position.y}
                      onChange={(e) => updateTagPosition(index, 'y', e.target.value)}
                      disabled={disabled}
                    />
                  </div>
                  <div className="position-input">
                    <label>Z:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={tag.position.z}
                      onChange={(e) => updateTagPosition(index, 'z', e.target.value)}
                      disabled={disabled}
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="config-summary">
          <h4>Configuration Summary</h4>
          <ul>
            <li>Total Tags: <strong>{tags.length}</strong></li>
            <li>Tag IDs: <strong>{tags.map(t => t.tagId).join(', ')}</strong></li>
            <li>Ping Rates: <strong>{[...new Set(tags.map(t => t.pingRate))].join(', ')} Hz</strong></li>
            <li>Average Interval: <strong>{(tags.reduce((sum, t) => sum + (1/t.pingRate), 0) / tags.length).toFixed(2)}s</strong></li>
            <li>Total Messages/sec: <strong>{tags.reduce((sum, t) => sum + t.pingRate, 0).toFixed(2)}</strong></li>
            <li>Type: <strong>Multiple Stationary</strong></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default MultipleFixedTags;