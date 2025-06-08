/* Name: NewTriggerDemo.js */
/* Version: 0.1.15 */
/* Created: 250607 */
/* Modified: 250607 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: JavaScript file for ParcoRTLS frontend to manage triggers */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo.js
// Version: 0.1.15 - Updated retryReloadTriggers to use port 8000, bumped from 0.1.14
// Version: 0.1.14 - Rate-limited GISData processing, validated tag subscriptions, skipped invalid zone checks, bumped from 0.1.13
// Previous: Updated heartbeat responses to include heartbeat_id for HeartbeatManager compatibility, bumped from 0.1.12
// Previous: Batched containment checks in useEffect, increased dataTimeout to 60s, bumped from 0.1.11
// Previous: Added GISData logging, extended dataTimeout, bumped from 0.1.10
// Previous: Added client-side radius-based containment for portable triggers, fixed event generation, bumped from 0.1.9
// Previous: Enhanced checkPortableTriggerContainment to handle all trigger directions, added static trigger containment, bumped from 0.1.8
// Previous: Ensured shouldReconnect persists, added WebSocket state logging, bumped from 0.1.7
// Previous: Fixed heartbeat handling, reset reconnectAttempts, added subscription timing logs, bumped from 0.1.6
// Previous: Increased maxReconnectAttempts, added stream subscription delay, enhanced error logging, bumped from 0.1.5
// Previous: Fixed TypeScript syntax errors, retained debug logging, bumped from 0.1.4
// Previous: Added debug logging for WebSocket URIs, subscriptions, closures, bumped from 0.1.3
// Previous: Updated to handle GISData messages, respond to heartbeats with heartbeat_id, enhanced reconnection, bumped from 0.1.2
// Previous: Updated WebSocket URI to ControlManager, bumped from 0.1.1
// Previous: Added PortRedirect handling (v0.1.1)
// Previous: Removed scaling factor for portable trigger radii (v0.10.90)
// Previous: Enhanced TriggerEvent message for portable triggers (v0.10.89)

import React, { useState, useEffect, useRef, useCallback } from "react";
import { Form, Tabs, Tab, Table, Button, FormCheck, InputGroup, FormControl } from "react-bootstrap";
import NewTriggerViewer from "./NewTriggerViewer";
import L from "leaflet";

