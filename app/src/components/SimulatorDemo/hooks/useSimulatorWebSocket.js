/* Name: useSimulatorWebSocket.js */
/* Version: 0.1.1 */
/* Created: 250707 */
/* Modified: 250707 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: WebSocket connection hook for SimulatorDemo */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/SimulatorDemo/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useRef, useCallback } from 'react';
import { config } from '../../../config.js';

const useSimulatorWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [error, setError] = useState(null);
  
  const controlWsRef = useRef(null);
  const streamWsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 3;

  const addLogEntry = useRef(() => {});

  // Set log callback
  const setLogCallback = useCallback((callback) => {
    addLogEntry.current = callback;
  }, []);

  // Connect to control WebSocket
  const connectControl = useCallback(async (tagConfigs, zoneId) => {
    try {
      if (controlWsRef.current && controlWsRef.current.readyState === WebSocket.OPEN) {
        controlWsRef.current.close();
      }

      const controlUri = `${config.WS_CONTROL_URL}/ws/ControlManager`;
      addLogEntry.current(`Connecting to control WebSocket: ${controlUri}`);
      
      const controlWs = new WebSocket(controlUri);
      controlWsRef.current = controlWs;

      return new Promise((resolve, reject) => {
        controlWs.onopen = () => {
          setIsConnected(true);
          setConnectionStatus('Connected to Control');
          setError(null);
          reconnectAttempts.current = 0;
          addLogEntry.current('Control WebSocket connected');
          
          // Send handshake
          const handshake = {
            type: "request",
            request: "BeginStream",
            reqid: "sim_init",
            params: tagConfigs.map(config => ({ id: config.tagId, data: "true" })),
            zone_id: zoneId
          };
          
          try {
            controlWs.send(JSON.stringify(handshake));
            addLogEntry.current(`Sent handshake for zone ${zoneId}`);
            resolve(controlWs);
          } catch (error) {
            addLogEntry.current(`Failed to send handshake: ${error.message}`);
            reject(error);
          }
        };

        controlWs.onmessage = async (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === "HeartBeat") {
              // Respond to heartbeat
              const heartbeatResponse = {
                type: "HeartBeat",
                heartbeat_id: data.heartbeat_id,
                ts: Date.now(),
                source: "simulator"
              };
              controlWs.send(JSON.stringify(heartbeatResponse));
            } else if (data.type === "PortRedirect") {
              // Handle port redirect to stream WebSocket
              const streamPort = data.port;
              addLogEntry.current(`Redirecting to stream port ${streamPort}`);
              await connectStream(streamPort);
              setConnectionStatus('Connected to Stream');
            } else if (data.type === "response") {
              addLogEntry.current(`Control response: ${data.message || 'OK'}`);
            }
          } catch (error) {
            addLogEntry.current(`Error parsing control message: ${error.message}`);
          }
        };

        controlWs.onclose = (event) => {
          setIsConnected(false);
          setConnectionStatus('Disconnected');
          addLogEntry.current(`Control WebSocket closed (code: ${event.code})`);
          
          // Attempt reconnection if not intentional close
          if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
            scheduleReconnect(tagConfigs, zoneId);
          }
        };

        controlWs.onerror = (error) => {
          setError(`Control WebSocket error: ${error.message}`);
          addLogEntry.current(`Control WebSocket error: ${error.message}`);
          reject(error);
        };
      });

    } catch (error) {
      setError(`Connection error: ${error.message}`);
      addLogEntry.current(`Connection error: ${error.message}`);
      throw error;
    }
  }, []);

  // Connect to stream WebSocket
  const connectStream = useCallback(async (port) => {
    try {
      if (streamWsRef.current && streamWsRef.current.readyState === WebSocket.OPEN) {
        streamWsRef.current.close();
      }

      // Extract host from API_BASE_URL properly
      const apiHost = config.API_BASE_URL.replace('http://', '').replace(':8000', '');
      const streamUri = `ws://${apiHost}:${port}/ws/RealTimeManager`;
      addLogEntry.current(`Connecting to stream WebSocket: ${streamUri}`);
      
      const streamWs = new WebSocket(streamUri);
      streamWsRef.current = streamWs;

      return new Promise((resolve, reject) => {
        streamWs.onopen = () => {
          setConnectionStatus('Connected to Stream');
          addLogEntry.current('Stream WebSocket connected');
          resolve(streamWs);
        };

        streamWs.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === "HeartBeat") {
              const heartbeatResponse = {
                type: "HeartBeat",
                heartbeat_id: data.heartbeat_id,
                ts: Date.now(),
                source: "simulator"
              };
              streamWs.send(JSON.stringify(heartbeatResponse));
            } else if (data.type === "TriggerEvent") {
              addLogEntry.current(`TriggerEvent: ${data.trigger_name} for tag ${data.tag_id}`);
            }
          } catch (error) {
            addLogEntry.current(`Error parsing stream message: ${error.message}`);
          }
        };

        streamWs.onclose = (event) => {
          addLogEntry.current(`Stream WebSocket closed (code: ${event.code})`);
        };

        streamWs.onerror = (error) => {
          addLogEntry.current(`Stream WebSocket error: ${error.message}`);
          reject(error);
        };
      });

    } catch (error) {
      addLogEntry.current(`Stream connection error: ${error.message}`);
      throw error;
    }
  }, []);

  // Schedule reconnection attempt
  const scheduleReconnect = useCallback((tagConfigs, zoneId) => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    reconnectAttempts.current++;
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000); // Exponential backoff, max 30s
    
    addLogEntry.current(`Scheduling reconnect attempt ${reconnectAttempts.current}/${maxReconnectAttempts} in ${delay}ms`);
    
    reconnectTimeoutRef.current = setTimeout(() => {
      connectControl(tagConfigs, zoneId).catch((error) => {
        addLogEntry.current(`Reconnect attempt ${reconnectAttempts.current} failed: ${error.message}`);
      });
    }, delay);
  }, [connectControl]);

  // Send GIS data message
  const sendGISData = useCallback((message) => {
    const targetWs = streamWsRef.current || controlWsRef.current;
    
    if (targetWs && targetWs.readyState === WebSocket.OPEN) {
      try {
        targetWs.send(JSON.stringify(message));
        return true;
      } catch (error) {
        addLogEntry.current(`Failed to send GIS data: ${error.message}`);
        return false;
      }
    } else {
      addLogEntry.current('No active WebSocket connection to send data');
      return false;
    }
  }, []);

  // Send end stream message
  const sendEndStream = useCallback(async () => {
    const endStreamMessage = {
      type: "request",
      request: "EndStream",
      reqid: "sim_end"
    };

    if (controlWsRef.current && controlWsRef.current.readyState === WebSocket.OPEN) {
      try {
        controlWsRef.current.send(JSON.stringify(endStreamMessage));
        addLogEntry.current('Sent EndStream message');
        
        // Wait for response
        await new Promise((resolve) => {
          const timeout = setTimeout(resolve, 5000); // 5 second timeout
          
          const originalOnMessage = controlWsRef.current.onmessage;
          controlWsRef.current.onmessage = (event) => {
            if (originalOnMessage) originalOnMessage(event);
            
            try {
              const data = JSON.parse(event.data);
              if (data.type === "response" && data.reqid === "sim_end") {
                clearTimeout(timeout);
                resolve();
              }
            } catch (error) {
              // Ignore parsing errors for EndStream response
            }
          };
        });
        
      } catch (error) {
        addLogEntry.current(`Failed to send EndStream: ${error.message}`);
      }
    }
  }, []);

  // Disconnect all WebSockets
  const disconnect = useCallback(async () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Send EndStream first
    await sendEndStream();

    // Close stream WebSocket
    if (streamWsRef.current) {
      streamWsRef.current.close(1000, 'Normal closure');
      streamWsRef.current = null;
    }

    // Close control WebSocket
    if (controlWsRef.current) {
      controlWsRef.current.close(1000, 'Normal closure');
      controlWsRef.current = null;
    }

    setIsConnected(false);
    setConnectionStatus('Disconnected');
    setError(null);
    reconnectAttempts.current = 0;
    addLogEntry.current('All WebSocket connections closed');
  }, [sendEndStream]);

  // Get current WebSocket state
  const getConnectionState = useCallback(() => {
    return {
      controlState: controlWsRef.current ? controlWsRef.current.readyState : WebSocket.CLOSED,
      streamState: streamWsRef.current ? streamWsRef.current.readyState : WebSocket.CLOSED,
      hasActiveConnection: isConnected && (
        (controlWsRef.current && controlWsRef.current.readyState === WebSocket.OPEN) ||
        (streamWsRef.current && streamWsRef.current.readyState === WebSocket.OPEN)
      )
    };
  }, [isConnected]);

  return {
    isConnected,
    connectionStatus,
    error,
    connectControl,
    connectStream,
    sendGISData,
    sendEndStream,
    disconnect,
    getConnectionState,
    setLogCallback
  };
};

export default useSimulatorWebSocket;