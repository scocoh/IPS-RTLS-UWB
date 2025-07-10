/* Name: MapPathSimulator.js */
/* Version: 0.1.0 */
/* Created: 971201 */
/* Modified: 250502 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: ParcoRTLS frontend script */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/SimulatorDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// MapPathSimulator.js
// Version: 0.5.6 - Added dropdown to select paths from database by zoneId

import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const API_BASE_URL = `http://${window.location.hostname || 'localhost'}:8000`;

const getTodayYYMMDD = () => {
  const now = new Date();
  const yy = String(now.getFullYear()).slice(-2);
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const dd = String(now.getDate()).padStart(2, '0');
  return `${yy}${mm}${dd}`;
};

const MapPathSimulator = ({ onConfigChange, disabled, zoneId }) => {
  const mapRef = useRef(null);
  const [pathPoints, setPathPoints] = useState([]);
  const [mapData, setMapData] = useState(null);
  const [tagId, setTagId] = useState('MAPTAG1');
  const [pingRate, setPingRate] = useState(0.25);
  const [pingRateDisplay, setPingRateDisplay] = useState('0.25');
  const [speedFps, setSpeedFps] = useState(5);
  const [speedFpsDisplay, setSpeedFpsDisplay] = useState('5');
  const [totalDistance, setTotalDistance] = useState(0);
  const [direction, setDirection] = useState('forward');
  const [dwellSecs, setDwellSecs] = useState(0);
  const [pathList, setPathList] = useState([]);
  const [selectedPathId, setSelectedPathId] = useState(null);

  useEffect(() => {
    if (!zoneId || disabled) return;
    fetch(`/maps/get_map_data/${zoneId}`)
      .then(res => res.json())
      .then(data => setMapData(data))
      .catch(console.error);
  }, [zoneId, disabled]);

  useEffect(() => {
    if (!mapData) return;

    if (mapRef.current) {
      mapRef.current.remove();
      mapRef.current = null;
    }

    const map = L.map('map-path-container', {
      crs: L.CRS.Simple,
      minZoom: -2,
      maxZoom: 4,
    });
    mapRef.current = map;

    const bounds = L.latLngBounds(mapData.bounds);
    L.imageOverlay(mapData.imageUrl, bounds).addTo(map);
    map.fitBounds(bounds);

    map.on('click', (e) => {
      if (disabled) return;
      const { lat, lng } = e.latlng;
      const newPoint = { x: parseFloat(lng.toFixed(2)), y: parseFloat(lat.toFixed(2)), z: 1.0 };
      setPathPoints(prev => [...prev, newPoint]);
    });
  }, [mapData, disabled]);

  useEffect(() => {
    if (!mapRef.current) return;

    mapRef.current.eachLayer(layer => {
      if (layer instanceof L.Marker || layer instanceof L.Polyline) {
        mapRef.current.removeLayer(layer);
      }
    });

    let distance = 0;
    for (let i = 0; i < pathPoints.length - 1; i++) {
      const a = pathPoints[i];
      const b = pathPoints[i + 1];
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      distance += Math.sqrt(dx * dx + dy * dy);
    }
    setTotalDistance(distance);

    for (let i = 0; i < pathPoints.length; i++) {
      const pt = pathPoints[i];
      const latlng = [pt.y, pt.x];

      const color = i === 0 ? 'green' : (i === pathPoints.length - 1 ? 'red' : 'blue');
      const label = (i + 1).toString();

      const icon = L.divIcon({
        className: 'map-label-icon',
        html: `<div style="background:${color};border-radius:50%;width:16px;height:16px;line-height:16px;text-align:center;font-size:10px;color:white;">${label}</div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
      });

      L.marker(latlng, { icon })
        .bindTooltip(`X: ${pt.x}, Y: ${pt.y}`, { permanent: false, direction: 'top' })
        .addTo(mapRef.current);

      if (i > 0) {
        const prev = pathPoints[i - 1];
        L.polyline([[prev.y, prev.x], [pt.y, pt.x]], {
          color: 'red',
          dashArray: '5, 5',
          weight: 2
        }).addTo(mapRef.current);
      }
    }
  }, [pathPoints, disabled]);

  useEffect(() => {
    if (pathPoints.length < 2) return;
    onConfigChange([
      {
        tagId,
        positions: pathPoints,
        pingRate,
        speedFps,
        sequenceNumber: 1
      }
    ]);
  }, [pathPoints, tagId, pingRate, speedFps, onConfigChange]);

  useEffect(() => {
    if (!zoneId || disabled) return;
    fetch(`${API_BASE_URL}/simulator/list_paths?i_zn=${zoneId}`)
      .then(res => res.json())
      .then(data => {
        setPathList(data);
        if (data.length > 0 && !selectedPathId) setSelectedPathId(data[0].i_path);
      })
      .catch(err => alert(`Failed to fetch path list: ${err.message || err}`));
  }, [zoneId, disabled, selectedPathId]);

  const clearPath = () => {
    setPathPoints([]);
    if (mapRef.current) {
      mapRef.current.eachLayer(layer => {
        if (layer instanceof L.Marker || layer instanceof L.Polyline) {
          mapRef.current.removeLayer(layer);
        }
      });
    }
  };

  const savePathAsJSON = () => {
    if (pathPoints.length < 2) return alert("You must define at least two path points.");

    const x_nm_path = prompt("Enter path name (x_nm_path):", `Path_${getTodayYYMMDD()}`);
    if (!x_nm_path) return;

    const payload = {
      x_nm_path,
      created: getTodayYYMMDD(),
      tag_id: tagId,
      i_zn: zoneId,
      ping_rate: pingRate,
      speed_fps: speedFps,
      direction,
      dwell_secs: dwellSecs,
      positions: pathPoints
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${x_nm_path}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const savePathToDatabase = async () => {
    if (pathPoints.length < 2) return alert("You must define at least two path points.");
    if (!zoneId) return alert("Zone ID is missing.");

    const x_nm_path = prompt("Enter path name (x_nm_path):", `Path_${getTodayYYMMDD()}`);
    if (!x_nm_path) return;

    const payload = {
      x_nm_path,
      tag_id: tagId,
      i_zn: zoneId,
      ping_rate: pingRate,
      speed_fps: speedFps,
      direction,
      dwell_secs: dwellSecs,
      positions: pathPoints
    };

    try {
      const res = await fetch(`${API_BASE_URL}/simulator/save_path`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        alert(`Path "${x_nm_path}" saved to database.`);
      } else {
        const err = await res.json();
        alert(`Failed to save path: ${err.detail || res.statusText}`);
      }
    } catch (err) {
      alert(`Error saving path: ${err.message || err}`);
    }
  };

  const loadPathFromJSON = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result);
        if (!json.positions || !Array.isArray(json.positions) || json.positions.length < 2) {
          return alert("Invalid or incomplete path file.");
        }

        setTagId(json.tag_id || 'MAPTAG1');
        setPingRate(json.ping_rate || 0.25);
        setPingRateDisplay((json.ping_rate || 0.25).toString());
        setSpeedFps(json.speed_fps || 5);
        setSpeedFpsDisplay((json.speed_fps || 5).toString());
        setDirection(json.direction || 'forward');
        setDwellSecs(json.dwell_secs || 0);
        setPathPoints(json.positions);

        alert(`Path "${json.x_nm_path}" loaded.`);
      } catch (err) {
        alert("Failed to parse JSON file.");
      }
    };
    reader.readAsText(file);
  };

  const loadPathFromDatabase = async () => {
    if (!selectedPathId) return alert("Please select a path from the dropdown.");

    try {
      const res = await fetch(`${API_BASE_URL}/simulator/get_path/${selectedPathId}`);
      if (!res.ok) {
        const err = await res.json();
        return alert(`Failed to load path: ${err.detail || res.statusText}`);
      }

      const data = await res.json();
      setTagId(data.tag_id || 'MAPTAG1');
      setPingRate(data.ping_rate || 0.25);
      setPingRateDisplay((data.ping_rate || 0.25).toString());
      setSpeedFps(data.speed_fps || 5);
      setSpeedFpsDisplay((data.speed_fps || 5).toString());
      setDirection(data.direction || 'forward');
      setDwellSecs(data.dwell_secs || 0);
      setPathPoints(data.positions);

      alert(`Path "${data.x_nm_path}" loaded from database.`);
    } catch (err) {
      alert(`Error loading path: ${err.message || err}`);
    }
  };

  const etaSeconds = speedFps > 0 ? (totalDistance / speedFps) : 0;

  return (
    <div className="mode-component">
      <h3>Map Path Simulator</h3>
      <p className="mode-description">
        Click on the map to define a path for the simulated tag to follow.
      </p>

      <div className="form-row">
        <div className="form-group">
          <label title="Unique ID to identify this simulated tag.">Tag ID:</label>
          <input type="text" value={tagId} onChange={(e) => setTagId(e.target.value)} disabled={disabled} />
        </div>
        <div className="form-group">
          <label title="Number of position reports per second.">Ping Rate (Hz):</label>
          <input type="text" value={pingRateDisplay} onChange={(e) => setPingRateDisplay(e.target.value)} onBlur={() => {
            const val = parseFloat(pingRateDisplay);
            if (!isNaN(val) && val > 0) setPingRate(val);
            else setPingRateDisplay(pingRate.toString());
          }} disabled={disabled} />
        </div>
        <div className="form-group">
          <label title="Speed the tag should move in feet per second.">Speed (ft/s):</label>
          <input type="text" value={speedFpsDisplay} onChange={(e) => setSpeedFpsDisplay(e.target.value)} onBlur={() => {
            const val = parseFloat(speedFpsDisplay);
            if (!isNaN(val) && val > 0) setSpeedFps(val);
            else setSpeedFpsDisplay(speedFps.toString());
          }} disabled={disabled} />
        </div>
        <div className="form-group">
          <label title="Should the tag move forward through the path or ping-pong back and forth?">Direction:</label>
          <select value={direction} onChange={(e) => setDirection(e.target.value)} disabled={disabled}>
            <option value="forward">Forward</option>
            <option value="pingpong">Ping-Pong</option>
          </select>
        </div>
        <div className="form-group">
          <label title="Optional pause time in seconds at each path point.">Dwell Time (s):</label>
          <input type="number" value={dwellSecs} onChange={(e) => setDwellSecs(parseFloat(e.target.value))} disabled={disabled} />
        </div>
      </div>

      <p style={{ fontSize: '14px', color: 'gray', marginTop: '10px' }}>
        Total Distance: {totalDistance.toFixed(2)} ft — ETA: {etaSeconds.toFixed(2)} sec @ {speedFps} ft/s
      </p>

      <div id="map-path-container" style={{ height: '500px', width: '100%', marginTop: '20px' }} />

      <div className="action-buttons">
        <select
          value={selectedPathId || ''}
          onChange={(e) => setSelectedPathId(e.target.value ? parseInt(e.target.value) : null)}
          disabled={disabled || pathList.length === 0}
          style={{ marginRight: '10px', padding: '5px' }}
        >
          <option value="">-- Select a Path --</option>
          {pathList.map(path => (
            <option key={path.i_path} value={path.i_path}>{path.x_nm_path} (ID: {path.i_path})</option>
          ))}
        </select>
        <button onClick={loadPathFromDatabase} disabled={disabled || !selectedPathId}>Load Path from Database</button>
        <button onClick={() => document.getElementById('json-file-input').click()} disabled={disabled}>
          Load Path from JSON
        </button>
        <input
          type="file"
          id="json-file-input"
          accept=".json"
          style={{ display: 'none' }}
          onChange={loadPathFromJSON}
        />
        <button onClick={clearPath} disabled={disabled}>Clear Path</button>
        <button onClick={savePathAsJSON} disabled={disabled || pathPoints.length < 2}>Save Path as JSON</button>
        <button onClick={savePathToDatabase} disabled={disabled || pathPoints.length < 2}>Save Path to Database</button>
      </div>
    </div>
  );
};

export default MapPathSimulator;