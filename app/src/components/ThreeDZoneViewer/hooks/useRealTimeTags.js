/* Name: useRealTimeTags.js */
/* Version: 0.1.3 */
/* Created: 250722 */
/* Modified: 250723 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: UNIVERSAL TAG VISIBILITY - Fixed tag filtering to ensure all received tags are visible regardless of zone categorization */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.3: UNIVERSAL TAG VISIBILITY - Fixed selectAllTags to include all categories, enhanced getDisplayTags to show all selected tags regardless of zone */
/* - 0.1.2: ALLTRAQ ZONE FILTERING - Added zone 451 filtering, alltraq tag categorization, enhanced zone-based display */
/* - 0.1.1: WEBSOCKET MESSAGE FIX - Fixed HeartBeat handling, enhanced GISData parsing, improved subscription format */
/* - 0.1.0: Initial version - WebSocket connection to port 8002, ALL tag reception, local filtering */

import { useState, useRef, useCallback, useEffect } from 'react';

// Centralized configuration - dynamic server detection
const getServerHost = () => window.location.hostname || 'localhost';
const REALTIME_WS_URL = () => `ws://${getServerHost()}:8002/ws/RealTimeManager`;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_INTERVAL = 5000;
const DATA_TIMEOUT = 60000; // 60 seconds
const UPDATE_THROTTLE = 1000; // 1 second for 3D updates

// NEW v0.1.2: Alltraq configuration
const ALLTRAQ_ZONE_ID = 451; // Boca campus zone for alltraq data
const BOCA_CAMPUS_ID = 449;  // Boca campus parent zone

