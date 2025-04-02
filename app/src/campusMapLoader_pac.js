// Version: 250307 src/TriggerDemo.js Version 0P.3B.003
//
// ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// Invented by Scott Cohen & Bertrand Dugal.
// Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
//
// Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';  // Use React Router v6
import { Tabs, Tab } from 'react-bootstrap';  // Use Bootstrap for tabs
import CreateTrigger from './components/CreateTrigger'; // Import the CreateTrigger component
import Map from './components/Map';  // Import the Map component

const TriggerDemo = () => {
  const [maps, setMaps] = useState([]); // Maps
  const [zones, setZones] = useState([]); // Zones
  const [triggerDirections, setTriggerDirections] = useState([]);  // Trigger Directions
  const [selectedZone, setSelectedZone] = useState(null); // Selected Zone
  const [selectedMap, setSelectedMap] = useState(null); // Selected Map
  const [triggerName, setTriggerName] = useState(''); // Trigger Name
  const [triggerDirection, setTriggerDirection] = useState(''); // Trigger Direction
  const [topElevation, setTopElevation] = useState(8); // Top Elevation
  const [bottomElevation, setBottomElevation] = useState(-1); // Bottom Elevation
  const [triggerColor, setTriggerColor] = useState('Red'); // Trigger Color
  const [eventList, setEventList] = useState([]); // Event List
  const [coordinates, setCoordinates] = useState(''); // Coordinates

  // Fetch Maps from Backend
  useEffect(() => {
    fetch('http://192.168.210.226:8000/maps/get_maps') // Use full URL
      .then((response) => response.json())
      .then((data) => setMaps(data))
      .catch((error) => console.error('Error fetching maps:', error));
  }, []);

  // Fetch Trigger Directions from Backend
  useEffect(() => {
    fetch('http://192.168.210.226:8000/api/list_trigger_directions')  // FastAPI endpoint for trigger directions
      .then((response) => response.json())
      .then((data) => setTriggerDirections(data))  // Set trigger directions to state
      .catch((error) => console.error('Error fetching trigger directions:', error));
  }, []);

  // Fetch Zones for Selected Map
  useEffect(() => {
    if (selectedMap) {
      const campusId = selectedMap.i_map;  // Assuming the map has an `i_map` field
      fetch(`http://192.168.210.226:8000/maps/get_campus_zones/${campusId}`)  // Full API URL for zones
        .then((response) => response.json())
        .then((data) => setZones(data))
        .catch((error) => console.error('Error fetching zones:', error));
    }
  }, [selectedMap]);

  // Handle Trigger Creation
  const handleCreateTrigger = () => {
    const newEvent = `${triggerName} created at ${coordinates} with ${triggerDirection} direction`;
    setEventList([...eventList, newEvent]);
  };

  // Handle Map Selection
  const handleMapSelect = (mapId) => {
    fetch(`http://192.168.210.226:8000/maps/get_map/${mapId}`)  // Use full API URL for map data
      .then((response) => response.json())
      .then((data) => setSelectedMap(data[0]))  // Assuming data is the map object
      .catch((error) => console.error('Error fetching map:', error));
  };

  // Handle Zone Selection
  const handleZoneSelect = (zoneId) => {
    setSelectedZone(zoneId);
  };

  return (
    <div>
      <h1>ParcoRTLS Trigger Management</h1>

      <Tabs defaultActiveKey="mapAndTrigger" id="trigger-demo-tabs">
        <Tab eventKey="mapAndTrigger" title="Map & Trigger">
          <div className="trigger-map-section">
            {/* Trigger Configuration Form */}
            <div className="trigger-form">
              <h3>Create Trigger</h3>
              <input
                type="text"
                placeholder="Trigger Name"
                value={triggerName}
                onChange={(e) => setTriggerName(e.target.value)}
              />

              {/* Trigger Direction Dropdown */}
              <select onChange={(e) => setTriggerDirection(e.target.value)} value={triggerDirection}>
                <option value="">Select Direction</option>
                {triggerDirections.map((direction) => (
                  <option key={direction.i_dir} value={direction.x_dir}>
                    {direction.x_dir}
                  </option>
                ))}
              </select>

              <input
                type="number"
                placeholder="Top Elevation"
                value={topElevation}
                onChange={(e) => setTopElevation(Number(e.target.value))}
              />
              <input
                type="number"
                placeholder="Bottom Elevation"
                value={bottomElevation}
                onChange={(e) => setBottomElevation(Number(e.target.value))}
              />
              <select onChange={(e) => setTriggerColor(e.target.value)} value={triggerColor}>
                <option value="Red">Red</option>
                <option value="Blue">Blue</option>
                <option value="Green">Green</option>
              </select>
              <button onClick={handleCreateTrigger}>Create Trigger</button>
            </div>

            {/* Map and Zone Selection */}
            <div className="map-selection">
              <h3>Select a Map</h3>
              <select onChange={(e) => handleMapSelect(e.target.value)} value={selectedMap ? selectedMap.i_map : ''}>
                <option value="">Select Map</option>
                {maps.map((map) => (
                  <option key={map.i_map} value={map.i_map}>
                    {map.x_nm_map}  {/* Display map name */}
                  </option>
                ))}
              </select>

              {selectedMap && (
                <div>
                  <h3>Select a Zone</h3>
                  <select onChange={(e) => handleZoneSelect(e.target.value)} value={selectedZone}>
                    <option value="">Select Zone</option>
                    {zones.map((zone) => (
                      <option key={zone.i_zn} value={zone.i_zn}>
                        {zone.x_nm_zn}  {/* Display zone name */}
                      </option>
                    ))}
                  </select>

                  <div id="zoneCanvasContainer">
                    {/* The canvas for drawing zones and vertices */}
                    <canvas id="zoneCanvas" width="800" height="600"></canvas>
                  </div>

                  {/* Load Zones and Vertices */}
                  <button onClick={() => renderZones(zones)}>Load Zones</button>
                </div>
              )}
            </div>
          </div>
        </Tab>
      </Tabs>
    </div>
  );
};

export default TriggerDemo;
