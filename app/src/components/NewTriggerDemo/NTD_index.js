/* Name: NTD_index.js */
/* Version: 0.1.0 */
/* Created: 250625 */
/* Modified: 250625 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Main component for NewTriggerDemo - orchestrates all subcomponents */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/NTD_index.js */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect, useRef, useCallback } from "react";
import { Tabs, Tab, Button } from "react-bootstrap";

// Import styles
import "./styles/NewTriggerDemo.css";

// Import components
import TriggerMapTab from "./components/TriggerMapTab";
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
  const [activeTab, setActiveTab] = useState("mapAndTrigger");
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  
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

  return (
    <div className="new-trigger-demo">
      <h2>New Trigger Demo</h2>
      <Button variant="secondary" onClick={clearSystemEvents}>
        Clear System Events
      </Button>
      {fetchError && <div className="fetch-error">{fetchError}</div>}
      {loading && <p className="loading-indicator">Loading...</p>}
      
      <Tabs 
        defaultActiveKey="mapAndTrigger" 
        onSelect={(key) => setActiveTab(key)}
      >
        <Tab eventKey="mapAndTrigger" title="Map & Trigger">
          <TriggerMapTab
            zones={zones}
            zoneHierarchy={zoneHierarchy}
            selectedZone={selectedZone}
            triggers={triggers}
            triggerDirections={triggerDirections}
            tagIdsInput={tagIdsInput}
            setTagIdsInput={setTagIdsInput}
            isConnected={isConnected}
            tagsData={tagsData}
            sequenceNumbers={sequenceNumbers}
            tagCount={tagCount}
            tagRate={tagRate}
            triggerEvents={triggerEvents}
            showTriggerEvents={showTriggerEvents}
            setShowTriggerEvents={setShowTriggerEvents}
            eventList={eventList}
            setEventList={setEventList}
            portableTriggerContainment={portableTriggerContainment}
            connectWebSocket={connectWebSocket}
            disconnectWebSocket={disconnectWebSocket}
            handleZoneChange={handleZoneChange}
            fetchTriggers={fetchTriggers}
            activeTab={activeTab}
          />
        </Tab>

        <Tab eventKey="deleteTriggers" title="Delete Triggers">
          <TriggerDeleteTab
            triggers={triggers}
            triggerDirections={triggerDirections}
            fetchTriggers={fetchTriggers}
            setEventList={setEventList}
          />
        </Tab>

        <Tab eventKey="events" title="System Events">
          <TriggerEventsTab eventList={eventList} />
        </Tab>

        <Tab eventKey="tetseToTriggers" title="TETSE to Triggers">
          <TetseConversionTab
            eventList={eventList}
            setEventList={setEventList}
            fetchTriggers={fetchTriggers}
          />
        </Tab>
      </Tabs>
    </div>
  );
};

export default NewTriggerDemo;