const NewTriggerDemo = () => {
  const [zones, setZones] = useState([]);
  const [zoneHierarchy, setZoneHierarchy] = useState([]);
  const [selectedZone, setSelectedZone] = useState(null);
  const [zoneVertices, setZoneVertices] = useState([]);
  const [zMin, setZMin] = useState(null);
  const [zMax, setZMax] = useState(null);
  const [customZMax, setCustomZMax] = useState(null);
  const [triggerName, setTriggerName] = useState("");
  const [triggerDirection, setTriggerDirection] = useState("");
  const [triggerDirections, setTriggerDirections] = useState([]);
  const [triggers, setTriggers] = useState([]);
  const [coordinates, setCoordinates] = useState([]);
  const [showMapForDrawing, setShowMapForDrawing] = useState(false);
  const [eventList, setEventList] = useState(() => {
    const savedEvents = localStorage.getItem("eventList");
    return savedEvents ? JSON.parse(savedEvents) : [];
  });
  const [triggerEvents, setTriggerEvents] = useState([]);
  const [showTriggerEvents, setShowTriggerEvents] = useState(true);
  const showTriggerEventsRef = useRef(true);
  const [loading, setLoading] = useState(true);
  const [showExistingTriggers, setShowExistingTriggers] = useState(true);
  const [existingTriggerPolygons, setExistingTriggerPolygons] = useState([]);
  const [useLeaflet, setUseLeaflet] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  const [tagIdsInput, setTagIdsInput] = useState("SIM1,SIM2");
  const [isConnected, setIsConnected] = useState(false);
  const [tagsData, setTagsData] = useState({});
  const [pendingTagsData, setPendingTagsData] = useState([]);
  const [sequenceNumbers, setSequenceNumbers] = useState({});
  const [tagCount, setTagCount] = useState(0);
  const [tagRate, setTagRate] = useState(0);
  const [tagTimestamps, setTagTimestamps] = useState([]);
  const [activeTab, setActiveTab] = useState("mapAndTrigger");
  const [portableTriggerContainment, setPortableTriggerContainment] = useState({});
  const [triggerContainmentState, setTriggerContainmentState] = useState({});
  const wsRef = useRef(null);
  const streamWsRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 10;
  const reconnectInterval = 5000;
  const shouldReconnect = useRef(true);
  const lastDataTime = useRef(null);
  const dataTimeout = 60000; // 60s
  const hasPromptedForZone = useRef(false);
  const retryIntervalRef = useRef(null);
  const lastUpdateTime = useRef(0);

  useEffect(() => {
    console.log("triggerEvents state updated:", triggerEvents);
  }, [triggerEvents]);

  useEffect(() => {
    console.log("showTriggerEvents state updated:", showTriggerEvents);
    showTriggerEventsRef.current = showTriggerEvents;
  }, [showTriggerEvents]);

  useEffect(() => {
    localStorage.setItem("eventList", JSON.stringify(eventList));
  }, [eventList]);

  const getFormattedTimestamp = () => {
    const now = new Date();
    const pad = (val) => String(val).padStart(2, "0");
    return `${String(now.getFullYear()).slice(-2)}${pad(now.getMonth() + 1)}${pad(now.getDate())} ${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
  };

  const fetchTriggers = async () => {
    try {
      const res = await fetch("http://192.168.210.226:8000/api/list_newtriggers");
      console.log("Fetch triggers response status:", res.status);
      if (!res.ok) throw new Error(`Failed to fetch triggers: ${res.status}`);
      const data = await res.json();
      console.log("Raw trigger data:", data);
      let triggerArray = Array.isArray(data) ? data : (data.triggers || []);
      setTriggers(triggerArray);
      console.log("Processed triggers:", triggerArray);
    } catch (e) {
      setFetchError(`Error fetching triggers: ${e.message}`);
      console.error("Fetch triggers error:", e);
    }
  };

  const checkTriggerContainment = async (triggerId, tagId, x, y, z, isPortable) => {
    try {
      const trigger = triggers.find(t => t.i_trg === triggerId);
      if (!trigger) return;

      // Verify tag is in a valid zone
      const zoneRes = await fetch(`http://192.168.210.226:8000/api/zones_by_point?x=${x}&y=${y}&z=${z}`);
      if (!zoneRes.ok) throw new Error(`Failed to check zone: ${zoneRes.status}`);
      const zoneData = await zoneRes.json();
      if (!zoneData.length) {
        console.log(`Tag ${tagId} at (${x}, ${y}, ${z}) not in any zone, skipping containment check`);
        return;
      }

      let contains = false;
      if (isPortable && trigger.assigned_tag_id) {
        const assignedTagData = tagsData[trigger.assigned_tag_id];
        if (assignedTagData) {
          const dx = x - assignedTagData.x;
          const dy = y - assignedTagData.y;
          const dz = z - assignedTagData.z;
          const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
          contains = distance <= trigger.radius_ft;
          console.log(`Portable trigger ${triggerId} containment: tag ${tagId} at (${x}, ${y}, ${z}), center (${assignedTagData.x}, ${assignedTagData.y}, ${assignedTagData.z}), distance=${distance}, radius=${trigger.radius_ft}, contains=${contains}`);
        } else {
          console.log(`No position data for assigned tag ${trigger.assigned_tag_id} for portable trigger ${triggerId}`);
        }
      } else {
        const res = await fetch(`http://192.168.210.226:8000/api/trigger_contains_point/${triggerId}?x=${x}&y=${y}&z=${z}`);
        if (!res.ok) throw new Error(`Failed to check containment: ${res.status}`);
        const data = await res.json();
        if (typeof data.contains !== 'boolean') {
          throw new Error("Invalid response format from trigger_contains_point");
        }
        contains = data.contains;
        console.log(`Static trigger ${triggerId} containment: tag ${tagId} at (${x}, ${y}, ${z}), contains=${contains}`);
      }

      setTriggerContainmentState(prev => {
        const prevState = prev[`${triggerId}_${tagId}`] || { contains: false, lastCross: null };
        const newState = { ...prev, [`${triggerId}_${tagId}`]: { contains, lastCross: prevState.lastCross } };
        
        if (showTriggerEventsRef.current) {
          const zoneId = trigger.zone_id || selectedZone?.i_zn || 417;
          const zoneName = zones.find(z => z.i_zn === zoneId)?.x_nm_zn || "Unknown";
          const directionName = triggerDirections.find(d => d.i_dir === trigger.i_dir)?.x_dir || "Unknown";
          
          if (trigger.i_dir === 1 && contains) { // While In
            setTriggerEvents(prev => [
              ...prev,
              `Tag ${tagId} is inside trigger ${trigger.x_nm_trg} (ID: ${triggerId}, Zone: ${zoneName}) at ${getFormattedTimestamp()}`
            ].slice(-10));
          } else if (trigger.i_dir === 2 && !contains) { // While Out
            setTriggerEvents(prev => [
              ...prev,
              `Tag ${tagId} is outside trigger ${trigger.x_nm_trg} (ID: ${triggerId}, Zone: ${zoneName}) at ${getFormattedTimestamp()}`
            ].slice(-10));
          } else if (trigger.i_dir === 3 && prevState.contains !== contains) { // On Cross
            setTriggerEvents(prev => [
              ...prev,
              `Tag ${tagId} crossed trigger ${trigger.x_nm_trg} (ID: ${triggerId}, Zone: ${zoneName}, Direction: ${contains ? 'Enter' : 'Exit'}) at ${getFormattedTimestamp()}`
            ].slice(-10));
            newState[`${triggerId}_${tagId}`].lastCross = Date.now();
          } else if (trigger.i_dir === 4 && !prevState.contains && contains) { // On Enter
            setTriggerEvents(prev => [
              ...prev,
              `Tag ${tagId} entered trigger ${trigger.x_nm_trg} (ID: ${triggerId}, Zone: ${zoneName}) at ${getFormattedTimestamp()}`
            ].slice(-10));
          } else if (trigger.i_dir === 5 && prevState.contains && !contains) { // On Exit
            setTriggerEvents(prev => [
              ...prev,
              `Tag ${tagId} exited trigger ${trigger.x_nm_trg} (ID: ${triggerId}, Zone: ${zoneName}) at ${getFormattedTimestamp()}`
            ].slice(-10));
          }
        }

        if (isPortable) {
          setPortableTriggerContainment(prevContainment => ({
            ...prevContainment,
            [triggerId]: { ...prevContainment[triggerId], [tagId]: contains }
          }));
        }
        return newState;
      });
    } catch (e) {
      console.error(`Error checking containment for trigger ${triggerId}, tag ${tagId}:`, e);
    }
  };

  useEffect(() => {
    if (!selectedZone || !triggers || !isConnected || Object.keys(tagsData).length === 0) return;

    const now = Date.now();
    if (now - lastUpdateTime.current < 4000) return; // Throttle to 4s (0.25 Hz)
    lastUpdateTime.current = now;

    console.log(`Batch containment check for tagsData:`, tagsData);
    const zoneTriggers = triggers.filter(t => t.zone_id === parseInt(selectedZone.i_zn) || t.zone_id == null);
    console.log(`Checking containment for ${zoneTriggers.length} triggers in zone ${selectedZone.i_zn}`);

    Object.entries(tagsData).forEach(([tagId, tagData]) => {
      zoneTriggers.forEach(trigger => {
        if (trigger.is_portable && trigger.assigned_tag_id !== tagId) {
          checkTriggerContainment(trigger.i_trg, tagId, tagData.x, tagData.y, tagData.z, true);
        } else if (!trigger.is_portable) {
          checkTriggerContainment(trigger.i_trg, tagId, tagData.x, tagData.y, tagData.z, false);
        }
      });
    });
  }, [tagsData, selectedZone, triggers, isConnected]);

  const movePortableTrigger = async (triggerId, x, y, z) => {
    try {
      const res = await fetch(
        `http://192.168.210.226:8000/api/move_trigger/${triggerId}?new_x=${x}&new_y=${y}&new_z=${z}`,
        { method: "PUT" }
      );
      if (!res.ok) throw new Error(`Failed to move trigger: ${res.status}`);
      const result = await res.json();
      setEventList(prev => [...prev, `Moved trigger ${triggerId} to (${x}, ${y}, ${z}) on ${getFormattedTimestamp()}`]);
      console.log(`Moved trigger ${triggerId}:`, result);
      await fetchTriggers();
    } catch (e) {
      console.error(`Error moving trigger ${triggerId}:`, e);
      setFetchError(`Error moving trigger: ${e.message}`);
    }
  };

  const connectWebSocket = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
      console.log("Control WebSocket close initiated due to reconnect");
    }

    const controlUri = "ws://192.168.210.226:8001/ws/ControlManager";
    console.log(`Connecting to control WebSocket: ${controlUri}`);
    const ws = new WebSocket(controlUri);
    wsRef.current = ws;
    reconnectAttempts.current = 0;

    ws.onopen = () => {
      console.log("Control WebSocket connected to ControlManager");
      const tagIds = tagIdsInput.split(',').map(id => id.trim()).filter(id => id);
      const subscription = {
        type: "request",
        request: "BeginStream",
        reqid: "triggerDemo1",
        params: tagIds.map(id => ({ id, data: "true" })),
        zone_id: selectedZone ? parseInt(selectedZone.i_zn) : 417
      };
      console.log("Control subscription:", subscription);
      console.log(`Sending control subscription at ${getFormattedTimestamp()}`);
      ws.send(JSON.stringify(subscription));
      console.log("Sent control subscription:", subscription);
      setIsConnected(true);
      setEventList(prev => [...prev, `Control WebSocket connected on ${getFormattedTimestamp()}`]);
      if (!tagCount) {
        setTagCount(0);
        setTagTimestamps([]);
        setTagRate(0);
      }
      fetchTriggers();
      hasPromptedForZone.current = false;
    };

    ws.onmessage = async (event) => {
      console.log("Raw control WebSocket message received:", event.data);
      let data;
      try {
        data = JSON.parse(event.data);
      } catch (e) {
        console.error("Failed to parse control WebSocket message:", e);
        return;
      }
      console.log("Parsed control WebSocket message:", data);
      if (data.type === "PortRedirect") {
        console.log("Received PortRedirect:", data);
        const { port, stream_type, manager_name } = data;
        if (port && stream_type && manager_name) {
          const streamUrl = `ws://192.168.210.226:${port}/ws/${manager_name}`;
          console.log(`Connecting to stream WebSocket: ${streamUrl}`);
          setTimeout(() => {
            connectStreamWebSocket(streamUrl, tagIdsInput.split(',').map(id => id.trim()).filter(id => id));
          }, 2000);
        }
      } else if (data.type === "HeartBeat" && data.data?.heartbeat_id) {
        const response = {
          type: "HeartBeat",
          ts: data.ts,
          data: { heartbeat_id: data.data.heartbeat_id }
        };
        ws.send(JSON.stringify(response));
        console.log("Sent control heartbeat response:", response);
        lastDataTime.current = Date.now();
      } else if (data.type === "GISData") {
        handleGISDataMessage(data);
      } else if (data.type === "TriggerEvent") {
        handleTriggerEvent(data);
      } else {
        console.log("Unhandled control WebSocket message type:", data.type);
      }
    };

    ws.onclose = (event) => {
      console.log(`Control WebSocket disconnected with code: ${event.code}, reason: ${event.reason}, shouldReconnect: ${shouldReconnect.current}, attempts: ${reconnectAttempts.current}/${maxReconnectAttempts}`);
      setIsConnected(false);
      setTagRate(0);
      setTagsData({});
      setSequenceNumbers({});
      setEventList(prev => [...prev, `Control WebSocket disconnected on ${getFormattedTimestamp()} (code: ${event.code}, reason: ${event.reason})`]);
      if (shouldReconnect.current && reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current += 1;
        console.log(`Attempting to reconnect control WebSocket (${reconnectAttempts.current}/${maxReconnectAttempts})...`);
        setTimeout(connectWebSocket, reconnectInterval);
      } else {
        console.log("Control WebSocket closed, no reconnect attempted.");
      }
    };

    ws.onerror = (error) => {
      console.error("Control WebSocket error:", error);
      setIsConnected(false);
      setTagRate(0);
      setTagsData({});
      setSequenceNumbers({});
      setEventList(prev => [...prev, `Control WebSocket error on ${getFormattedTimestamp()}: ${error.message || 'Unknown error'}`]);
    };
  };

  const connectStreamWebSocket = (url, tagIds) => {
    if (streamWsRef.current && streamWsRef.current.readyState === WebSocket.OPEN) {
      streamWsRef.current.close();
      console.log("Stream WebSocket close initiated due to reconnect");
    }

    console.log(`Connecting to stream WebSocket: ${url}`);
    const ws = new WebSocket(url);
    streamWsRef.current = ws;
    reconnectAttempts.current = 0;

    ws.onopen = () => {
      console.log("Stream WebSocket connected:", url);
      const subscription = {
        type: "request",
        request: "BeginStream",
        reqid: "triggerDemoStream1",
        params: tagIds.map(id => ({ id, data: "true" })),
        zone_id: selectedZone ? parseInt(selectedZone.i_zn) : 417
      };
      console.log("Stream subscription:", subscription);
      console.log(`Sending stream subscription at ${getFormattedTimestamp()}`);
      ws.send(JSON.stringify(subscription));
      console.log("Sent stream subscription:", subscription);
    };

    ws.onmessage = async (event) => {
      console.log("Raw stream WebSocket message received:", event.data);
      let data;
      try {
        data = JSON.parse(event.data);
      } catch (e) {
        console.error("Failed to parse stream WebSocket message:", e);
        return;
      }
      console.log("Parsed stream WebSocket message:", data);
      if (data.type === "GISData") {
        handleGISDataMessage(data);
      } else if (data.type === "TriggerEvent") {
        handleTriggerEvent(data);
      } else if (data.type === "HeartBeat" && data.data?.heartbeat_id) {
        const response = {
          type: "HeartBeat",
          ts: data.ts,
          data: { heartbeat_id: data.data.heartbeat_id }
        };
        ws.send(JSON.stringify(response));
        console.log("Sent stream heartbeat response:", response);
        lastDataTime.current = Date.now();
      } else {
        console.log("Unhandled stream WebSocket message type:", data.type);
      }
    };

    ws.onclose = (event) => {
      console.log(`Stream WebSocket disconnected with code: ${event.code}, reason: ${event.reason}, shouldReconnect: ${shouldReconnect.current}, attempts: ${reconnectAttempts.current}/${maxReconnectAttempts}`);
      streamWsRef.current = null;
      if (shouldReconnect.current && reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current += 1;
        console.log(`Attempting to reconnect stream WebSocket (${reconnectAttempts.current}/${maxReconnectAttempts})...`);
        setTimeout(() => connectStreamWebSocket(url, tagIds), reconnectInterval);
      } else {
        console.log("Stream WebSocket closed, no reconnect attempted.");
      }
    };

    ws.onerror = (error) => {
      console.error("Stream WebSocket error:", error);
      streamWsRef.current = null;
      setEventList(prev => [...prev, `Stream WebSocket error on ${getFormattedTimestamp()}: ${error.message || 'Unknown error'}`]);
    };
  };

  const handleGISDataMessage = (data) => {
    const tagIds = tagIdsInput.split(',').map(id => id.trim()).filter(id => id);
    if (!tagIds.includes(data.ID)) {
      console.log(`Ignoring GISData for unsubscribed tag ${data.ID}`);
      return;
    }

    console.log("Processing GISData message:", JSON.stringify(data));
    setPendingTagsData(prev => [...prev, data]);

    const now = Date.now();
    if (now - lastUpdateTime.current < 4000) return; // Throttle to 4s (0.25 Hz)
    lastUpdateTime.current = now;

    setPendingTagsData(prev => {
      const updates = [...prev];
      setPendingTagsData([]); // Clear buffer
      updates.forEach(data => {
        lastDataTime.current = now;
        const tagZoneId = data.zone_id || (selectedZone ? selectedZone.i_zn : 417);
        console.log("Tag zone ID determination:", {
          zone_id_in_message: data.zone_id,
          selectedZone_i_zn: selectedZone ? selectedZone.i_zn : "N/A",
          fallback_zone: 417,
          final_tagZoneId: tagZoneId
        });

        const zoneMatch = zones.find(z => z.i_zn === parseInt(tagZoneId));
        if (zoneMatch && selectedZone && selectedZone.i_zn !== parseInt(tagZoneId) && !hasPromptedForZone.current) {
          console.log("Found zone mismatch:", zoneMatch);
          const shouldSwitch = window.confirm(
            `Tag ${data.ID} is in Zone ${zoneMatch.i_zn} (${zoneMatch.x_nm_zn}). Do you want to switch to this zone?`
          );
          if (shouldSwitch) {
            setSelectedZone(zoneMatch);
            setEventList(prev => [...prev, `Zone synced to ${zoneMatch.i_zn} - ${zoneMatch.x_nm_zn} on ${getFormattedTimestamp()}`]);
            hasPromptedForZone.current = true;
            fetchZoneVertices(zoneMatch.i_zn);
          } else {
            console.log("User chose not to switch zones");
            setEventList(prev => [...prev, `User declined to sync to Zone ${zoneMatch.i_zn} on ${getFormattedTimestamp()}`]);
            hasPromptedForZone.current = true;
          }
        }

        const newTagData = {
          id: data.ID,
          x: data.X,
          y: data.Y,
          z: data.Z,
          sequence: data.Sequence,
          timestamp: now,
          zone_id: tagZoneId
        };

        setTagsData(prev => {
          const updated = { ...prev, [data.ID]: newTagData };
          console.log("Updated tagsData:", updated);
          return updated;
        });

        setSequenceNumbers(prev => ({
          ...prev,
          [data.ID]: data.Sequence || "N/A"
        }));
        console.log(`Updated sequence for tag ${data.ID}: ${data.Sequence}`);

        setTagCount(prev => {
          const newCount = prev + 1;
          console.log(`Incremented tagCount to ${newCount} for tag ${data.ID}`);
          return newCount;
        });

        setTagTimestamps(prev => {
          const windowStart = now - 10000;
          const newTimestamps = [...prev, now].filter(ts => ts >= windowStart);
          if (newTimestamps.length > 1) {
            const timeSpan = (newTimestamps[newTimestamps.length - 1] - newTimestamps[0]) / 1000;
            const rate = timeSpan > 0 ? (newTimestamps.length - 1) / timeSpan : 0;
            setTagRate(rate);
            console.log(`Updated tagRate to ${rate.toFixed(2)} tags/sec`);
          } else {
            setTagRate(0);
          }
          return newTimestamps;
        });
      });
      return [];
    });
  };

  const handleTriggerEvent = (data) => {
    console.log("Processing TriggerEvent:", data);
    lastDataTime.current = Date.now();
    let trigger = triggers.find(t => t.i_trg === data.trigger_id);
    if (!trigger) {
      fetch(`http://192.168.210.226:8000/api/get_trigger_details/${data.trigger_id}`)
        .then(res => {
          if (!res.ok) throw new Error(`Failed to fetch trigger details: ${res.status}`);
          return res.json();
        })
        .then(triggerData => {
          trigger = { i_trg: data.trigger_id, x_nm_trg: triggerData.name, i_dir: triggerData.direction_id, i_zn: data.zone_id || parseInt(selectedZone?.i_zn) };
          setTriggers(prev => {
            const newTriggers = [...prev, trigger];
            console.log("Updated triggers:", newTriggers);
            return newTriggers;
          });
          console.log(`Fetched trigger details for ID ${data.trigger_id}:`, triggerData);
          processTriggerEvent(data, trigger);
        })
        .catch(e => {
          console.error(`Error fetching trigger details for ID ${data.trigger_id}:`, e);
        });
    } else {
      processTriggerEvent(data, trigger);
    }
  };

  const processTriggerEvent = (data, trigger) => {
    const zoneName = zones.find(z => z.i_zn === trigger.i_zn)?.x_nm_zn || "Unknown";
    const sequenceNumber = sequenceNumbers[data.tag_id] || (tagsData[data.tag_id]?.sequence || "N/A");
    let eventMsg;
    if (data.assigned_tag_id && data.tag_id !== data.assigned_tag_id) {
      eventMsg = `${data.tag_id} within ${data.assigned_tag_id} Trigger ${trigger.i_trg} (Zone ${trigger.i_zn} - ${zoneName}, Seq ${sequenceNumber}) at ${data.timestamp}`;
    } else {
      eventMsg = `Tag ${data.tag_id} ${data.direction} trigger ${trigger.i_trg} (Zone ${trigger.i_zn} - ${zoneName}, Seq ${sequenceNumber}) at ${data.timestamp}`;
    }
    if (showTriggerEventsRef.current) {
      setTriggerEvents(prev => {
        const newEvents = [...prev, eventMsg].slice(-10);
        console.log("Updated triggerEvents:", newEvents);
        return newEvents;
      });
    }
    const eventMessage = `Tag ${data.tag_id} ${data.direction} trigger ${trigger.x_nm_trg} (Zone ${trigger.i_zn} - ${zoneName}, Seq ${sequenceNumber}) at ${data.timestamp}`;
    setEventList(prev => [...prev, eventMessage]);
  };

  const disconnectWebSocket = async () => {
    if (wsRef.current) {
      shouldReconnect.current = false;
      if (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING) {
        wsRef.current.close();
        console.log("Control WebSocket close initiated");
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      setIsConnected(false);
      wsRef.current = null;
      setTagsData({});
      setSequenceNumbers({});
      setEventList(prev => [...prev, `Control WebSocket disconnected manually on ${getFormattedTimestamp()}`]);
      hasPromptedForZone.current = false;
    }
    if (streamWsRef.current) {
      if (streamWsRef.current.readyState === WebSocket.OPEN || streamWsRef.current.readyState === WebSocket.CONNECTING) {
        streamWsRef.current.close();
        console.log("Stream WebSocket close initiated");
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      streamWsRef.current = null;
    }
  };

  useEffect(() => {
    const checkDataTimeout = () => {
      if (isConnected && lastDataTime.current) {
        const timeSinceLastData = Date.now() - lastDataTime.current;
        if (timeSinceLastData > dataTimeout) {
          console.log("No data received for 60 seconds, assuming disconnected");
          setIsConnected(false);
          setTagsData({});
          setSequenceNumbers({});
          setEventList(prev => [...prev, `No data received for 60 seconds, assumed disconnected on ${getFormattedTimestamp()}`]);
          hasPromptedForZone.current = false;
        }
      }
    };

    const interval = setInterval(checkDataTimeout, 1000);
    return () => clearInterval(interval);
  }, [isConnected]);

  const fetchZoneVertices = async (zoneId) => {
    try {
      const response = await fetch(`http://192.168.210.226:8000/zoneviewer/get_vertices_for_campus/${zoneId}`);
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      const data = await response.json();
      const vertices = data.vertices.map(vertex => ({
        i_vtx: vertex.vertex_id,
        zone_id: vertex.zone_id,
        n_x: Number(vertex.x).toFixed(6),
        n_y: Number(vertex.y).toFixed(6),
        n_z: Number(vertex.z).toFixed(6),
        n_ord: vertex.order,
      }));
      setZoneVertices(vertices);
      const zValues = vertices.map(v => Number(v.n_z));
      const minZ = Math.min(...zValues);
      const maxZ = Math.max(...zValues);
      setZMin(minZ);
      setZMax(maxZ);
      setCustomZMax(maxZ);
    } catch (e) {
      console.error("Error fetching zone vertices:", e);
    }
  };

  useEffect(() => {
    const fetchZones = async () => {
      try {
        const response = await fetch("http://192.168.210.226:8000/zonebuilder/get_parent_zones_for_trigger_demo");
        console.log("Raw response status:", response.status);
        console.log("Raw response headers:", [...response.headers.entries()]);
        const text = await response.text();
        console.log("Raw response text:", text);
        if (!response.ok) throw new Error(`Failed to fetch zones: ${response.status}`);
        let data;
        try {
          data = JSON.parse(text);
        } catch (e) {
          throw new Error(`Failed to parse response as JSON: ${e.message}`);
        }
        console.log("Parsed response data:", data);

        let zonesArray;
        if (Array.isArray(data)) {
          zonesArray = data;
        } else if (data && Array.isArray(data.zones)) {
          zonesArray = data.zones;
        } else {
          throw new Error("Invalid zones response from server: Expected an array or object with zones array.");
        }

        const mappedZones = zonesArray.map(zone => ({
          i_zn: parseInt(zone.zone_id),
          x_nm_zn: zone.name,
          i_typ_zn: zone.level,
          i_map: zone.i_map || null,
          parent_zone_id: zone.parent_zone_id ? parseInt(zone.parent_zone_id) : null
        }));

        const hierarchy = [];
        const zoneMap = new Map(mappedZones.map(zone => [zone.i_zn, { ...zone, children: [] }]));
        zoneMap.forEach(zone => {
          if (zone.parent_zone_id && zoneMap.has(zone.parent_zone_id)) {
            zoneMap.get(zone.parent_zone_id).children.push(zone);
          } else {
            hierarchy.push(zone);
          }
        });

        hierarchy.sort((a, b) => a.x_nm_zn.localeCompare(b.x_nm_zn));
        const customOrder = [1, 10, 2];
        const sortChildren = (children) => {
          children.sort((a, b) => {
            const aIndex = customOrder.indexOf(a.i_typ_zn);
            const bIndex = customOrder.indexOf(b.i_typ_zn);
            if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
            if (aIndex !== -1) return -1;
            if (bIndex !== -1) return 1;
            if (a.i_typ_zn !== b.i_typ_zn) return a.i_typ_zn - b.i_typ_zn;
            return a.x_nm_zn.localeCompare(b.x_nm_zn);
          });
          children.forEach(child => sortChildren(child.children));
        };

        hierarchy.forEach(parent => sortChildren(parent.children));
        console.log("Zone hierarchy:", JSON.stringify(hierarchy, null, 2));
        setZoneHierarchy(hierarchy);
        setZones(mappedZones);
        const campusZone = hierarchy.find(z => z.i_typ_zn === 1);
        if (campusZone) {
          console.log("Selected campus zone:", campusZone);
          setSelectedZone(campusZone);
          await fetchZoneVertices(campusZone.i_zn);
        } else if (hierarchy.length > 0) {
          console.log("No campus zone found, selecting first zone:", hierarchy[0]);
          setSelectedZone(hierarchy[0]);
          await fetchZoneVertices(hierarchy[0].i_zn);
        }
      } catch (e) {
        setFetchError(`Error fetching zones: ${e.message}`);
      }
    };

    const fetchTriggerDirections = async () => {
      try {
        const res = await fetch("http://192.168.210.226:8000/api/list_trigger_directions");
        if (!res.ok) throw new Error(`Failed to fetch trigger directions: ${res.status}`);
        const data = await res.json();
        setTriggerDirections(data);
      } catch (e) {
        setFetchError(`Error fetching directions: ${e.message}`);
      }
    };

    fetchZones();
    fetchTriggerDirections();
    fetchTriggers();

    return () => {
      if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
        wsRef.current.close();
        shouldReconnect.current = false;
        setIsConnected(false);
      }
      if (streamWsRef.current && streamWsRef.current.readyState !== WebSocket.CLOSED) {
        streamWsRef.current.close();
      }
      if (retryIntervalRef.current) {
        clearInterval(retryIntervalRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!selectedZone) return;
    console.log("useEffect triggered with selectedZone:", selectedZone.i_zn, "isConnected:", isConnected);
    const zoneTriggers = triggers.filter(t => t.zone_id === parseInt(selectedZone.i_zn) || t.zone_id == null);
    console.log("Zone triggers for zone", selectedZone.i_zn, ":", zoneTriggers);

    const fetchPolygons = async () => {
      console.log("Fetching polygons for triggers:", zoneTriggers);
      if (zoneTriggers.length === 0) {
        console.log("No triggers found for zone", selectedZone.i_zn);
        setExistingTriggerPolygons([]);
        return;
      }
      try {
        const polygons = await Promise.all(
          zoneTriggers.map(async (t) => {
            try {
              console.log(`Fetching details for trigger ID ${t.i_trg}`);
              if (t.is_portable) {
                return { id: t.i_trg, name: t.x_nm_trg, isPortable: true, pending: true, assigned_tag_id: t.assigned_tag_id, radius_ft: t.radius_ft };
              } else {
                const res = await fetch(`http://192.168.210.226:8000/api/get_trigger_details/${t.i_trg}`);
                if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
                const data = await res.json();
                console.log(`Trigger ${t.i_trg} response from get_trigger_details:`, data);
                if (Array.isArray(data.vertices)) {
                  const latLngs = data.vertices.map(v => [v.y, v.x]);
                  return { id: t.i_trg, name: t.x_nm_trg, latLngs, isPortable: false };
                }
                console.log(`No vertices for trigger ${t.i_trg}`);
                return null;
              }
            } catch (e) {
              console.error(`Failed to fetch details for trigger ${t.i_trg}:`, e);
              return null;
            }
          })
        );
        const validPolygons = polygons.filter(p => p);
        console.log("Fetched polygons:", validPolygons);
        setExistingTriggerPolygons(validPolygons);
      } catch (e) {
        console.error("Failed to fetch polygons:", e);
        setFetchError("Failed to fetch trigger polygons.");
      }
    };

    fetchPolygons();
    fetchZoneVertices(selectedZone.i_zn);
    hasPromptedForZone.current = false;
  }, [selectedZone, triggers]);

  useEffect(() => {
    if (!selectedZone || !triggers || !isConnected) return;

    console.log("Updating portable polygons after WebSocket connection");
    const zoneTriggers = triggers.filter(t => t.zone_id === parseInt(selectedZone.i_zn) || t.zone_id == null);
    const portableTriggers = zoneTriggers.filter(t => t.is_portable);
    if (portableTriggers.length === 0) return;

    const updatePortablePolygons = async () => {
      const updatedPolygons = portableTriggers.map(t => {
        const tagId = t.assigned_tag_id;
        const tagData = tagsData[tagId];
        if (!tagData) {
          console.log(`No live position data for tag ${tagId} assigned to portable trigger ${t.i_trg}`);
          return null;
        }
        const radius = t.radius_ft;
        console.log(`Updating portable trigger ${t.i_trg} with center ${[tagData.y, tagData.x]} and radius ${radius}`);
        return {
          id: t.i_trg,
          name: t.x_nm_trg,
          center: [tagData.y, tagData.x],
          radius: radius,
          isPortable: true,
          assigned_tag_id: t.assigned_tag_id,
          radius_ft: t.radius_ft
        };
      });

      const validPortable = updatedPolygons.filter(p => p);
      if (validPortable.length === portableTriggers.length) {
        setExistingTriggerPolygons(prev => {
          const nonPortable = prev.filter(p => !p.isPortable || p.pending);
          console.log("Updated existingTriggerPolygons:", [...nonPortable, ...validPortable]);
          return [...nonPortable, ...validPortable];
        });
        if (retryIntervalRef.current) {
          clearInterval(retryIntervalRef.current);
          retryIntervalRef.current = null;
        }
      }
    };

    updatePortablePolygons();

    if (!retryIntervalRef.current) {
      retryIntervalRef.current = setInterval(updatePortablePolygons, 1000);
    }

    return () => {
      if (retryIntervalRef.current) {
        clearInterval(retryIntervalRef.current);
        retryIntervalRef.current = null;
      }
    };
  }, [tagsData, selectedZone, triggers, isConnected]);

  useEffect(() => {
    if (!selectedZone || !triggers || !isConnected) return;

    console.log("Refreshing portable polygons");
    const zoneTriggers = triggers.filter(t => t.zone_id === parseInt(selectedZone.i_zn) || t.zone_id == null);
    const portableTriggers = zoneTriggers.filter(t => t.is_portable);
    if (portableTriggers.length === 0) return;

    const refreshPortablePolygons = async () => {
      const updatedPolygons = portableTriggers.map(t => {
        const tagId = t.assigned_tag_id;
        const tagData = tagsData[tagId];
        if (!tagData) return null;
        const radius = t.radius_ft;
        console.log(`Refreshing portable trigger ${t.i_trg} with center ${[tagData.y, tagData.x]} and radius ${radius}`);
        return {
          id: t.i_trg,
          name: t.x_nm_trg,
          center: [tagData.y, tagData.x],
          radius: radius,
          isPortable: true,
          assigned_tag_id: t.assigned_tag_id,
          radius_ft: t.radius_ft
        };
      });

      setExistingTriggerPolygons(prev => {
        const nonPortable = prev.filter(p => !p.isPortable || p.pending);
        const validPortable = updatedPolygons.filter(p => p);
        console.log("Refreshed existingTriggerPolygons:", [...nonPortable, ...validPortable]);
        return [...nonPortable, ...validPortable];
      });
    };

    refreshPortablePolygons();
  }, [triggers, selectedZone, tagsData, isConnected]);

  const handleDrawComplete = useCallback((coords) => {
    try {
      const parsed = Array.isArray(coords) ? coords : JSON.parse(coords);
      if (Array.isArray(parsed) && parsed.length >= 3) {
        const effectiveZMax = zMin === zMax && customZMax !== null ? Number(customZMax) : zMax;
        const formattedCoords = parsed.map((coord, index) => {
          const x = Number(coord.lng);
          const y = Number(coord.lat);
          if (isNaN(x) || isNaN(y)) throw new Error(`Invalid coordinates at index ${index}`);
          let n_z = index === 0 ? zMin : (index === 1 ? effectiveZMax : zMin);
          return { n_x: x.toFixed(6), n_y: y.toFixed(6), n_z: n_z };
        });
        console.log("Formatted coordinates:", formattedCoords);
        setCoordinates(formattedCoords);
      }
    } catch (e) {
      console.error("Error parsing draw coords:", e);
      alert("Failed to process drawn coordinates.");
    }
  }, [zMin, zMax, customZMax]);

  const handleZoneChange = (zoneId) => {
    const parsedZoneId = parseInt(zoneId);
    console.log("Selected zone ID:", parsedZoneId);
    const zone = zones.find(z => z.i_zn === parsedZoneId);
    console.log("Found zone:", zone);
    if (zone && (!selectedZone || zone.i_zn !== selectedZone.i_zn)) {
      setSelectedZone(zone);
      setCoordinates([]);
      setShowMapForDrawing(false);
      setZMin(null);
      setZMax(null);
      setCustomZMax(null);
      console.log("Updated selectedZone:", zone);
      setEventList(prev => [...prev, `Zone changed to ${zone.i_zn} - ${zone.x_nm_zn} on ${getFormattedTimestamp()}`]);
      hasPromptedForZone.current = false;
      if (isConnected && shouldReconnect.current) {
        console.log("Zone changed, reconnecting WebSocket with new zone_id:", zone.i_zn);
        connectWebSocket();
      }
    }
  };

  const retryReloadTriggers = async (retries = 3, delay = 1000) => {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const reloadRes = await fetch("http://192.168.210.226:8000/api/reload_triggers", {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        });
        if (!reloadRes.ok) throw new Error(`Failed to reload triggers: ${reloadRes.status}`);
        console.log("Successfully sent reload triggers request");
        return true;
      } catch (e) {
        console.error(`Attempt ${attempt} failed: ${e.message}`);
        if (attempt === retries) {
          console.error("All retry attempts failed.");
          return false;
        }
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    return false;
  };

  const handleCreateTrigger = async () => {
    if (!triggerName || !selectedZone || !triggerDirection) {
      alert("Please complete all fields.");
      return;
    }

    if (!showMapForDrawing) {
      setShowMapForDrawing(true);
      return;
    }

    if (coordinates.length < 3) {
      alert("Please draw a polygon with at least 3 points.");
      return;
    }

    const dir = triggerDirections.find(d => d.x_dir === triggerDirection);
    if (!dir) {
      alert("Invalid direction.");
      return;
    }

    const payload = {
      name: triggerName,
      direction: dir.i_dir,
      zone_id: parseInt(selectedZone.i_zn),
      ignore: false,
      vertices: coordinates.map(({ n_x, n_y, n_z }) => ({
        x: Number(n_x),
        y: Number(n_y),
        z: Number(n_z)
      }))
    };
    console.log("Creating trigger in zone:", selectedZone.i_zn);
    console.log("Payload after conversion:", JSON.stringify(payload, null, 2));

    try {
      const res = await fetch("http://192.168.210.226:8000/api/add_trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      alert(`Trigger ID: ${result.trigger_id}`);
      setEventList(prev => [...prev, `Trigger ${triggerName} created on ${getFormattedTimestamp()}`]);
      setCoordinates([]);
      setShowMapForDrawing(false);

      const reloadSuccess = await retryReloadTriggers(3, 1000);
      if (!reloadSuccess) {
        alert("Trigger created, but failed to reload triggers on the server. Please restart the WebSocket server or try again.");
      }

      await fetchTriggers();
    } catch (e) {
      console.error("Trigger create error:", e);
      alert("Failed to create trigger.");
    }
  };

  const handleDeleteTrigger = async (id) => {
    if (!window.confirm(`Delete trigger ID ${id}?`)) return;
    try {
      const res = await fetch(`http://192.168.210.226:8000/api/delete_trigger/${id}`, { method: "DELETE" });
      const result = await res.json();
      alert(`Deleted trigger ${id}`);
      setEventList(prev => [...prev, `Trigger ID ${id} deleted on ${getFormattedTimestamp()}`]);
      await fetchTriggers();

      const reloadSuccess = await retryReloadTriggers(3, 1000);
      if (!reloadSuccess) {
        alert("Trigger deleted, but failed to reload triggers on the server. Please restart the WebSocket server or try again.");
      }
    } catch (e) {
      console.error("Delete error:", e);
      alert("Failed to delete trigger.");
    }
  };

  const handleMoveTrigger = async (triggerId) => {
    const x = prompt("Enter new X coordinate:");
    const y = prompt("Enter new Y coordinate:");
    const z = prompt("Enter new Z coordinate:");
    if (x && y && z && !isNaN(x) && !isNaN(y) && !isNaN(z)) {
      await movePortableTrigger(triggerId, Number(x), Number(y), Number(z));
    } else {
      alert("Invalid coordinates entered.");
    }
  };

  const getDirectionName = (id) => triggerDirections.find(d => d.i_dir === id)?.x_dir || `ID ${id}`;

  const renderZoneOptions = (zoneList, indentLevel = 0) => {
    return zoneList.map(zone => (
      <React.Fragment key={zone.i_zn}>
        <option value={zone.i_zn}>
          {`${"  ".repeat(indentLevel)}${indentLevel > 0 ? "- " : ""}${zone.i_zn} - ${zone.x_nm_zn} (Level ${zone.i_typ_zn})`}
        </option>
        {zone.children && zone.children.length > 0 && renderZoneOptions(zone.children, indentLevel + 1)}
      </React.Fragment>
    ));
  };

  const infoLines = Object.values(tagsData).length > 0
    ? Object.values(tagsData).map(tagData =>
        `Tag ${tagData.id} (Zone ${tagData.zone_id || selectedZone?.i_zn || "N/A"} - ${zones.find(z => z.i_zn === (tagData.zone_id || selectedZone?.i_zn))?.x_nm_zn || "Unknown"}): X=${tagData.x}, Y=${tagData.y}, Z=${tagData.z}, Sequence=${tagData.sequence}, Counts=${tagCount}, Tags/sec=${tagRate.toFixed(2)}`
      ).join('\n')
    : "No tag data";

  return (
    <div>
      <h2>New Trigger Demo</h2>
      <Button variant="secondary" onClick={() => { setEventList([]); localStorage.setItem("eventList", JSON.stringify([])); }}>
        Clear System Events
      </Button>
      {fetchError && <div style={{ color: "red" }}>{fetchError}</div>}
      {loading && <p>Loading...</p>}
      <Tabs 
        defaultActiveKey="mapAndTrigger" 
        onSelect={(key) => setActiveTab(key)}
      >
        <Tab eventKey="mapAndTrigger" title="Map & Trigger">
          <Form.Group>
            <Form.Label>Tag IDs to Subscribe (comma-separated, e.g., SIM1,SIM2)</Form.Label>
            <InputGroup>
              <FormControl
                type="text"
                value={tagIdsInput}
                onChange={(e) => setTagIdsInput(e.target.value)}
                placeholder="Enter Tag IDs (e.g., SIM1,SIM2)"
                disabled={isConnected}
              />
              <Button
                variant={isConnected ? "danger" : "primary"}
                onClick={() => {
                  if (isConnected) {
                    disconnectWebSocket();
                  } else {
                    shouldReconnect.current = true;
                    connectWebSocket();
                  }
                }}
                disabled={!tagIdsInput}
              >
                {isConnected ? "Disconnect" : "Connect"}
              </Button>
            </InputGroup>
          </Form.Group>

          {Object.values(tagsData).length > 0 && (
            <div style={{ marginTop: "10px", whiteSpace: "pre-wrap" }}>
              <p>{infoLines}</p>
            </div>
          )}

          <div style={{ marginTop: "10px" }}>
            <h3>Trigger Events</h3>
            <FormCheck
              type="checkbox"
              label="Show Trigger Events"
              checked={showTriggerEvents}
              onChange={(e) => setShowTriggerEvents(e.target.checked)}
              style={{ marginBottom: "10px" }}
            />
            {triggerEvents.length === 0 ? (
              <p>No trigger events recorded.</p>
            ) : (
              <div style={{ maxHeight: "200px", overflowY: "auto", border: "1px solid #ccc", padding: "10px" }}>
                <ul style={{ margin: 0, padding: 0, listStyleType: "none" }}>
                  {triggerEvents.map((event, index) => (
                    <li key={index}>{event}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <Form.Group>
            <Form.Label>Trigger Name</Form.Label>
            <Form.Control type="text" value={triggerName} onChange={e => setTriggerName(e.target.value)} />
          </Form.Group>

          <Form.Group>
            <Form.Label>Select Zone</Form.Label>
            <Form.Control as="select" value={selectedZone?.i_zn || ""} onChange={e => handleZoneChange(e.target.value)}>
              <option value="">-- Choose Zone --</option>
              {renderZoneOptions(zoneHierarchy)}
            </Form.Control>
          </Form.Group>

          <Form.Group>
            <Form.Label>Z Min: {zMin !== null ? zMin : 'N/A'}</Form.Label>
          </Form.Group>

          <Form.Group>
            <Form.Label>Z Max: {zMax !== null ? zMax : 'N/A'}</Form.Label>
            {zMin !== null && zMax !== null && zMin === zMax && (
              <InputGroup className="mt-2">
                <InputGroup.Text>Modify Z Max</InputGroup.Text>
                <FormControl
                  type="number"
                  value={customZMax || ''}
                  onChange={e => setCustomZMax(e.target.value)}
                  placeholder="Enter new Z Max"
                />
              </InputGroup>
            )}
          </Form.Group>

          <Form.Group>
            <Form.Label>Direction</Form.Label>
            <Form.Control as="select" value={triggerDirection} onChange={e => setTriggerDirection(e.target.value)}>
              <option value="">Select Direction</option>
              {triggerDirections.map(d => (
                <option key={d.i_dir} value={d.x_dir}>{d.x_dir}</option>
              ))}
            </Form.Control>
          </Form.Group>

          <Button onClick={handleCreateTrigger}>{showMapForDrawing ? "Save Trigger" : "Create Trigger"}</Button>

          <FormCheck
            type="checkbox"
            label="Show Existing Triggers"
            checked={showExistingTriggers}
            onChange={e => setShowExistingTriggers(e.target.checked)}
            style={{ marginTop: "10px" }}
          />

          {selectedZone && activeTab === "mapAndTrigger" && (
            <div style={{ marginTop: "15px" }}>
              <strong>Zone Preview:</strong>
              {selectedZone.i_map ? (
                <NewTriggerViewer
                  mapId={selectedZone.i_map}
                  zones={[selectedZone]}
                  checkedZones={[selectedZone.i_zn]}
                  vertices={zoneVertices}
                  useLeaflet={useLeaflet}
                  enableDrawing={showMapForDrawing}
                  onDrawComplete={handleDrawComplete}
                  showExistingTriggers={showExistingTriggers}
                  existingTriggerPolygons={existingTriggerPolygons.map(p => ({
                    ...p,
                    isContained: p.isPortable ? Object.keys(portableTriggerContainment[p.id] || {}).some(tagId => portableTriggerContainment[p.id][tagId]) : false
                  }))}
                  tagsData={tagsData}
                  isConnected={isConnected}
                  triggers={triggers}
                />
              ) : (
                <div style={{ color: "red" }}>No map ID available for this zone.</div>
              )}
            </div>
          )}
        </Tab>

        <Tab eventKey="deleteTriggers" title="Delete Triggers">
          {triggers.length === 0 ? <p>No triggers found.</p> : (
            <Table striped bordered hover>
              <thead>
                <tr><th>ID</th><th>Name</th><th>Direction</th><th>Zone</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {triggers.map(t => (
                  <tr key={t.i_trg}>
                    <td>{t.i_trg}</td>
                    <td>{t.x_nm_trg}</td>
                    <td>{getDirectionName(t.i_dir)}</td>
                    <td>{t.zone_name || "Unknown"}</td>
                    <td>
                      <Button variant="danger" onClick={() => handleDeleteTrigger(t.i_trg)}>Delete</Button>
                      {t.is_portable && (
                        <Button
                          variant="primary"
                          onClick={() => handleMoveTrigger(t.i_trg)}
                          style={{ marginLeft: "10px" }}
                        >
                          Move
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Tab>

        <Tab eventKey="events" title="System Events">
          {eventList.length === 0 ? <p>No system events recorded.</p> : (
            <ul>{eventList.map((e, i) => <li key={i}>{e}</li>)}</ul>
          )}
        </Tab>
      </Tabs>
    </div>
  );
};

export default NewTriggerDemo;