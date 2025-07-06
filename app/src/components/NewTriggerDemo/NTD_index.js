/* Name: NTD_index.js */
/* Version: 0.2.2 */
/* Created: 250625 */
/* Modified: 250706 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Main component for NewTriggerDemo - Enhanced with responsive map controls and better UI integration */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/NTD_index.js */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect, useRef, useCallback } from "react";
import { Tabs, Tab, Button, Form, Alert } from "react-bootstrap";

// Import styles
import "./styles/NewTriggerDemo.css";

// Import NEW tab components
import TriggerDataTab from "./components/TriggerDataTab";
import TriggerCreateTab from "./components/TriggerCreateTab";
import TriggerDisplayTab from "./components/TriggerDisplayTab";
// Import existing components
import TriggerDeleteTab from "./components/TriggerDeleteTab";
import TriggerEventsTab from "./components/TriggerEventsTab";
import TetseConversionTab from "./components/TetseConversionTab";

// Import hooks
import { useWebSocket } from "./hooks/useWebSocket";
import { useTriggerContainment } from "./hooks/useTriggerContainment";
import { useTagTracking } from "./hooks/useTagTracking";

// Import services
import { triggerApi } from "./services/triggerApi";
import { zoneApi } from "./services/zoneApi";

// Import utils
import { getFormattedTimestamp } from "./utils/formatters";

