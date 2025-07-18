/* Name: useRealTimeUpdates.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: React hook for real-time WebSocket updates and port monitoring */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useEffect, useRef, useCallback } from 'react';
import { config } from '../../../config';

export const useRealTimeUpdates = (options = {}) => {
    const {
        autoConnect = true,
        reconnectAttempts = 5,
        reconnectInterval = 3000,
        pingInterval = 30000,
        managerId = 'ControlManager'
    } = options;

    const [realTimeData, setRealTimeData] = useState({});
    const [isConnected, setIsConnected] = useState(false);
    const [connectionError, setConnectionError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [connectionStats, setConnectionStats] = useState({
        attempts: 0,
        totalReconnects: 0,
        messagesReceived: 0,
        lastHeartbeat: null
    });

    const wsRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const pingTimeoutRef = useRef(null);
    const shouldReconnectRef = useRef(autoConnect);
    const reconnectCountRef = useRef(0);

    // Connection setup
    const connect = useCallback(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            console.log('⚠️ WebSocket already connected');
            return;
        }

        // Use existing config structure - Control WebSocket is on port 8001
        const wsUrl = `ws://${config.API_BASE_URL.replace('http://', '').replace(':8000', ':8001')}/ws/${managerId}`;
        
        console.log(`🔌 Connecting to real-time WebSocket: ${wsUrl}`);
        setConnectionStats(prev => ({ ...prev, attempts: prev.attempts + 1 }));

        try {
            wsRef.current = new WebSocket(wsUrl);

            wsRef.current.onopen = () => {
                console.log('✅ Real-time WebSocket connected');
                setIsConnected(true);
                setConnectionError(null);
                reconnectCountRef.current = 0;
                
                setConnectionStats(prev => ({
                    ...prev,
                    lastHeartbeat: new Date()
                }));

                // Start ping interval
                startPingInterval();
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                    
                    setConnectionStats(prev => ({
                        ...prev,
                        messagesReceived: prev.messagesReceived + 1,
                        lastHeartbeat: new Date()
                    }));
                } catch (error) {
                    console.error('❌ Error parsing WebSocket message:', error);
                }
            };

            wsRef.current.onclose = (event) => {
                console.log(`🔌 Real-time WebSocket disconnected: ${event.code} - ${event.reason}`);
                setIsConnected(false);
                stopPingInterval();

                if (shouldReconnectRef.current && reconnectCountRef.current < reconnectAttempts) {
                    reconnectCountRef.current++;
                    setConnectionStats(prev => ({
                        ...prev,
                        totalReconnects: prev.totalReconnects + 1
                    }));
                    
                    console.log(`🔄 Attempting reconnect ${reconnectCountRef.current}/${reconnectAttempts} in ${reconnectInterval}ms`);
                    
                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect();
                    }, reconnectInterval);
                } else {
                    console.log('❌ Max reconnection attempts reached or reconnection disabled');
                    setConnectionError('Connection lost - max reconnection attempts reached');
                }
            };

            wsRef.current.onerror = (error) => {
                console.error('❌ Real-time WebSocket error:', error);
                setConnectionError('WebSocket connection error');
            };

        } catch (error) {
            console.error('❌ Failed to create WebSocket connection:', error);
            setConnectionError(`Failed to connect: ${error.message}`);
        }
    }, [managerId, reconnectAttempts, reconnectInterval]);

    // Handle incoming messages
    const handleMessage = useCallback((data) => {
        console.log('📨 Real-time message received:', data.type || 'unknown');

        switch (data.type) {
            case 'HeartBeat':
                handleHeartbeat(data);
                break;
            case 'PortRedirect':
                handlePortRedirect(data);
                break;
            case 'GISData':
                handleGISData(data);
                break;
            case 'PortHealth':
                handlePortHealth(data);
                break;
            case 'ScalingEvent':
                handleScalingEvent(data);
                break;
            case 'EndStream':
                handleEndStream(data);
                break;
            default:
                console.log('📝 Unhandled message type:', data.type, data);
        }

        setLastUpdate(new Date());
    }, []);

    // Message handlers
    const handleHeartbeat = useCallback((data) => {
        if (data.heartbeat_id) {
            const response = {
                type: 'HeartBeat',
                heartbeat_id: data.heartbeat_id,
                ts: Date.now(),
                source: 'ScalingManager'
            };
            
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify(response));
                console.log('💓 Heartbeat response sent:', data.heartbeat_id);
            }
        }
    }, []);

    const handlePortRedirect = useCallback((data) => {
        console.log('🔄 Port redirect received:', data);
        // Could be used to establish additional connections or update routing
        setRealTimeData(prev => ({
            ...prev,
            redirects: [...(prev.redirects || []), {
                ...data,
                timestamp: new Date()
            }]
        }));
    }, []);

    const handleGISData = useCallback((data) => {
        // Real-time coordinate data
        setRealTimeData(prev => ({
            ...prev,
            gisData: {
                ...data,
                timestamp: new Date()
            }
        }));
    }, []);

    const handlePortHealth = useCallback((data) => {
        // Port health updates
        setRealTimeData(prev => ({
            ...prev,
            portHealth: {
                ...prev.portHealth,
                [data.port]: {
                    ...data,
                    timestamp: new Date()
                }
            }
        }));
    }, []);

    const handleScalingEvent = useCallback((data) => {
        // Scaling events (port created, removed, etc.)
        console.log('⚡ Scaling event:', data);
        setRealTimeData(prev => ({
            ...prev,
            scalingEvents: [...(prev.scalingEvents || []), {
                ...data,
                timestamp: new Date()
            }].slice(-50) // Keep last 50 events
        }));
    }, []);

    const handleEndStream = useCallback((data) => {
        console.log('🔚 EndStream received:', data);
        disconnect();
    }, []);

    // Ping interval management
    const startPingInterval = useCallback(() => {
        stopPingInterval();
        
        pingTimeoutRef.current = setInterval(() => {
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                const pingMessage = {
                    type: 'ping',
                    timestamp: Date.now(),
                    source: 'ScalingManager'
                };
                
                wsRef.current.send(JSON.stringify(pingMessage));
                console.log('🏓 Ping sent to maintain connection');
            }
        }, pingInterval);
    }, [pingInterval]);

    const stopPingInterval = useCallback(() => {
        if (pingTimeoutRef.current) {
            clearInterval(pingTimeoutRef.current);
            pingTimeoutRef.current = null;
        }
    }, []);

    // Connection management
    const disconnect = useCallback(() => {
        console.log('🔌 Disconnecting real-time WebSocket');
        shouldReconnectRef.current = false;
        
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }
        
        stopPingInterval();
        
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        
        setIsConnected(false);
    }, [stopPingInterval]);

    const reconnect = useCallback(() => {
        console.log('🔄 Manual reconnection requested');
        shouldReconnectRef.current = true;
        reconnectCountRef.current = 0;
        disconnect();
        setTimeout(connect, 1000);
    }, [connect, disconnect]);

    // Send message
    const sendMessage = useCallback((message) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
            console.log('📤 Message sent:', message.type || 'unknown');
            return true;
        } else {
            console.warn('⚠️ Cannot send message - WebSocket not connected');
            return false;
        }
    }, []);

    // Subscribe to specific port updates
    const subscribeToPort = useCallback((port) => {
        const subscribeMessage = {
            type: 'subscribe',
            port,
            timestamp: Date.now()
        };
        
        return sendMessage(subscribeMessage);
    }, [sendMessage]);

    // Request port health update
    const requestHealthUpdate = useCallback((port = null) => {
        const healthRequest = {
            type: 'healthRequest',
            port,
            timestamp: Date.now()
        };
        
        return sendMessage(healthRequest);
    }, [sendMessage]);

    // Effect for auto-connection
    useEffect(() => {
        if (autoConnect) {
            connect();
        }

        return () => {
            shouldReconnectRef.current = false;
            disconnect();
        };
    }, [autoConnect, connect, disconnect]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            stopPingInterval();
        };
    }, [stopPingInterval]);

    // Listen for custom events from other components
    useEffect(() => {
        const handleScalingManagerEvent = (event) => {
            switch (event.type) {
                case 'scalingManager:retryConnection':
                    reconnect();
                    break;
                case 'scalingManager:refreshHealth':
                    requestHealthUpdate();
                    break;
                default:
                    console.log('🔔 Unhandled scaling manager event:', event.type);
            }
        };

        window.addEventListener('scalingManager:retryConnection', handleScalingManagerEvent);
        window.addEventListener('scalingManager:refreshHealth', handleScalingManagerEvent);

        return () => {
            window.removeEventListener('scalingManager:retryConnection', handleScalingManagerEvent);
            window.removeEventListener('scalingManager:refreshHealth', handleScalingManagerEvent);
        };
    }, [reconnect, requestHealthUpdate]);

    return {
        // Data
        realTimeData,
        lastUpdate,
        connectionStats,
        
        // State
        isConnected,
        connectionError,
        
        // Actions
        connect,
        disconnect,
        reconnect,
        sendMessage,
        subscribeToPort,
        requestHealthUpdate,
        
        // Connection info
        isReconnecting: reconnectCountRef.current > 0 && reconnectCountRef.current < reconnectAttempts,
        reconnectCount: reconnectCountRef.current,
        maxReconnectAttempts: reconnectAttempts
    };
};