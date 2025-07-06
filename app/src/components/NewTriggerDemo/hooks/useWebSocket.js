/* Name: useWebSocket.js */
/* Version: 0.1.2 */
/* Created: 250625 */
/* Modified: 250705 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: WebSocket connection hook for NewTriggerDemo - Fixed sequence number debugging in trigger events */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useRef, useCallback, useEffect } from 'react';
import { getFormattedTimestamp, formatWebSocketStatus } from '../utils/formatters';
import { triggerApi } from '../services/triggerApi';

// Centralized configuration - dynamic server detection
const getServerHost = () => window.location.hostname || 'localhost';
const CONTROL_WS_URL = () => `ws://${getServerHost()}:8001/ws/ControlManager`;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_INTERVAL = 5000;
const DATA_TIMEOUT = 60000; // 60 seconds
const UPDATE_THROTTLE = 4000; // 4 seconds

export const useWebSocket = ({
  selectedZone,
  tagIdsInput,
  zones,
  setEventList,
  setTriggerEvents,
  showTriggerEventsRef,
  fetchTriggers,
  triggerDirections,
  triggers,
  setTriggers
}) => {
  // Connection state
  const [isConnected, setIsConnected] = useState(false);
  
  // Tag data state
  const [tagsData, setTagsData] = useState({});
  const [pendingTagsData, setPendingTagsData] = useState([]);
  const [sequenceNumbers, setSequenceNumbers] = useState({});
  const [tagCount, setTagCount] = useState(0);
  const [tagRate, setTagRate] = useState(0);
  const [tagTimestamps, setTagTimestamps] = useState([]);
  
  // WebSocket refs
  const wsRef = useRef(null);
  const streamWsRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const shouldReconnect = useRef(true);
  const lastDataTime = useRef(null);
  const hasPromptedForZone = useRef(false);
  const lastUpdateTime = useRef(0);

  // Handle GISData message
  const handleGISDataMessage = useCallback((data) => {
    const tagIds = tagIdsInput.split(',').map(id => id.trim()).filter(id => id);
    if (!tagIds.includes(data.ID)) {
      console.log(`Ignoring GISData for unsubscribed tag ${data.ID}`);
      return;
    }

    console.log("Processing GISData message:", JSON.stringify(data));
    setPendingTagsData(prev => [...prev, data]);

    const now = Date.now();
    if (now - lastUpdateTime.current < UPDATE_THROTTLE) return;
    lastUpdateTime.current = now;

    setPendingTagsData(prev => {
      const updates = [...prev];
      setPendingTagsData([]);
      
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
            // Note: Zone switching should be handled by parent component
            setEventList(prev => [...prev, 
              `Zone sync requested to ${zoneMatch.i_zn} - ${zoneMatch.x_nm_zn} on ${getFormattedTimestamp()}`
            ]);
          } else {
            console.log("User chose not to switch zones");
            setEventList(prev => [...prev, 
              `User declined to sync to Zone ${zoneMatch.i_zn} on ${getFormattedTimestamp()}`
            ]);
          }
          hasPromptedForZone.current = true;
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

        setSequenceNumbers(prev => {
          const updated = {
            ...prev,
            [data.ID]: data.Sequence || "N/A"
          };
          console.log(`Updated sequence for tag ${data.ID}: ${data.Sequence}, available keys:`, Object.keys(updated));
          return updated;
        });

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
  }, [tagIdsInput, selectedZone, zones, setEventList]);

  // Handle TriggerEvent message
  const handleTriggerEvent = useCallback(async (data) => {
    console.log("Processing TriggerEvent:", data);
    lastDataTime.current = Date.now();
    
    let trigger = triggers.find(t => t.i_trg === data.trigger_id);
    if (!trigger) {
      try {
        const triggerData = await triggerApi.getTriggerDetails(data.trigger_id);
        trigger = { 
          i_trg: data.trigger_id, 
          x_nm_trg: triggerData.name, 
          i_dir: triggerData.direction_id, 
          i_zn: data.zone_id || parseInt(selectedZone?.i_zn) 
        };
        setTriggers(prev => {
          const newTriggers = [...prev, trigger];
          console.log("Updated triggers:", newTriggers);
          return newTriggers;
        });
        console.log(`Fetched trigger details for ID ${data.trigger_id}:`, triggerData);
      } catch (e) {
        console.error(`Error fetching trigger details for ID ${data.trigger_id}:`, e);
        return;
      }
    }

    const zoneName = zones.find(z => z.i_zn === trigger.i_zn)?.x_nm_zn || "Unknown";
    
    // Enhanced sequence number lookup with debugging
    const tagId = data.tag_id;
    const sequenceFromNumbers = sequenceNumbers[tagId];
    const sequenceFromTagsData = tagsData[tagId]?.sequence;
    
    console.log(`Sequence lookup for tag ${tagId}:`, {
      sequenceFromNumbers,
      sequenceFromTagsData,
      availableKeys: Object.keys(sequenceNumbers)
    });
    
    const sequenceNumber = sequenceFromNumbers !== undefined ? sequenceFromNumbers : 
                          (sequenceFromTagsData !== undefined ? sequenceFromTagsData : "N/A");
    
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
  }, [triggers, zones, sequenceNumbers, tagsData, selectedZone, setTriggers, setTriggerEvents, showTriggerEventsRef, setEventList]);

  // Connect to stream WebSocket
  const connectStreamWebSocket = useCallback((url, tagIds) => {
    if (streamWsRef.current && streamWsRef.current.readyState === WebSocket.OPEN) {
      streamWsRef.current.close();
      console.log("Stream WebSocket close initiated due to reconnect");
    }

    console.log(`Connecting to stream WebSocket: ${url}`);
    const ws = new WebSocket(url);
    streamWsRef.current = ws;
    
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
      console.log(`Stream WebSocket disconnected with code: ${event.code}, reason: ${event.reason}`);
      streamWsRef.current = null;
      
      if (shouldReconnect.current && reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts.current += 1;
        console.log(`Attempting to reconnect stream WebSocket (${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS})...`);
        setTimeout(() => connectStreamWebSocket(url, tagIds), RECONNECT_INTERVAL);
      } else {
        console.log("Stream WebSocket closed, no reconnect attempted.");
      }
    };

    ws.onerror = (error) => {
      console.error("Stream WebSocket error:", error);
      streamWsRef.current = null;
      setEventList(prev => [...prev, 
        formatWebSocketStatus("Stream", "error", getFormattedTimestamp(), { error: error.message || 'Unknown error' })
      ]);
    };
  }, [selectedZone, handleGISDataMessage, handleTriggerEvent, setEventList]);

  // Connect to control WebSocket
  const connectWebSocket = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
      console.log("Control WebSocket close initiated due to reconnect");
    }

    const controlUrl = CONTROL_WS_URL();
    console.log(`Connecting to control WebSocket: ${controlUrl}`);
    const ws = new WebSocket(controlUrl);
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
      setEventList(prev => [...prev, 
        formatWebSocketStatus("Control", "connected", getFormattedTimestamp())
      ]);
      
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
        
        // Handle PortRedirect with just port (external systems) or full details (internal)
        if (port) {
          // Default to RealTimeManager on port 8002 if manager_name not provided
          const managerName = manager_name || "RealTimeManager";
          // Use centralized server host configuration
          const streamUrl = `ws://${getServerHost()}:${port}/ws/${managerName}`;
          console.log(`Connecting to stream WebSocket: ${streamUrl}`);
          console.log(`Using manager_name: ${managerName}, stream_type: ${stream_type || 'RealTime'}`);
          
          setTimeout(() => {
            const tagIds = tagIdsInput.split(',').map(id => id.trim()).filter(id => id);
            connectStreamWebSocket(streamUrl, tagIds);
          }, 2000);
        } else {
          console.log("PortRedirect missing required port field");
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
      console.log(`Control WebSocket disconnected with code: ${event.code}, reason: ${event.reason}`);
      setIsConnected(false);
      setTagRate(0);
      setTagsData({});
      setSequenceNumbers({});
      setEventList(prev => [...prev, 
        formatWebSocketStatus("Control", "disconnected", getFormattedTimestamp(), { code: event.code, reason: event.reason })
      ]);
      
      if (shouldReconnect.current && reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts.current += 1;
        console.log(`Attempting to reconnect control WebSocket (${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS})...`);
        setTimeout(connectWebSocket, RECONNECT_INTERVAL);
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
      setEventList(prev => [...prev, 
        formatWebSocketStatus("Control", "error", getFormattedTimestamp(), { error: error.message || 'Unknown error' })
      ]);
    };
  }, [tagIdsInput, selectedZone, fetchTriggers, handleGISDataMessage, handleTriggerEvent, connectStreamWebSocket, setEventList]);

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(async () => {
    shouldReconnect.current = false;
    
    if (wsRef.current) {
      if (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING) {
        wsRef.current.close();
        console.log("Control WebSocket close initiated");
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      setIsConnected(false);
      wsRef.current = null;
      setTagsData({});
      setSequenceNumbers({});
      setEventList(prev => [...prev, 
        formatWebSocketStatus("Control", "disconnected manually", getFormattedTimestamp())
      ]);
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
  }, [setEventList]);

  // Check for data timeout
  useEffect(() => {
    const checkDataTimeout = () => {
      if (isConnected && lastDataTime.current) {
        const timeSinceLastData = Date.now() - lastDataTime.current;
        if (timeSinceLastData > DATA_TIMEOUT) {
          console.log("No data received for 60 seconds, assuming disconnected");
          setIsConnected(false);
          setTagsData({});
          setSequenceNumbers({});
          setEventList(prev => [...prev, 
            `No data received for 60 seconds, assumed disconnected on ${getFormattedTimestamp()}`
          ]);
          hasPromptedForZone.current = false;
        }
      }
    };

    const interval = setInterval(checkDataTimeout, 1000);
    return () => clearInterval(interval);
  }, [isConnected, setEventList]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      shouldReconnect.current = false;
      if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
        wsRef.current.close();
      }
      if (streamWsRef.current && streamWsRef.current.readyState !== WebSocket.CLOSED) {
        streamWsRef.current.close();
      }
    };
  }, []);

  return {
    isConnected,
    tagsData,
    sequenceNumbers,
    tagCount,
    tagRate,
    connectWebSocket,
    disconnectWebSocket
  };
};