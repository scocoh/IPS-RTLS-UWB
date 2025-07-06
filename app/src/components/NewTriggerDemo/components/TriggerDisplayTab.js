/* Name: TriggerDisplayTab.js */
/* Version: 0.1.1 */
/* Created: 250705 */
/* Modified: 250705 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Trigger display tab for NewTriggerDemo - Fixed map conflicts with unique key prop */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect, useRef } from "react";
import { FormCheck, ButtonGroup, Button } from "react-bootstrap";
import NewTriggerViewer from "../../NewTriggerViewer";
import { triggerApi } from "../services/triggerApi";
import { zoneApi } from "../services/zoneApi";

const TriggerDisplayTab = ({
  zones,
  selectedZone,
  triggers,
  tagsData,
  isConnected,
  triggerEvents,
  showTriggerEvents,
  setShowTriggerEvents,
  portableTriggerContainment
}) => {
  // Local state for display
  const [zoneVertices, setZoneVertices] = useState([]);
  const [showExistingTriggers, setShowExistingTriggers] = useState(true);
  const [existingTriggerPolygons, setExistingTriggerPolygons] = useState([]);
  const [eventFilter, setEventFilter] = useState('all');
  const retryIntervalRef = useRef(null);

  // Trigger styling for display
  const [triggerStyle, setTriggerStyle] = useState({
    staticFillOpacity: 25,
    staticLineOpacity: 80,
    portableFillOpacity: 40,
    portableLineOpacity: 90,
    staticColor: '#ff0000',
    portableColor: '#00ff00',
    vertexColor: '#0000ff'
  });

  // Update trigger styling
  const updateTriggerStyle = (property, value) => {
    setTriggerStyle(prev => ({
      ...prev,
      [property]: value
    }));
  };

  // Fetch zone vertices when zone changes
  useEffect(() => {
    if (selectedZone) {
      const fetchZoneVertices = async () => {
        try {
          const { vertices } = await zoneApi.fetchZoneVertices(selectedZone.i_zn);
          setZoneVertices(vertices);
        } catch (e) {
          console.error("Error fetching zone vertices:", e);
        }
      };
      fetchZoneVertices();
    }
  }, [selectedZone]);

  // Fetch trigger polygons
  useEffect(() => {
    if (!selectedZone) return;
    
    const zoneTriggers = triggers.filter(t => t.zone_id === parseInt(selectedZone.i_zn) || t.zone_id == null);
    
    const fetchPolygons = async () => {
      if (zoneTriggers.length === 0) {
        setExistingTriggerPolygons([]);
        return;
      }
      
      try {
        const polygons = await Promise.all(
          zoneTriggers.map(async (t) => {
            try {
              if (t.is_portable) {
                return { 
                  id: t.i_trg, 
                  name: t.x_nm_trg, 
                  isPortable: true, 
                  pending: true, 
                  assigned_tag_id: t.assigned_tag_id, 
                  radius_ft: t.radius_ft,
                  style: {
                    fillOpacity: triggerStyle.portableFillOpacity / 100,
                    lineOpacity: triggerStyle.portableLineOpacity / 100,
                    color: triggerStyle.portableColor
                  }
                };
              } else {
                const data = await triggerApi.getTriggerDetails(t.i_trg);
                if (Array.isArray(data.vertices)) {
                  const latLngs = data.vertices.map(v => [v.y, v.x]);
                  return { 
                    id: t.i_trg, 
                    name: t.x_nm_trg, 
                    latLngs, 
                    isPortable: false,
                    style: {
                      fillOpacity: triggerStyle.staticFillOpacity / 100,
                      lineOpacity: triggerStyle.staticLineOpacity / 100,
                      color: triggerStyle.staticColor
                    }
                  };
                }
                return null;
              }
            } catch (e) {
              console.error(`Failed to fetch details for trigger ${t.i_trg}:`, e);
              return null;
            }
          })
        );
        
        const validPolygons = polygons.filter(p => p);
        setExistingTriggerPolygons(validPolygons);
      } catch (e) {
        console.error("Failed to fetch polygons:", e);
      }
    };

    fetchPolygons();
  }, [selectedZone, triggers, triggerStyle]);

  // Update portable trigger polygons with live data
  useEffect(() => {
    if (!selectedZone || !triggers || !isConnected) return;

    const zoneTriggers = triggers.filter(t => t.zone_id === parseInt(selectedZone.i_zn) || t.zone_id == null);
    const portableTriggers = zoneTriggers.filter(t => t.is_portable);
    if (portableTriggers.length === 0) return;

    const updatePortablePolygons = () => {
      const updatedPolygons = portableTriggers.map(t => {
        const tagId = t.assigned_tag_id;
        const tagData = tagsData[tagId];
        if (!tagData) return null;
        
        return {
          id: t.i_trg,
          name: t.x_nm_trg,
          center: [tagData.y, tagData.x],
          radius: t.radius_ft,
          isPortable: true,
          assigned_tag_id: t.assigned_tag_id,
          radius_ft: t.radius_ft,
          style: {
            fillOpacity: triggerStyle.portableFillOpacity / 100,
            lineOpacity: triggerStyle.portableLineOpacity / 100,
            color: triggerStyle.portableColor
          }
        };
      });

      const validPortable = updatedPolygons.filter(p => p);
      if (validPortable.length > 0) {
        setExistingTriggerPolygons(prev => {
          const nonPortable = prev.filter(p => !p.isPortable || p.pending);
          return [...nonPortable, ...validPortable];
        });
      }
    };

    updatePortablePolygons();
    const interval = setInterval(updatePortablePolygons, 1000);
    return () => clearInterval(interval);
  }, [tagsData, selectedZone, triggers, isConnected, triggerStyle]);

  // Filter events based on selected filter
  const filteredEvents = triggerEvents.filter(event => {
    if (eventFilter === 'all') return true;
    if (eventFilter === 'enter') return event.toLowerCase().includes('enter');
    if (eventFilter === 'exit') return event.toLowerCase().includes('exit');
    if (eventFilter === 'portable') return event.toLowerCase().includes('within');
    return true;
  });

  return (
    <div>
      <h3>View Triggers & Events</h3>
      <p>View existing triggers on the map and monitor real-time trigger events.</p>

      {/* Trigger Styling Controls */}
      <div style={{ 
        marginBottom: "15px", 
        padding: "10px", 
        backgroundColor: "#f8f9fa", 
        borderRadius: "5px",
        border: "1px solid #dee2e6"
      }}>
        <h6>🎨 Trigger Display Settings</h6>
        
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "10px" }}>
          <div>
            <label style={{ fontSize: "12px", display: "block", marginBottom: "5px" }}>
              Static Trigger Transparency:
            </label>
            <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
              <input
                type="range"
                min="0"
                max="100"
                value={triggerStyle.staticFillOpacity}
                onChange={(e) => updateTriggerStyle('staticFillOpacity', parseInt(e.target.value))}
                style={{ flex: 1 }}
              />
              <span style={{ fontSize: "11px", minWidth: "30px" }}>
                {triggerStyle.staticFillOpacity}%
              </span>
            </div>
          </div>
          
          <div>
            <label style={{ fontSize: "12px", display: "block", marginBottom: "5px" }}>
              Portable Trigger Transparency:
            </label>
            <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
              <input
                type="range"
                min="0"
                max="100"
                value={triggerStyle.portableFillOpacity}
                onChange={(e) => updateTriggerStyle('portableFillOpacity', parseInt(e.target.value))}
                style={{ flex: 1 }}
              />
              <span style={{ fontSize: "11px", minWidth: "30px" }}>
                {triggerStyle.portableFillOpacity}%
              </span>
            </div>
          </div>
        </div>

        <FormCheck
          type="checkbox"
          label="Show Existing Triggers"
          checked={showExistingTriggers}
          onChange={e => setShowExistingTriggers(e.target.checked)}
        />
      </div>

      {/* Trigger Events Display */}
      <div style={{ 
        marginBottom: "15px", 
        padding: "10px", 
        backgroundColor: "#ffffff", 
        borderRadius: "5px",
        border: "1px solid #dee2e6"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
          <h6>📋 Trigger Events</h6>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <FormCheck
              type="checkbox"
              label="Show Events"
              checked={showTriggerEvents}
              onChange={(e) => setShowTriggerEvents(e.target.checked)}
              style={{ fontSize: "13px" }}
            />
          </div>
        </div>

        {/* Event Filter */}
        <div style={{ marginBottom: "10px" }}>
          <label style={{ fontSize: "12px", marginBottom: "5px", display: "block" }}>
            Filter Events:
          </label>
          <ButtonGroup size="sm">
            <Button 
              variant={eventFilter === 'all' ? 'primary' : 'outline-primary'}
              onClick={() => setEventFilter('all')}
            >
              All
            </Button>
            <Button 
              variant={eventFilter === 'enter' ? 'success' : 'outline-success'}
              onClick={() => setEventFilter('enter')}
            >
              Enter
            </Button>
            <Button 
              variant={eventFilter === 'exit' ? 'danger' : 'outline-danger'}
              onClick={() => setEventFilter('exit')}
            >
              Exit
            </Button>
            <Button 
              variant={eventFilter === 'portable' ? 'warning' : 'outline-warning'}
              onClick={() => setEventFilter('portable')}
            >
              Portable
            </Button>
          </ButtonGroup>
        </div>
        
        {filteredEvents.length === 0 ? (
          <p style={{ margin: 0, fontSize: "13px", color: "#6c757d", fontStyle: "italic" }}>
            No trigger events recorded.
          </p>
        ) : (
          <div style={{ 
            maxHeight: "200px", 
            overflowY: "auto", 
            backgroundColor: "#f8f9fa", 
            border: "1px solid #e9ecef", 
            borderRadius: "4px",
            padding: "8px" 
          }}>
            <ul style={{ margin: 0, padding: 0, listStyleType: "none" }}>
              {filteredEvents.slice(-50).map((event, index) => (
                <li key={index} style={{ 
                  fontSize: "12px", 
                  fontFamily: "monospace",
                  padding: "2px 0",
                  borderBottom: index < filteredEvents.length - 1 ? "1px solid #dee2e6" : "none",
                  color: event.includes('enter') ? '#28a745' : 
                        event.includes('exit') ? '#dc3545' : 
                        event.includes('within') ? '#ffc107' : '#6c757d'
                }}>
                  {event}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Map Display */}
      {selectedZone && (
        <div style={{ 
          marginTop: "15px", 
          padding: "10px", 
          backgroundColor: "#ffffff", 
          borderRadius: "5px",
          border: "1px solid #dee2e6"
        }}>
          <h6>🗺️ Zone Map: {selectedZone.x_nm_zn}</h6>
          
          {selectedZone.i_map ? (
            <NewTriggerViewer
              key={`display-${selectedZone.i_map}-${selectedZone.i_zn}`}
              mapId={selectedZone.i_map}
              zones={[selectedZone]}
              checkedZones={[selectedZone.i_zn]}
              vertices={zoneVertices}
              useLeaflet={true}
              enableDrawing={false}
              onDrawComplete={() => {}}
              showExistingTriggers={showExistingTriggers}
              existingTriggerPolygons={existingTriggerPolygons.map(p => ({
                ...p,
                isContained: p.isPortable ? Object.keys(portableTriggerContainment[p.id] || {}).some(tagId => portableTriggerContainment[p.id][tagId]) : false
              }))}
              tagsData={tagsData}
              isConnected={isConnected}
              triggers={triggers}
              triggerStyle={triggerStyle}
            />
          ) : (
            <div style={{ 
              padding: "20px", 
              textAlign: "center", 
              color: "#dc3545", 
              backgroundColor: "#f8d7da", 
              borderRadius: "4px",
              border: "1px solid #f5c6cb"
            }}>
              ⚠️ No map ID available for this zone.
            </div>
          )}
        </div>
      )}

      {/* Display Help */}
      <div style={{ 
        marginTop: "15px", 
        padding: "10px", 
        backgroundColor: "#e7f3ff", 
        borderRadius: "5px",
        border: "1px solid #b3d9ff"
      }}>
        <h6 style={{ color: "#0066cc" }}>💡 Display Help</h6>
        <ul style={{ fontSize: "13px", color: "#333", marginBottom: 0 }}>
          <li>Use transparency sliders to adjust trigger visibility</li>
          <li>Toggle "Show Existing Triggers" to hide/show triggers on map</li>
          <li>Filter events by type (Enter, Exit, Portable)</li>
          <li>Events are color-coded: green (enter), red (exit), yellow (portable)</li>
          <li>Portable triggers move with their assigned tags</li>
        </ul>
      </div>
    </div>
  );
};

export default TriggerDisplayTab;