export const useRealTimeTags = ({
  selectedCampusId = null,
  isEnabled = false,
  onConnectionChange = null,
  onTagUpdate = null,
  maxTagHistory = 50, // Maximum number of historical positions per tag
  // NEW v0.1.2: Zone filtering options
  enableAlltraqFiltering = true,  // Enable special handling for alltraq zone 451
  showAlltraqSeparately = true    // Show alltraq tags in separate category
}) => {
  console.log(`🏷️ useRealTimeTags v0.1.3: Initializing for campus ${selectedCampusId}, enabled: ${isEnabled}, alltraq filtering: ${enableAlltraqFiltering}`);

  // Connection state
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  // Tag data state
  const [allTagsData, setAllTagsData] = useState({}); // All received tags
  const [selectedTags, setSelectedTags] = useState(new Set()); // User-selected tags to display
  
  // NEW v0.1.2: Zone-categorized tag data
  const [alltraqTags, setAlltraqTags] = useState({}); // Tags specifically from zone 451
  const [campusTags, setCampusTags] = useState({});   // Tags from selected campus (not zone 451)
  const [otherTags, setOtherTags] = useState({});     // Tags from other zones
  
  const [tagStats, setTagStats] = useState({
    totalTags: 0,
    activeTags: 0,
    tagRate: 0,
    lastUpdateTime: null,
    // NEW v0.1.2: Zone-specific stats
    alltraqCount: 0,
    campusCount: 0,
    otherCount: 0
  });
  
  // Tag history for trails
  const [tagHistory, setTagHistory] = useState({}); // tagId -> array of positions
  
  // WebSocket refs
  const wsRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const shouldReconnect = useRef(true);
  const lastDataTime = useRef(null);
  const lastUpdateTime = useRef(0);
  const tagTimestamps = useRef([]);
  
  // NEW v0.1.2: Enhanced GISData handler with zone filtering
  const handleGISDataMessage = useCallback((data) => {
    // Support multiple data formats
    const tagId = data.ID || data.id || data.tagId;
    const x = parseFloat(data.X || data.x);
    const y = parseFloat(data.Y || data.y); 
    const z = parseFloat(data.Z || data.z || 0);
    const sequence = data.Sequence || data.sequence || 0;
    const zoneId = data.zone_id || data.zoneId;

    if (!tagId || isNaN(x) || isNaN(y)) {
      console.warn(`⚠️ Invalid GISData message format:`, data);
      return;
    }

    // NEW v0.1.2: Determine tag category based on zone
    let tagCategory = 'other';
    let isAlltraqTag = false;
    
    if (zoneId === ALLTRAQ_ZONE_ID || zoneId === BOCA_CAMPUS_ID) {
      tagCategory = 'alltraq';
      isAlltraqTag = true;
      console.log(`🎯 Alltraq tag detected: ${tagId} in zone ${zoneId}`);
    } else if (selectedCampusId && zoneId === selectedCampusId) {
      tagCategory = 'campus';
      console.log(`🏫 Campus tag detected: ${tagId} in zone ${zoneId}`);
    } else if (zoneId) {
      tagCategory = 'other';
      console.log(`🔄 Other zone tag: ${tagId} in zone ${zoneId}`);
    } else {
      tagCategory = 'unknown';
      console.log(`❓ Unknown zone tag: ${tagId}`);
    }

    console.log(`📊 Processing GISData for tag ${tagId} (${tagCategory}):`, {
      id: tagId,
      x: x,
      y: y,
      z: z,
      zone_id: zoneId,
      sequence: sequence,
      category: tagCategory,
      isAlltraq: isAlltraqTag
    });

    const now = Date.now();
    lastDataTime.current = now;
    
    // Throttle updates for performance
    if (now - lastUpdateTime.current < UPDATE_THROTTLE) return;
    lastUpdateTime.current = now;

    // Create tag data object with enhanced metadata
    const tagData = {
      id: tagId,
      x: x,
      y: y,
      z: z,
      zone_id: zoneId,
      sequence: sequence,
      timestamp: now,
      isActive: true,
      // NEW v0.1.2: Category metadata
      category: tagCategory,
      isAlltraq: isAlltraqTag,
      source: isAlltraqTag ? 'alltraq' : 'parco'
    };

    // Update all tags data
    setAllTagsData(prev => {
      const updated = {
        ...prev,
        [tagId]: tagData
      };
      console.log(`📍 Updated tag ${tagId} position: (${tagData.x.toFixed(2)}, ${tagData.y.toFixed(2)}, ${tagData.z.toFixed(2)}) [${tagCategory}]`);
      return updated;
    });

    // NEW v0.1.2: Update zone-categorized data
    if (tagCategory === 'alltraq') {
      setAlltraqTags(prev => ({
        ...prev,
        [tagId]: tagData
      }));
    } else if (tagCategory === 'campus') {
      setCampusTags(prev => ({
        ...prev,
        [tagId]: tagData
      }));
    } else {
      setOtherTags(prev => ({
        ...prev,
        [tagId]: tagData
      }));
    }

    // Update tag history for trails
    setTagHistory(prev => {
      const currentHistory = prev[tagId] || [];
      const newPosition = {
        x: tagData.x,
        y: tagData.y,
        z: tagData.z,
        timestamp: now,
        zone_id: zoneId,
        category: tagCategory
      };
      
      // Add new position and limit history
      const updatedHistory = [...currentHistory, newPosition].slice(-maxTagHistory);
      
      return {
        ...prev,
        [tagId]: updatedHistory
      };
    });

    // NEW v0.1.2: Update enhanced tag statistics
    setTagStats(prev => {
      // Calculate tag rate
      const windowStart = now - 10000; // 10 second window
      const newTimestamps = [...tagTimestamps.current, now].filter(ts => ts >= windowStart);
      tagTimestamps.current = newTimestamps;
      
      const timeSpan = newTimestamps.length > 1 ? 
        (newTimestamps[newTimestamps.length - 1] - newTimestamps[0]) / 1000 : 0;
      const rate = timeSpan > 0 ? (newTimestamps.length - 1) / timeSpan : 0;

      const newStats = {
        totalTags: prev.totalTags + 1,
        activeTags: Object.keys(allTagsData).length + 1, // +1 for current update
        tagRate: rate,
        lastUpdateTime: now,
        // Zone-specific counts will be updated via separate effect
        alltraqCount: prev.alltraqCount + (isAlltraqTag ? 1 : 0),
        campusCount: prev.campusCount + (tagCategory === 'campus' ? 1 : 0),
        otherCount: prev.otherCount + (tagCategory === 'other' ? 1 : 0)
      };

      console.log(`📈 Tag stats updated:`, newStats);
      return newStats;
    });

    // Callback for external handling
    if (onTagUpdate) {
      onTagUpdate(tagData);
    }
  }, [onTagUpdate, maxTagHistory, allTagsData, selectedCampusId, enableAlltraqFiltering]);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log(`🔌 WebSocket already connected, skipping reconnect`);
      return;
    }

    if (!isEnabled || !selectedCampusId) {
      console.log(`⚠️ Connection skipped: enabled=${isEnabled}, campusId=${selectedCampusId}`);
      return;
    }

    const url = REALTIME_WS_URL();
    console.log(`🔗 Connecting to real-time WebSocket: ${url}`);
    
    setConnectionStatus('connecting');
    const ws = new WebSocket(url);
    wsRef.current = ws;
    reconnectAttempts.current = 0;

    ws.onopen = () => {
      console.log(`✅ Real-time WebSocket connected to RealTimeManager`);
      
      // NEW v0.1.2: Enhanced subscription for alltraq support
      const subscriptions = [
        // Format 1: Wildcard subscription (existing)
        {
          type: "request",
          request: "BeginStream", 
          reqid: "threeDZoneViewer_allTags",
          params: [{ id: "*", data: "true" }],
          zone_id: selectedCampusId
        },
        // NEW v0.1.2: Specific alltraq zone subscription
        {
          type: "request",
          request: "BeginStream",
          reqid: "threeDZoneViewer_alltraq", 
          params: [{ id: "*", data: "true" }],
          zone_id: ALLTRAQ_ZONE_ID
        },
        // Format 2: Specific simulator tags (based on your logs)
        {
          type: "request",
          request: "BeginStream",
          reqid: "threeDZoneViewer_simTags", 
          params: [
            { id: "SIM1", data: "true" },
            { id: "SIM2", data: "true" },
            { id: "SIM3", data: "true" },
            { id: "SIM4", data: "true" },
            { id: "SIM5", data: "true" }
          ],
          zone_id: selectedCampusId
        }
      ];
      
      subscriptions.forEach((subscription, index) => {
        console.log(`📡 Sending subscription ${index + 1}:`, subscription);
        ws.send(JSON.stringify(subscription));
      });
      
      setIsConnected(true);
      setConnectionStatus('connected');
      
      if (onConnectionChange) {
        onConnectionChange(true, 'connected');
      }
      
      console.log(`🔍 DEBUG: Enhanced subscription sent for campus ${selectedCampusId} + alltraq zone ${ALLTRAQ_ZONE_ID}`);
    };

    ws.onmessage = (event) => {
      console.log(`📨 Raw WebSocket message:`, event.data);
      
      let data;
      try {
        data = JSON.parse(event.data);
      } catch (e) {
        console.error(`❌ Failed to parse WebSocket message:`, e);
        return;
      }

      console.log(`📋 Parsed WebSocket message type: ${data.type}`, data);
      
      if (data.type === "GISData") {
        console.log(`🎯 Found GISData message!`, data);
        handleGISDataMessage(data);
      } else if (data.type === "HeartBeat") {
        // Handle both data.data.heartbeat_id and data.heartbeat_id formats
        const heartbeatId = data.data?.heartbeat_id || data.heartbeat_id;
        if (heartbeatId) {
          const response = {
            type: "HeartBeat",
            ts: data.ts,
            data: { heartbeat_id: heartbeatId }
          };
          ws.send(JSON.stringify(response));
          console.log(`💓 Sent heartbeat response: ${heartbeatId}`);
        }
        lastDataTime.current = Date.now();
      } else if (data.type === "response") {
        // Handle subscription response
        console.log(`📡 Subscription response: ${data.msg || 'OK'}`);
        lastDataTime.current = Date.now();
      } else {
        console.log(`🤷 Unhandled message type: ${data.type}`, data);
        // Log the full message to help debug the format
        console.log(`🔍 Full message data:`, JSON.stringify(data, null, 2));
      }
    };

    ws.onclose = (event) => {
      console.log(`🔌 WebSocket disconnected: code=${event.code}, reason=${event.reason}`);
      setIsConnected(false);
      setConnectionStatus('disconnected');
      wsRef.current = null;
      
      if (onConnectionChange) {
        onConnectionChange(false, 'disconnected');
      }
      
      // Auto-reconnect logic
      if (shouldReconnect.current && reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS && isEnabled) {
        reconnectAttempts.current += 1;
        console.log(`🔄 Attempting reconnect ${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS}...`);
        setTimeout(connect, RECONNECT_INTERVAL);
      } else {
        console.log(`❌ No more reconnect attempts or reconnect disabled`);
        setConnectionStatus('failed');
      }
    };

    ws.onerror = (error) => {
      console.error(`❌ WebSocket error:`, error);
      setConnectionStatus('error');
      
      if (onConnectionChange) {
        onConnectionChange(false, 'error');
      }
    };
  }, [isEnabled, selectedCampusId, handleGISDataMessage, onConnectionChange, enableAlltraqFiltering]);

  // Disconnect WebSocket
  const disconnect = useCallback(() => {
    console.log(`🔌 Disconnecting real-time WebSocket...`);
    shouldReconnect.current = false;
    
    if (wsRef.current) {
      if (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING) {
        wsRef.current.close();
      }
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setConnectionStatus('disconnected');
    setAllTagsData({});
    setTagHistory({});
    
    // NEW v0.1.2: Clear zone-categorized data
    setAlltraqTags({});
    setCampusTags({});
    setOtherTags({});
    
    setTagStats({
      totalTags: 0,
      activeTags: 0,
      tagRate: 0,
      lastUpdateTime: null,
      alltraqCount: 0,
      campusCount: 0,
      otherCount: 0
    });
    
    if (onConnectionChange) {
      onConnectionChange(false, 'disconnected');
    }
    
    console.log(`✅ Real-time WebSocket disconnected and cleaned up`);
  }, [onConnectionChange]);

  // Tag selection management
  const toggleTagSelection = useCallback((tagId) => {
    setSelectedTags(prev => {
      const updated = new Set(prev);
      if (updated.has(tagId)) {
        updated.delete(tagId);
        console.log(`➖ Removed tag ${tagId} from selection`);
      } else {
        updated.add(tagId);
        console.log(`➕ Added tag ${tagId} to selection`);
      }
      return updated;
    });
  }, []);

  // FIXED v0.1.3: Select all tags from ALL categories
  const selectAllTags = useCallback(() => {
    const allTagIds = Object.keys(allTagsData);
    setSelectedTags(new Set(allTagIds));
    console.log(`✅ Selected all ${allTagIds.length} tags from all categories`);
  }, [allTagsData]);

  // NEW v0.1.2: Zone-specific selection methods
  const selectAlltraqTags = useCallback(() => {
    const alltraqTagIds = Object.keys(alltraqTags);
    setSelectedTags(prev => new Set([...prev, ...alltraqTagIds]));
    console.log(`✅ Selected ${alltraqTagIds.length} alltraq tags`);
  }, [alltraqTags]);

  const selectCampusTags = useCallback(() => {
    const campusTagIds = Object.keys(campusTags);
    setSelectedTags(prev => new Set([...prev, ...campusTagIds]));
    console.log(`✅ Selected ${campusTagIds.length} campus tags`);
  }, [campusTags]);

  // NEW v0.1.3: Select other zone tags
  const selectOtherTags = useCallback(() => {
    const otherTagIds = Object.keys(otherTags);
    setSelectedTags(prev => new Set([...prev, ...otherTagIds]));
    console.log(`✅ Selected ${otherTagIds.length} other zone tags`);
  }, [otherTags]);

  const clearTagSelection = useCallback(() => {
    setSelectedTags(new Set());
    console.log(`🚫 Cleared all tag selections`);
  }, []);

  // FIXED v0.1.3: Get filtered tag data for display - includes ALL selected tags regardless of category
  const getDisplayTags = useCallback(() => {
    const filtered = {};
    selectedTags.forEach(tagId => {
      if (allTagsData[tagId]) {
        filtered[tagId] = allTagsData[tagId];
      }
    });
    console.log(`🎯 Display tags: ${Object.keys(filtered).length} selected from ${Object.keys(allTagsData).length} total (all categories included)`);
    return filtered;
  }, [allTagsData, selectedTags]);

  // NEW v0.1.2: Get alltraq-specific tags for display
  const getDisplayAlltraqTags = useCallback(() => {
    const filtered = {};
    selectedTags.forEach(tagId => {
      if (alltraqTags[tagId]) {
        filtered[tagId] = alltraqTags[tagId];
      }
    });
    console.log(`🎯 Alltraq display tags: ${Object.keys(filtered).length} selected from ${Object.keys(alltraqTags).length} total`);
    return filtered;
  }, [alltraqTags, selectedTags]);

  // Data timeout check
  useEffect(() => {
    const checkDataTimeout = () => {
      if (isConnected && lastDataTime.current) {
        const timeSinceLastData = Date.now() - lastDataTime.current;
        if (timeSinceLastData > DATA_TIMEOUT) {
          console.log(`⏰ No data received for ${DATA_TIMEOUT/1000} seconds, marking as disconnected`);
          setIsConnected(false);
          setConnectionStatus('timeout');
          
          if (onConnectionChange) {
            onConnectionChange(false, 'timeout');
          }
        }
      }
    };

    const interval = setInterval(checkDataTimeout, 5000);
    return () => clearInterval(interval);
  }, [isConnected, onConnectionChange]);

  // Auto-connect when enabled and campus selected
  useEffect(() => {
    if (isEnabled && selectedCampusId && !isConnected) {
      console.log(`🚀 Auto-connecting for campus ${selectedCampusId}...`);
      shouldReconnect.current = true;
      connect();
    } else if (!isEnabled && isConnected) {
      console.log(`⏹️ Disconnecting due to disabled state...`);
      disconnect();
    }
  }, [isEnabled, selectedCampusId, isConnected, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      console.log(`🧹 useRealTimeTags cleanup`);
      shouldReconnect.current = false;
      if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
        wsRef.current.close();
      }
    };
  }, []);

  console.log(`🏷️ useRealTimeTags v0.1.3 status:`, {
    isConnected,
    connectionStatus,
    totalTags: Object.keys(allTagsData).length,
    selectedTags: selectedTags.size,
    alltraqTags: Object.keys(alltraqTags).length,
    campusTags: Object.keys(campusTags).length,
    otherTags: Object.keys(otherTags).length,
    tagStats
  });

  return {
    // Connection state
    isConnected,
    connectionStatus,
    
    // Tag data
    allTagsData,
    displayTags: getDisplayTags(),
    tagHistory,
    tagStats,
    
    // NEW v0.1.2: Zone-categorized data
    alltraqTags,
    campusTags,
    otherTags,
    displayAlltraqTags: getDisplayAlltraqTags(),
    
    // Tag selection
    selectedTags,
    toggleTagSelection,
    selectAllTags,
    selectAlltraqTags,     // NEW
    selectCampusTags,      // NEW
    selectOtherTags,       // NEW v0.1.3
    clearTagSelection,
    
    // Connection controls
    connect,
    disconnect
  };
};