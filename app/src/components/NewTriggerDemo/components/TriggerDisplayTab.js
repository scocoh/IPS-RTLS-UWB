/* Name: TriggerDisplayTab.js */
/* Version: 0.1.9 */
/* Created: 250705 */
/* Modified: 250707 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Trigger display tab – Refactored with separate static and portable renderers */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect, useRef } from "react";
import { FormCheck, ButtonGroup, Button } from "react-bootstrap";
// FIXED: Import path (adjust if needed based on your actual structure)
import NewTriggerViewer from "../../NewTriggerViewer/NTV_index";
import { zoneApi } from "../services/zoneApi";
// NEW: Import renderer components
import PortableTriggerRenderer from "./PortableTriggerRenderer";
import StaticTriggerRenderer from "./StaticTriggerRenderer";

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
  const [showTriggerLabels, setShowTriggerLabels] = useState(true);
  
  // NEW: Separate state for static and portable triggers
  const [staticTriggerPolygons, setStaticTriggerPolygons] = useState([]);
  const [portableTriggerPolygons, setPortableTriggerPolygons] = useState([]);
  const [combinedTriggerPolygons, setCombinedTriggerPolygons] = useState([]);
  // REMOVED: mapUpdateKey - was causing infinite re-renders
  
  const [eventFilter, setEventFilter] = useState('all');

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

  // ENHANCED: Debug logging with refactored components
  console.log("TriggerDisplayTab DEBUG:", {
    selectedZone: selectedZone?.i_zn,
    triggersCount: triggers?.length,
    zoneTriggers: triggers?.filter(t => t.zone_id === parseInt(selectedZone?.i_zn) || t.zone_id == null)?.length,
    staticPolygons: staticTriggerPolygons.length,
    portablePolygons: portableTriggerPolygons.length,
    combinedPolygons: combinedTriggerPolygons.length,
    showExistingTriggers,
    showTriggerLabels
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
          console.log("✅ Zone vertices fetched:", vertices.length);
          setZoneVertices(vertices);
        } catch (e) {
          console.error("❌ Error fetching zone vertices:", e);
        }
      };
      fetchZoneVertices();
    }
  }, [selectedZone]);

  // NEW: Callback handlers for renderer components
  const handleStaticTriggersUpdate = (staticPolygons) => {
    console.log("📨 Received static triggers update:", staticPolygons.length);
    setStaticTriggerPolygons(staticPolygons);
  };

  const handlePortableTriggersUpdate = (portablePolygons) => {
    console.log("📨 Received portable triggers update:", portablePolygons.length);
    setPortableTriggerPolygons(portablePolygons);
    // REMOVED: Forced map re-render - causing infinite loops
  };

  // NEW: Combine static and portable triggers for map display
  useEffect(() => {
    const combined = [...staticTriggerPolygons, ...portableTriggerPolygons];
    console.log(`🔄 Combining triggers: ${staticTriggerPolygons.length} static + ${portableTriggerPolygons.length} portable = ${combined.length} total`);
    
    // Force new array reference to trigger NewTriggerViewer re-render
    setCombinedTriggerPolygons([...combined]);
  }, [staticTriggerPolygons, portableTriggerPolygons]);

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

      {/* NEW: Renderer Components (invisible) */}
      <StaticTriggerRenderer
        selectedZone={selectedZone}
        triggers={triggers}
        triggerStyle={triggerStyle}
        onStaticTriggersUpdate={handleStaticTriggersUpdate}
      />
      
      <PortableTriggerRenderer
        selectedZone={selectedZone}
        triggers={triggers}
        tagsData={tagsData}
        isConnected={isConnected}
        triggerStyle={triggerStyle}
        portableTriggerContainment={portableTriggerContainment}
        onPortableTriggersUpdate={handlePortableTriggersUpdate}
      />

      {/* ENHANCED: Debug Info Panel with refactored data */}
      <div style={{ 
        marginBottom: "15px", 
        padding: "10px", 
        backgroundColor: "#fff3cd", 
        borderRadius: "5px",
        border: "1px solid #ffeaa7",
        fontSize: "12px"
      }}>
        <h6>🐛 Debug Info (Refactored)</h6>
        <div>Zone: {selectedZone?.i_zn} | Map ID: {selectedZone?.i_map}</div>
        <div>Total Triggers: {triggers?.length || 0}</div>
        <div>Zone Triggers: {triggers?.filter(t => t.zone_id === parseInt(selectedZone?.i_zn) || t.zone_id == null)?.length || 0}</div>
        <div>Portable Polygons: {portableTriggerPolygons.length} (Keys: {portableTriggerPolygons.map(p => p.uniqueKey).join(', ')})</div>
        <div>Combined Polygons: {combinedTriggerPolygons.length}</div>
        <div>Show Triggers: {showExistingTriggers ? 'YES' : 'NO'} | Show Labels: {showTriggerLabels ? 'YES' : 'NO'}</div>
        <div>Tag Data Keys: {Object.keys(tagsData || {}).join(', ')}</div>
      </div>

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

        <div style={{ display: "flex", gap: "15px" }}>
          <FormCheck
            type="checkbox"
            label="Show Existing Triggers"
            checked={showExistingTriggers}
            onChange={e => setShowExistingTriggers(e.target.checked)}
          />
          <FormCheck
            type="checkbox"
            label="Show Trigger ID Numbers"
            checked={showTriggerLabels}
            onChange={e => setShowTriggerLabels(e.target.checked)}
          />
        </div>
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
              showTriggerLabels={showTriggerLabels}
              existingTriggerPolygons={combinedTriggerPolygons}
              // REMOVED: triggerPolygonKey prop - not accepted by NewTriggerViewer
              tagsData={tagsData}
              isConnected={isConnected}
              triggers={triggers}
              triggerStyle={triggerStyle}
              // ADDED: Debug props
              enableResponsive={true}
              enableControls={true}
              height="600px"
              width="100%"
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
          <li><strong>Toggle "Show Trigger ID Numbers" to display trigger IDs at trigger centers</strong></li>
          <li>Filter events by type (Enter, Exit, Portable)</li>
          <li>Events are color-coded: green (enter), red (exit), yellow (portable)</li>
          <li><strong>Portable triggers now update in real-time with separate rendering logic</strong></li>
          <li>Trigger ID labels are color-matched to their trigger type</li>
          <li><strong>Static and portable triggers are handled by separate components for better performance</strong></li>
        </ul>
      </div>
    </div>
  );
};

export default TriggerDisplayTab;