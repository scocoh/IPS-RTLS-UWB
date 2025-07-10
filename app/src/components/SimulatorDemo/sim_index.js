/* Name: sim_index.js */
/* Version: 0.4.0 */
/* Modified: 250708 */
/* Description: Uses speed (ft/s) to interpolate tag movement */

import React, { useState, useRef, useEffect } from 'react';
import useSimulatorWebSocket from './hooks/useSimulatorWebSocket';
import SingleFixedTag from './components/SingleFixedTag';
import SingleMovingTag from './components/SingleMovingTag';
import MultipleFixedTags from './components/MultipleFixedTags';
import DifferentRateTags from './components/DifferentRateTags';
import MixedTags from './components/MixedTags';
import TetseDebugMode from './components/TetseDebugMode';
import MapPathSimulator from './components/MapPathSimulator';
import ConnectionPanel from './components/ConnectionPanel';
import EventLogPanel from './components/EventLogPanel';
import { interpolatePath } from './utils/pathUtils';
import './styles/SimulatorDemo.css';

const SimulatorDemo = () => {
  const [currentMode, setCurrentMode] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [duration, setDuration] = useState(30);
  const [zoneId, setZoneId] = useState(417);
  const [availableZones, setAvailableZones] = useState([]);
  const [tagConfigs, setTagConfigs] = useState([]);
  const [eventLog, setEventLog] = useState([]);

  const isRunningRef = useRef(false);
  const simulationIntervals = useRef(new Map());

  const {
    isConnected,
    connectionStatus,
    error,
    connectControl,
    sendGISData,
    disconnect,
    setLogCallback
  } = useSimulatorWebSocket();

  useEffect(() => {
    setLogCallback(addLogEntry);
  }, [setLogCallback]);

  useEffect(() => {
    fetch(`${window.location.origin}/api/zone_list`)
      .then(res => res.json())
      .then(data => {
        const zones = Array.isArray(data)
          ? data.map(z => ({ id: z.i_zn, name: z.x_nm_zn }))
          : [];
        setAvailableZones(zones);
        if (zones.length && !zoneId) setZoneId(zones[0].id);
      })
      .catch(() => addLogEntry('Failed to load zone list from API'));
  }, []);

  const simulationModes = [
    { id: 1, name: "Single tag at fixed point", component: SingleFixedTag },
    { id: 2, name: "Single moving tag", component: SingleMovingTag },
    { id: 3, name: "Multiple fixed tags", component: MultipleFixedTags },
    { id: 4, name: "Different rate tags", component: DifferentRateTags },
    { id: 5, name: "Mixed stationary & moving tags", component: MixedTags },
    { id: 6, name: "TETSE Debug Mode", component: TetseDebugMode },
    { id: 7, name: "Interactive map path", component: MapPathSimulator }
  ];

  const addLogEntry = (message) => {
    const timestamp = new Date().toISOString();
    setEventLog(prev => [...prev.slice(-49), `${timestamp}: ${message}`]);
  };

  const startSimulation = async () => {
    if (!isConnected) return addLogEntry('Cannot start simulation - not connected');
    if (tagConfigs.length === 0) return addLogEntry('No tag configurations available');

    setIsRunning(true);
    isRunningRef.current = true;
    addLogEntry(`Starting simulation mode ${currentMode} for ${duration}s`);

    tagConfigs.forEach(config => startTagSimulation(config));
    setTimeout(stopSimulation, duration * 1000);
  };

  const stopSimulation = () => {
    setIsRunning(false);
    isRunningRef.current = false;
    addLogEntry('Stopping simulation');
    simulationIntervals.current.forEach((interval, tagId) => {
      clearInterval(interval);
      addLogEntry(`Stopped simulation for tag ${tagId}`);
    });
    simulationIntervals.current.clear();
  };

  const startTagSimulation = (config) => {
    const sleepInterval = 1000 / config.pingRate;
    let sequenceNumber = config.sequenceNumber || 1;
    const startTime = Date.now();

    const sendTagData = () => {
      if (!isRunningRef.current) return;

      const elapsed = (Date.now() - startTime) / 1000;
      const { x, y, z, debug } = interpolatePath(config.positions, elapsed, config.speedFps || 5.0);
      const position = { x, y, z };

      console.log(`[${config.tagId}] t=${debug.t} segment=${debug.segmentIndex} pos=(${x.toFixed(2)}, ${y.toFixed(2)}) dist=${debug.segDist} total=${debug.totalDistance} speed=${debug.speedFps}`);

      const message = {
        type: "GISData",
        ID: config.tagId,
        Type: "Sim",
        TS: new Date().toISOString(),
        X: x,
        Y: y,
        Z: z,
        Bat: 100,
        CNF: 95.0,
        GWID: "SIM-GW",
        Sequence: sequenceNumber,
        zone_id: zoneId
      };

      sendGISData(message) && addLogEntry(`${config.tagId}: (${x}, ${y}, ${z}) seq=${sequenceNumber}`);
      sequenceNumber = sequenceNumber >= 200 ? 1 : sequenceNumber + 1;
    };

    sendTagData();
    const intervalId = setInterval(sendTagData, sleepInterval);
    simulationIntervals.current.set(config.tagId, intervalId);
  };

  const handleConnect = async () => {
    try {
      await connectControl(tagConfigs, zoneId);
    } catch (err) {
      addLogEntry(`Connection failed: ${err.message}`);
    }
  };

  const handleDisconnect = async () => {
    await disconnect();
    stopSimulation();
  };

  const CurrentModeComponent = currentMode ? simulationModes.find(mode => mode.id === parseInt(currentMode))?.component : null;

  return (
    <div className="simulator-demo">
      <div className="simulator-header">
        <h2>ParcoRTLS Simulator (v0.4.0)</h2>
        <div className="connection-status">
          Status: <span className={isConnected ? 'connected' : 'disconnected'}>{connectionStatus}</span>
        </div>
      </div>

      <div className="simulator-layout">
        <div className="mode-selection">
          <h3>Simulation Mode</h3>
          <select value={currentMode} onChange={(e) => setCurrentMode(e.target.value)} disabled={isRunning}>
            <option value="">-- Select a Simulation Mode --</option>
            {simulationModes.map(mode => (
              <option key={mode.id} value={mode.id}>{mode.id}. {mode.name}</option>
            ))}
          </select>
        </div>

        <div className="global-settings">
          <h3>Global Settings</h3>
          <div className="settings-row">
            <div className="setting-group">
              <label>Duration (seconds):</label>
              <input type="number" value={duration} onChange={(e) => setDuration(parseInt(e.target.value))} disabled={isRunning} />
            </div>
            <div className="setting-group">
              <label>Zone:</label>
              <select value={zoneId} onChange={(e) => setZoneId(parseInt(e.target.value))} disabled={isRunning}>
                {availableZones.map(zone => (
                  <option key={zone.id} value={zone.id}>{zone.name || `Zone ${zone.id}`}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {CurrentModeComponent && (
          <CurrentModeComponent
            onConfigChange={setTagConfigs}
            disabled={isRunning}
            zoneId={zoneId}
            onZoneIdChange={setZoneId}
          />
        )}

        <div className="row config-and-log">
          <div className="config-summary">
            <div className="summary-box">
              <h3>Configuration Summary</h3>
              <ul>
                {tagConfigs.map((cfg, idx) => (
                  <li key={idx}><strong>{cfg.tagId}</strong> @ {cfg.positions[0].x}, {cfg.positions[0].y}, {cfg.positions[0].z} @ {cfg.pingRate}Hz, speed={cfg.speedFps || 5}ft/s</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="event-log-panel">
            <EventLogPanel eventLog={eventLog} onClear={() => setEventLog([])} />
          </div>
        </div>

        <div className="connection-panel">
          <ConnectionPanel
            isConnected={isConnected}
            isRunning={isRunning}
            onConnect={handleConnect}
            onDisconnect={handleDisconnect}
            onStart={startSimulation}
            onStop={stopSimulation}
            error={error}
          />
        </div>
      </div>
    </div>
  );
};

export default SimulatorDemo;
