/* Name: ConnectionPanel.js */
/* Version: 0.1.0 */
/* Created: 250707 */
/* Modified: 250707 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Connection and control panel component for SimulatorDemo */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/SimulatorDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

const ConnectionPanel = ({
  isConnected,
  isRunning,
  onConnect,
  onDisconnect,
  onStart,
  onStop,
  error
}) => {
  return (
    <div className="connection-panel">
      <h3>Connection & Control</h3>
      
      {/* Connection Status */}
      <div className="connection-status-detail">
        <div className="status-indicator-row">
          <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
          <span>WebSocket: {isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
        <div className="status-indicator-row">
          <span className={`status-dot ${isRunning ? 'running' : 'stopped'}`}></span>
          <span>Simulation: {isRunning ? 'Running' : 'Stopped'}</span>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Control Buttons */}
      <div className="control-buttons">
        <button
          onClick={onConnect}
          disabled={isConnected || isRunning}
          className="connect-btn"
        >
          Connect WebSocket
        </button>

        <button
          onClick={onDisconnect}
          disabled={!isConnected}
          className="disconnect-btn"
        >
          Disconnect
        </button>

        <button
          onClick={onStart}
          disabled={!isConnected || isRunning}
          className="start-btn"
        >
          Start Simulation
        </button>

        <button
          onClick={onStop}
          disabled={!isRunning}
          className="stop-btn"
        >
          Stop Simulation
        </button>
      </div>

      {/* Connection Info */}
      <div className="connection-info">
        <h4>Connection Details</h4>
        <div className="info-item">
          <strong>Control Port:</strong> 8001
        </div>
        <div className="info-item">
          <strong>Stream Port:</strong> 8002 (auto-redirect)
        </div>
        <div className="info-item">
          <strong>Protocol:</strong> WebSocket
        </div>
        <div className="info-item">
          <strong>Message Format:</strong> GISData
        </div>
      </div>

      {/* Instructions */}
      <div className="instructions">
        <h4>Instructions</h4>
        <ol>
          <li>Configure your simulation mode settings</li>
          <li>Click "Connect WebSocket" to establish connection</li>
          <li>Click "Start Simulation" to begin sending data</li>
          <li>Monitor the event log for real-time feedback</li>
          <li>Click "Stop Simulation" to end data transmission</li>
        </ol>
      </div>
    </div>
  );
};

export default ConnectionPanel;