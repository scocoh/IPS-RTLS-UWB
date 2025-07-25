/* Name: useWebSocketConnection.js */
/* Version: 0.1.2 */
/* Created: 250724 */
/* Modified: 250724 */
/* Creator: ParcoAdmin + Claude */
/* Description: React hook for WebSocket connection management - HARDCODED TAG IDS to match 2D viewer approach */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/hooks */
/* Role: Frontend Hook */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.2: HARDCODED TAG IDS - Using exact same approach as working 2D viewer with 103 known tag IDs */
/* - 0.1.1: FIXED dependency loop causing connection failures - removed isConnected, connect, disconnect from effect dependencies */

import { useState, useRef, useCallback, useEffect } from 'react';

// WebSocket configuration - MATCHING 2D VIEWER APPROACH
const getServerHost = () => window.location.hostname || 'localhost';
const REALTIME_WS_URL = () => `ws://${getServerHost()}:8002/ws/RealTimeManager`;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_INTERVAL = 5000;
const DATA_TIMEOUT = 60000; // 60 seconds
const HEARTBEAT_TIMEOUT = 35000; // 35 seconds

// HARDCODED TAG IDS - All 103 AllTraq tags (exactly what 2D viewer receives)
const HARDCODED_TAG_IDS = [
  "26010","26011","26012","26014","26015","26016","26017","26018","26019","26020",
  "13351","13353","13355","13358","13359","26070","26071","26072","26073","26074",
  "26075","26076","26077","26079","26080","26081","26082","26083","26084","26085",
  "26086","26087","26088","26089","26090","26091","26092","26093","26094","26095",
  "26096","26097","26099","26100","26101","26102","26103","13356","26021","26022",
  "26023","26024","26025","26065","26027","26028","26029","26030","26031","26032",
  "26033","26034","26035","26036","26037","26039","26040","26041","26042","26043",
  "26044","26046","26047","26048","26049","26050","26051","26052","26053","26054",
  "26055","26056","26057","26058","26059","26060","13354","13360","13352","13357",
  "26063","26064","26005","26007","26008","26000","26001","26002","26009","26066",
  "26069","26067","26068"
];

/**
 * Hook for managing WebSocket connection to real-time data
 * @param {Object} options - Connection options
 * @param {boolean} options.enabled - Enable/disable connection
 * @param {Array} options.devices - Devices to subscribe to (IGNORED - using hardcoded list)
 * @param {number} options.selectedCampusId - Campus zone ID
 * @param {Function} options.onMessage - Message handler function
 * @param {Function} options.onConnectionChange - Connection status change handler
 * @param {boolean} options.enableAlltraqFiltering - Enable AllTraq filtering (IGNORED - hardcoded)
 * @returns {Object} WebSocket connection state and functions
 */