const NewTriggerDemo = () => {
  // Zone state
  const [zones, setZones] = useState([]);
  const [zoneHierarchy, setZoneHierarchy] = useState([]);
  const [selectedZone, setSelectedZone] = useState(null);
  
  // Trigger state
  const [triggers, setTriggers] = useState([]);
  const [triggerDirections, setTriggerDirections] = useState([]);
  
  // Event tracking
  const [eventList, setEventList] = useState(() => {
    const savedEvents = localStorage.getItem("eventList");
    return savedEvents ? JSON.parse(savedEvents) : [];
  });
  const [triggerEvents, setTriggerEvents] = useState([]);
  const [showTriggerEvents, setShowTriggerEvents] = useState(true);
  const showTriggerEventsRef = useRef(true);
  
  // UI state
  const [activeTab, setActiveTab] = useState("dataSubscription");
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  
  // NEW: Enhanced UI settings
  const [mapSettings, setMapSettings] = useState({
    responsive: true,
    enableControls: true,
    showLegend: true,
    height: "600px",
    width: "100%"
  });
  const [highlightedTrigger, setHighlightedTrigger] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  
  // Tag tracking state
  const [tagIdsInput, setTagIdsInput] = useState("SIM1,SIM2");
  
  // WebSocket and data tracking
  const {
    isConnected,
    tagsData,
    sequenceNumbers,
    tagCount,
    tagRate,
    connectWebSocket,
    disconnectWebSocket
  } = useWebSocket({
    selectedZone,
    tagIdsInput,
    zones,
    setEventList,
    setTriggerEvents,
    showTriggerEventsRef,
    fetchTriggers: () => fetchTriggers(),
    triggerDirections,
    triggers,
    setTriggers
  });

  // Trigger containment tracking
  const {
    portableTriggerContainment,
    checkTriggerContainment
  } = useTriggerContainment({
    triggers,
    tagsData,
    selectedZone,
    zones,
    triggerDirections,
    showTriggerEventsRef,
    setTriggerEvents,
    getFormattedTimestamp
  });

  // Save event list to localStorage when it changes
  useEffect(() => {
    localStorage.setItem("eventList", JSON.stringify(eventList));
  }, [eventList]);

  // Update showTriggerEventsRef when showTriggerEvents changes
  useEffect(() => {
    console.log("showTriggerEvents state updated:", showTriggerEvents);
    showTriggerEventsRef.current = showTriggerEvents;
  }, [showTriggerEvents]);

  // NEW: Save map settings to localStorage
  useEffect(() => {
    localStorage.setItem("mapSettings", JSON.stringify(mapSettings));
  }, [mapSettings]);

  // NEW: Load map settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem("mapSettings");
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setMapSettings(prev => ({ ...prev, ...parsed }));
      } catch (e) {
        console.warn("Failed to load map settings:", e);
      }
    }
  }, []);

  // NEW: Handle trigger event highlighting
  useEffect(() => {
    if (triggerEvents.length > 0) {
      const latestEvent = triggerEvents[triggerEvents.length - 1];
      if (latestEvent.trigger_id) {
        setHighlightedTrigger(latestEvent.trigger_id);
        // Clear highlight after 3 seconds
        setTimeout(() => setHighlightedTrigger(null), 3000);
      }
    }
  }, [triggerEvents]);

  // Fetch triggers from API
  const fetchTriggers = async () => {
    try {
      const data = await triggerApi.fetchTriggers();
      console.log("Raw trigger data:", data);
      let triggerArray = Array.isArray(data) ? data : (data.triggers || []);
      setTriggers(triggerArray);
      console.log("Processed triggers:", triggerArray);
    } catch (e) {
      setFetchError(`Error fetching triggers: ${e.message}`);
      console.error("Fetch triggers error:", e);
    }
  };

  // Fetch zones and hierarchy on mount
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        // Fetch zones
        const { zones: mappedZones, hierarchy, selectedZone: initialZone } = await zoneApi.fetchZonesWithHierarchy();
        setZones(mappedZones);
        setZoneHierarchy(hierarchy);
        
        if (initialZone) {
          setSelectedZone(initialZone);
        }

        // Fetch trigger directions
        const directions = await triggerApi.fetchTriggerDirections();
        setTriggerDirections(directions);

        // Fetch triggers
        await fetchTriggers();
        
        setLoading(false);
      } catch (e) {
        setFetchError(`Error fetching initial data: ${e.message}`);
        setLoading(false);
      }
    };

    fetchInitialData();

    // Cleanup on unmount
    return () => {
      if (isConnected) {
        disconnectWebSocket();
      }
    };
  }, []);

  // Check trigger containment when data changes
  useEffect(() => {
    if (!selectedZone || !triggers || !isConnected || Object.keys(tagsData).length === 0) return;

    const zoneTriggers = triggers.filter(t => 
      t.zone_id === parseInt(selectedZone.i_zn) || t.zone_id == null
    );

    Object.entries(tagsData).forEach(([tagId, tagData]) => {
      zoneTriggers.forEach(trigger => {
        if (trigger.is_portable && trigger.assigned_tag_id !== tagId) {
          checkTriggerContainment(trigger.i_trg, tagId, tagData.x, tagData.y, tagData.z, true);
        } else if (!trigger.is_portable) {
          checkTriggerContainment(trigger.i_trg, tagId, tagData.x, tagData.y, tagData.z, false);
        }
      });
    });
  }, [tagsData, selectedZone, triggers, isConnected, checkTriggerContainment]);

  // Handle zone change
  const handleZoneChange = (zoneId) => {
    const parsedZoneId = parseInt(zoneId);
    const zone = zones.find(z => z.i_zn === parsedZoneId);
    
    if (zone && (!selectedZone || zone.i_zn !== selectedZone.i_zn)) {
      setSelectedZone(zone);
      setEventList(prev => [...prev, 
        `Zone changed to ${zone.i_zn} - ${zone.x_nm_zn} on ${getFormattedTimestamp()}`
      ]);
      
      // Reconnect WebSocket with new zone if connected
      if (isConnected) {
        console.log("Zone changed, reconnecting WebSocket with new zone_id:", zone.i_zn);
        connectWebSocket();
      }
    }
  };

  // Clear system events
  const clearSystemEvents = () => {
    setEventList([]);
    localStorage.setItem("eventList", JSON.stringify([]));
  };

  // NEW: Update map settings
  const updateMapSettings = (newSettings) => {
    setMapSettings(prev => ({ ...prev, ...newSettings }));
  };

  // NEW: Connection status component
  const ConnectionStatus = () => (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      padding: '8px 12px',
      backgroundColor: isConnected ? '#d4edda' : '#f8d7da',
      color: isConnected ? '#155724' : '#721c24',
      border: `1px solid ${isConnected ? '#c3e6cb' : '#f5c6cb'}`,
      borderRadius: '4px',
      fontSize: '14px',
      marginBottom: '10px'
    }}>
      <span style={{ 
        width: '8px', 
        height: '8px', 
        borderRadius: '50%', 
        backgroundColor: isConnected ? '#28a745' : '#dc3545' 
      }}></span>
      <span>
        {isConnected ? 'Connected to WebSocket' : 'Disconnected from WebSocket'}
      </span>
      {isConnected && (
        <span style={{ marginLeft: 'auto', fontSize: '12px', opacity: 0.8 }}>
          Tags: {tagCount} | Rate: {tagRate.toFixed(1)}/s
        </span>
      )}
    </div>
  );

  // NEW: Map settings panel
  const MapSettingsPanel = () => (
    <div style={{
      backgroundColor: '#f8f9fa',
      border: '1px solid #dee2e6',
      borderRadius: '4px',
      padding: '12px',
      marginBottom: '10px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h6 style={{ margin: 0 }}>Map Settings</h6>
        <Button 
          variant="outline-secondary" 
          size="sm"
          onClick={() => setShowSettings(!showSettings)}
        >
          {showSettings ? 'Hide' : 'Show'}
        </Button>
      </div>
      
      {showSettings && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '14px' }}>
          <Form.Check
            type="checkbox"
            label="Responsive sizing"
            checked={mapSettings.responsive}
            onChange={(e) => updateMapSettings({ responsive: e.target.checked })}
          />
          <Form.Check
            type="checkbox"
            label="Show controls"
            checked={mapSettings.enableControls}
            onChange={(e) => updateMapSettings({ enableControls: e.target.checked })}
          />
          <Form.Check
            type="checkbox"
            label="Show legend"
            checked={mapSettings.showLegend}
            onChange={(e) => updateMapSettings({ showLegend: e.target.checked })}
          />
          <div>
            <Form.Label style={{ fontSize: '12px', marginBottom: '2px' }}>Map Height</Form.Label>
            <Form.Select
              size="sm"
              value={mapSettings.height}
              onChange={(e) => updateMapSettings({ height: e.target.value })}
            >
              <option value="400px">400px</option>
              <option value="500px">500px</option>
              <option value="600px">600px</option>
              <option value="700px">700px</option>
              <option value="800px">800px</option>
            </Form.Select>
          </div>
        </div>
      )}
    </div>
  );

  // NEW: Enhanced trigger display polygons with highlighting
  const getEnhancedTriggerPolygons = () => {
    if (!triggers || triggers.length === 0) return [];
    
    return triggers.map(trigger => ({
      ...trigger,
      id: trigger.i_trg,
      isPortable: trigger.is_portable,
      isContained: portableTriggerContainment[trigger.i_trg] || false,
      isHighlighted: highlightedTrigger === trigger.i_trg,
      center: trigger.is_portable && trigger.assigned_tag_id ? 
        (tagsData[trigger.assigned_tag_id] ? 
          [tagsData[trigger.assigned_tag_id].y, tagsData[trigger.assigned_tag_id].x] : null) : null,
      radius: trigger.radius_ft || 10,
      latLngs: !trigger.is_portable && trigger.vertices ? 
        trigger.vertices.map(v => [v.y, v.x]) : null
    }));
  };

  return (
    <div className="new-trigger-demo">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h2 style={{ margin: 0 }}>New Trigger Demo</h2>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Button variant="secondary" onClick={clearSystemEvents}>
            Clear System Events
          </Button>
          <Button 
            variant="info" 
            size="sm"
            onClick={() => setShowSettings(!showSettings)}
          >
            ⚙️ Settings
          </Button>
        </div>
      </div>

      <ConnectionStatus />
      
      {showSettings && <MapSettingsPanel />}
      
      {fetchError && (
        <Alert variant="danger" style={{ marginBottom: '15px' }}>
          {fetchError}
        </Alert>
      )}
      
      {loading && <p className="loading-indicator">Loading...</p>}
      
      <Tabs 
        defaultActiveKey="dataSubscription" 
        onSelect={(key) => setActiveTab(key)}
        className="mb-3"
      >
        <Tab eventKey="dataSubscription" title="📡 Data Subscription">
          {activeTab === "dataSubscription" && (
            <TriggerDataTab
              zones={zones}
              zoneHierarchy={zoneHierarchy}
              selectedZone={selectedZone}
              tagIdsInput={tagIdsInput}
              setTagIdsInput={setTagIdsInput}
              isConnected={isConnected}
              tagsData={tagsData}
              sequenceNumbers={sequenceNumbers}
              tagCount={tagCount}
              tagRate={tagRate}
              connectWebSocket={connectWebSocket}
              disconnectWebSocket={disconnectWebSocket}
              handleZoneChange={handleZoneChange}
              // NEW: Enhanced props
              mapSettings={mapSettings}
              updateMapSettings={updateMapSettings}
            />
          )}
        </Tab>

        <Tab eventKey="createTrigger" title="➕ Create Trigger">
          {activeTab === "createTrigger" && (
            <TriggerCreateTab
              zones={zones}
              zoneHierarchy={zoneHierarchy}
              selectedZone={selectedZone}
              triggerDirections={triggerDirections}
              setEventList={setEventList}
              fetchTriggers={fetchTriggers}
              handleZoneChange={handleZoneChange}
              // NEW: Enhanced map settings
              mapSettings={mapSettings}
              enableResponsive={mapSettings.responsive}
              enableControls={mapSettings.enableControls}
              height={mapSettings.height}
              width={mapSettings.width}
            />
          )}
        </Tab>

        <Tab eventKey="displayTriggers" title="👁️ View Triggers">
          {activeTab === "displayTriggers" && (
            <TriggerDisplayTab
              zones={zones}
              selectedZone={selectedZone}
              triggers={triggers}
              tagsData={tagsData}
              isConnected={isConnected}
              triggerEvents={triggerEvents}
              showTriggerEvents={showTriggerEvents}
              setShowTriggerEvents={setShowTriggerEvents}
              portableTriggerContainment={portableTriggerContainment}
              // NEW: Enhanced map integration
              mapSettings={mapSettings}
              highlightedTrigger={highlightedTrigger}
              enhancedTriggerPolygons={getEnhancedTriggerPolygons()}
              enableResponsive={mapSettings.responsive}
              enableControls={mapSettings.enableControls}
              height={mapSettings.height}
              width={mapSettings.width}
            />
          )}
        </Tab>

        <Tab eventKey="deleteTriggers" title="🗑️ Delete Triggers">
          {activeTab === "deleteTriggers" && (
            <TriggerDeleteTab
              triggers={triggers}
              triggerDirections={triggerDirections}
              fetchTriggers={fetchTriggers}
              setEventList={setEventList}
            />
          )}
        </Tab>

        <Tab eventKey="events" title="📋 System Events">
          {activeTab === "events" && (
            <TriggerEventsTab 
              eventList={eventList}
              triggerEvents={triggerEvents}
              onTriggerHighlight={setHighlightedTrigger}
            />
          )}
        </Tab>

        <Tab eventKey="tetseToTriggers" title="🔄 TETSE to Triggers">
          {activeTab === "tetseToTriggers" && (
            <TetseConversionTab
              eventList={eventList}
              setEventList={setEventList}
              fetchTriggers={fetchTriggers}
            />
          )}
        </Tab>
      </Tabs>

      {/* NEW: Global keyboard shortcuts info */}
      <div style={{
        position: 'fixed',
        bottom: '10px',
        left: '10px',
        fontSize: '11px',
        color: '#666',
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        padding: '4px 8px',
        borderRadius: '3px',
        border: '1px solid #ddd'
      }}>
        💡 Map shortcuts: Home (🏠), Fit Data (📏), Scale bar enabled
      </div>
    </div>
  );
};

export default NewTriggerDemo;