export const useWebSocketConnection = ({
  enabled = false,
  devices = [], // IGNORED - using hardcoded tag IDs
  selectedCampusId = null,
  onMessage = null,
  onConnectionChange = null,
  enableAlltraqFiltering = true // IGNORED - hardcoded approach
} = {}) => {
  console.log(`🔌 useWebSocketConnection v0.1.2: Using hardcoded ${HARDCODED_TAG_IDS.length} tag IDs (matching 2D viewer)`);
  
  // Connection state
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [lastDataTime, setLastDataTime] = useState(null);
  
  // Connection statistics
  const [stats, setStats] = useState({
    connectAttempts: 0,
    reconnectAttempts: 0,
    messagesReceived: 0,
    lastHeartbeat: null,
    subscriptionsSent: 0,
    connectionDuration: 0
  });
  
  // WebSocket refs
  const wsRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const shouldReconnect = useRef(true);
  const connectTime = useRef(null);
  const heartbeatTimeoutRef = useRef(null);
  
  /**
   * Update connection status and notify
   * @param {boolean} connected - Connection state
   * @param {string} status - Status string
   */
  const updateConnectionStatus = useCallback((connected, status) => {
    setIsConnected(connected);
    setConnectionStatus(status);
    
    if (onConnectionChange) {
      onConnectionChange(connected, status);
    }
    
    console.log(`🔌 Connection status: ${connected ? 'connected' : 'disconnected'} (${status})`);
  }, [onConnectionChange]);
  
  /**
   * Handle incoming WebSocket message
   * @param {MessageEvent} event - WebSocket message event
   */
  const handleMessage = useCallback((event) => {
    const now = Date.now();
    setLastDataTime(now);
    
    // Update message statistics
    setStats(prev => ({
      ...prev,
      messagesReceived: prev.messagesReceived + 1
    }));
    
    let data;
    try {
      data = JSON.parse(event.data);
    } catch (e) {
      console.error(`❌ Failed to parse WebSocket message:`, e);
      return;
    }
    
    console.log(`📨 WebSocket message: ${data.type}`, data);
    
    // Handle different message types
    if (data.type === "HeartBeat") {
      handleHeartbeat(data);
    } else if (data.type === "GISData") {
      // Forward GIS data to message handler
      if (onMessage) {
        onMessage(data);
      }
    } else if (data.type === "response") {
      console.log(`📡 Subscription response: ${data.msg || 'OK'}`);
    } else {
      console.log(`🤷 Unhandled message type: ${data.type}`);
    }
  }, [onMessage]);
  
  /**
   * Handle heartbeat message
   * @param {Object} data - Heartbeat message data
   */
  const handleHeartbeat = useCallback((data) => {
    const heartbeatId = data.data?.heartbeat_id || data.heartbeat_id;
    
    if (heartbeatId && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const response = {
        type: "HeartBeat",
        ts: data.ts,
        data: { heartbeat_id: heartbeatId }
      };
      
      wsRef.current.send(JSON.stringify(response));
      console.log(`💓 Sent heartbeat response: ${heartbeatId}`);
      
      // Update heartbeat statistics
      setStats(prev => ({
        ...prev,
        lastHeartbeat: Date.now()
      }));
      
      // Reset heartbeat timeout
      if (heartbeatTimeoutRef.current) {
        clearTimeout(heartbeatTimeoutRef.current);
      }
      
      heartbeatTimeoutRef.current = setTimeout(() => {
        console.warn(`💔 Heartbeat timeout - no heartbeat received for ${HEARTBEAT_TIMEOUT/1000}s`);
        if (wsRef.current) {
          wsRef.current.close(1000, 'Heartbeat timeout');
        }
      }, HEARTBEAT_TIMEOUT);
    }
  }, []);
  
  /**
   * Send hardcoded subscription (matching 2D viewer approach)
   */
  const sendHardcodedSubscription = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.warn(`⚠️ Cannot send subscription: WebSocket not connected`);
      return false;
    }
    
    // SIMPLE SUBSCRIPTION - Matching 2D viewer approach exactly
    const subscription = {
      type: "request",
      request: "BeginStream",
      reqid: "threeDZoneViewer_hardcoded_alltraq",
      params: HARDCODED_TAG_IDS.map(id => ({ id, data: "true" })),
      zone_id: selectedCampusId || 449 // Use selected campus or fallback to known working zone
    };
    
    try {
      wsRef.current.send(JSON.stringify(subscription));
      console.log(`📡 Sent hardcoded subscription for ${HARDCODED_TAG_IDS.length} tag IDs to zone ${subscription.zone_id}`);
      console.log(`📡 Subscription details:`, {
        reqid: subscription.reqid,
        tagCount: subscription.params.length,
        firstFewTags: HARDCODED_TAG_IDS.slice(0, 5),
        zone_id: subscription.zone_id
      });
      
      // Update statistics
      setStats(prev => ({
        ...prev,
        subscriptionsSent: prev.subscriptionsSent + 1
      }));
      
      return true;
    } catch (error) {
      console.error(`❌ Error sending hardcoded subscription:`, error);
      return false;
    }
  }, [selectedCampusId]);
  
  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log(`🔌 WebSocket already connected, skipping reconnect`);
      return;
    }
    
    if (!enabled) {
      console.log(`⚠️ Connection skipped: enabled=${enabled}`);
      return;
    }
    
    const url = REALTIME_WS_URL();
    console.log(`🔗 Connecting to WebSocket: ${url}`);
    
    updateConnectionStatus(false, 'connecting');
    
    // Update connection attempt statistics
    setStats(prev => ({
      ...prev,
      connectAttempts: prev.connectAttempts + 1,
      reconnectAttempts: reconnectAttempts.current
    }));
    
    const ws = new WebSocket(url);
    wsRef.current = ws;
    
    ws.onopen = () => {
      console.log(`✅ WebSocket connected to RealTimeManager`);
      connectTime.current = Date.now();
      reconnectAttempts.current = 0;
      
      updateConnectionStatus(true, 'connected');
      
      // Wait a moment for the connection to stabilize, then send hardcoded subscription
      setTimeout(() => {
        if (ws.readyState === WebSocket.OPEN) {
          sendHardcodedSubscription();
        } else {
          console.warn(`⚠️ WebSocket connection lost before sending subscription`);
        }
      }, 100); // Small delay to ensure connection is stable
    };
    
    ws.onmessage = handleMessage;
    
    ws.onclose = (event) => {
      console.log(`🔌 WebSocket disconnected: code=${event.code}, reason=${event.reason}`);
      
      updateConnectionStatus(false, 'disconnected');
      wsRef.current = null;
      connectTime.current = null;
      
      // Clear heartbeat timeout
      if (heartbeatTimeoutRef.current) {
        clearTimeout(heartbeatTimeoutRef.current);
        heartbeatTimeoutRef.current = null;
      }
      
      // Auto-reconnect logic
      if (shouldReconnect.current && reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS && enabled) {
        reconnectAttempts.current += 1;
        updateConnectionStatus(false, 'reconnecting');
        
        console.log(`🔄 Attempting reconnect ${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS}...`);
        setTimeout(connect, RECONNECT_INTERVAL);
      } else if (reconnectAttempts.current >= MAX_RECONNECT_ATTEMPTS) {
        console.log(`❌ Max reconnect attempts reached`);
        updateConnectionStatus(false, 'failed');
      }
    };
    
    ws.onerror = (error) => {
      console.error(`❌ WebSocket error:`, error);
      updateConnectionStatus(false, 'error');
    };
  }, [enabled, selectedCampusId, updateConnectionStatus, handleMessage, sendHardcodedSubscription]);
  
  /**
   * Disconnect from WebSocket
   */
  const disconnect = useCallback(() => {
    console.log(`🔌 Disconnecting WebSocket...`);
    shouldReconnect.current = false;
    
    // Clear heartbeat timeout
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      if (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING) {
        wsRef.current.close(1000, 'Manual disconnect');
      }
      wsRef.current = null;
    }
    
    updateConnectionStatus(false, 'disconnected');
    connectTime.current = null;
    setLastDataTime(null);
    
    console.log(`✅ WebSocket disconnected and cleaned up`);
  }, [updateConnectionStatus]);
  
  /**
   * Force reconnection
   */
  const reconnect = useCallback(() => {
    console.log(`🔄 Force reconnecting...`);
    disconnect();
    shouldReconnect.current = true;
    reconnectAttempts.current = 0;
    setTimeout(connect, 1000);
  }, [disconnect, connect]);
  
  /**
   * Check connection health
   * @returns {Object} Connection health information
   */
  const getConnectionHealth = useCallback(() => {
    const now = Date.now();
    const timeSinceConnect = connectTime.current ? now - connectTime.current : 0;
    const timeSinceData = lastDataTime ? now - lastDataTime : null;
    
    return {
      isHealthy: isConnected && (timeSinceData === null || timeSinceData < DATA_TIMEOUT),
      connectionDuration: timeSinceConnect,
      timeSinceLastData: timeSinceData,
      heartbeatAge: stats.lastHeartbeat ? now - stats.lastHeartbeat : null,
      reconnectAttempts: reconnectAttempts.current,
      hardcodedTagCount: HARDCODED_TAG_IDS.length
    };
  }, [isConnected, lastDataTime, stats.lastHeartbeat]);
  
  // Auto-connect when enabled (removed campus dependency for hardcoded approach)
  useEffect(() => {
    if (enabled && !isConnected && wsRef.current === null) {
      console.log(`🚀 Auto-connecting with hardcoded tag IDs...`);
      shouldReconnect.current = true;
      connect();
    } else if (!enabled && wsRef.current !== null) {
      console.log(`⏹️ Disconnecting due to disabled state...`);
      disconnect();
    }
  }, [enabled]); // Only enabled should trigger auto-connect for hardcoded approach
  
  // Update connection duration
  useEffect(() => {
    if (isConnected && connectTime.current) {
      const interval = setInterval(() => {
        setStats(prev => ({
          ...prev,
          connectionDuration: Date.now() - connectTime.current
        }));
      }, 1000);
      
      return () => clearInterval(interval);
    }
  }, [isConnected]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      console.log(`🧹 useWebSocketConnection cleanup`);
      shouldReconnect.current = false;
      if (heartbeatTimeoutRef.current) {
        clearTimeout(heartbeatTimeoutRef.current);
      }
      if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
        wsRef.current.close();
      }
    };
  }, []);
  
  console.log(`🔌 useWebSocketConnection v0.1.2 status:`, {
    isConnected,
    connectionStatus,
    hardcodedTagCount: HARDCODED_TAG_IDS.length,
    lastData: lastDataTime ? new Date(lastDataTime).toLocaleTimeString() : 'Never',
    stats: stats.messagesReceived
  });
  
  return {
    // State
    isConnected,
    connectionStatus,
    lastDataTime,
    stats,
    
    // Actions
    connect,
    disconnect,
    reconnect,
    sendSubscriptions: sendHardcodedSubscription, // Using hardcoded subscription
    
    // Getters
    getConnectionHealth
  };
};

export default useWebSocketConnection;