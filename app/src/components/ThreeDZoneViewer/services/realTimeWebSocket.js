/* Name: realTimeWebSocket.js */
/* Version: 0.1.0 */
/* Created: 250724 */
/* Modified: 250724 */
/* Creator: ParcoAdmin + Claude */
/* Description: Real-time WebSocket service for ParcoRTLS data streaming */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/services */
/* Role: Frontend Service */
/* Status: Active */
/* Dependent: TRUE */

// WebSocket configuration
const getServerHost = () => window.location.hostname || 'localhost';
const REALTIME_WS_URL = () => `ws://${getServerHost()}:8002/ws/RealTimeManager`;

/**
 * Real-time WebSocket service for managing connections to ParcoRTLS
 */
export class RealTimeWebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectInterval = 5000;
    this.shouldReconnect = true;
    this.messageHandlers = new Map();
    this.connectionListeners = new Set();
    this.heartbeatTimeout = null;
    this.stats = {
      connectAttempts: 0,
      messagesReceived: 0,
      messagesSent: 0,
      lastHeartbeat: null,
      connectionDuration: 0
    };
  }
  
  /**
   * Connect to WebSocket
   * @param {Object} options - Connection options
   * @param {string} options.manager - Manager name (default: RealTimeManager)
   * @returns {Promise<boolean>} Connection success
   */
  async connect(options = {}) {
    const { manager = 'RealTimeManager' } = options;
    
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log(`🔌 WebSocket already connected`);
      return true;
    }
    
    const url = `${REALTIME_WS_URL().replace('/RealTimeManager', '')}/${manager}`;
    console.log(`🔗 Connecting to WebSocket: ${url}`);
    
    this.stats.connectAttempts++;
    
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(url);
        
        this.ws.onopen = () => {
          console.log(`✅ WebSocket connected to ${manager}`);
          this.reconnectAttempts = 0;
          this.notifyConnectionChange(true, 'connected');
          resolve(true);
        };
        
        this.ws.onmessage = (event) => {
          this.handleMessage(event);
        };
        
        this.ws.onclose = (event) => {
          console.log(`🔌 WebSocket disconnected: code=${event.code}, reason=${event.reason}`);
          this.cleanup();
          this.notifyConnectionChange(false, 'disconnected');
          
          // Auto-reconnect if needed
          if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };
        
        this.ws.onerror = (error) => {
          console.error(`❌ WebSocket error:`, error);
          this.notifyConnectionChange(false, 'error');
          reject(error);
        };
        
      } catch (error) {
        console.error(`❌ Failed to create WebSocket:`, error);
        reject(error);
      }
    });
  }
  
  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    console.log(`🔌 Disconnecting WebSocket...`);
    this.shouldReconnect = false;
    
    if (this.ws) {
      if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
        this.ws.close(1000, 'Manual disconnect');
      }
    }
    
    this.cleanup();
    this.notifyConnectionChange(false, 'disconnected');
  }
  
  /**
   * Send message to WebSocket
   * @param {Object} message - Message object to send
   * @returns {boolean} Send success
   */
  send(message) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn(`⚠️ Cannot send message: WebSocket not connected`);
      return false;
    }
    
    try {
      const jsonMessage = JSON.stringify(message);
      this.ws.send(jsonMessage);
      this.stats.messagesSent++;
      console.log(`📤 Sent WebSocket message: ${message.type || 'unknown'}`, message);
      return true;
    } catch (error) {
      console.error(`❌ Error sending WebSocket message:`, error);
      return false;
    }
  }
  
  /**
   * Send multiple messages
   * @param {Array<Object>} messages - Array of message objects
   * @returns {number} Number of successfully sent messages
   */
  sendBatch(messages) {
    if (!Array.isArray(messages)) {
      console.warn(`⚠️ sendBatch expects an array of messages`);
      return 0;
    }
    
    let sentCount = 0;
    messages.forEach((message, index) => {
      if (this.send(message)) {
        sentCount++;
      } else {
        console.warn(`⚠️ Failed to send message ${index + 1}/${messages.length}`);
      }
    });
    
    console.log(`📤 Sent ${sentCount}/${messages.length} messages successfully`);
    return sentCount;
  }
  
  /**
   * Subscribe to real-time data
   * @param {Object} subscription - Subscription configuration
   * @param {string} subscription.reqid - Request ID
   * @param {Array} subscription.params - Subscription parameters
   * @param {number} subscription.zone_id - Zone ID
   * @returns {boolean} Subscription success
   */
  subscribe(subscription) {
    const message = {
      type: "request",
      request: "BeginStream",
      reqid: subscription.reqid || `subscription_${Date.now()}`,
      params: subscription.params || [],
      zone_id: subscription.zone_id
    };
    
    return this.send(message);
  }
  
  /**
   * Unsubscribe from real-time data
   * @param {string} reqid - Request ID to unsubscribe
   * @returns {boolean} Unsubscribe success
   */
  unsubscribe(reqid) {
    const message = {
      type: "request",
      request: "EndStream",
      reqid: reqid
    };
    
    return this.send(message);
  }
  
  /**
   * Register message handler
   * @param {string} messageType - Message type to handle
   * @param {Function} handler - Handler function
   */
  onMessage(messageType, handler) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, new Set());
    }
    this.messageHandlers.get(messageType).add(handler);
    console.log(`📝 Registered handler for message type: ${messageType}`);
  }
  
  /**
   * Remove message handler
   * @param {string} messageType - Message type
   * @param {Function} handler - Handler function to remove
   */
  offMessage(messageType, handler) {
    if (this.messageHandlers.has(messageType)) {
      this.messageHandlers.get(messageType).delete(handler);
    }
  }
  
  /**
   * Register connection change listener
   * @param {Function} listener - Connection change callback
   */
  onConnectionChange(listener) {
    this.connectionListeners.add(listener);
  }
  
  /**
   * Remove connection change listener
   * @param {Function} listener - Listener to remove
   */
  offConnectionChange(listener) {
    this.connectionListeners.delete(listener);
  }
  
  /**
   * Get connection status
   * @returns {Object} Connection status information
   */
  getStatus() {
    const readyState = this.ws ? this.ws.readyState : WebSocket.CLOSED;
    const stateNames = {
      [WebSocket.CONNECTING]: 'connecting',
      [WebSocket.OPEN]: 'connected',
      [WebSocket.CLOSING]: 'closing',
      [WebSocket.CLOSED]: 'disconnected'
    };
    
    return {
      connected: readyState === WebSocket.OPEN,
      state: stateNames[readyState] || 'unknown',
      reconnectAttempts: this.reconnectAttempts,
      stats: { ...this.stats }
    };
  }
  
  /**
   * Handle incoming WebSocket message
   * @private
   * @param {MessageEvent} event - WebSocket message event
   */
  handleMessage(event) {
    this.stats.messagesReceived++;
    
    let data;
    try {
      data = JSON.parse(event.data);
    } catch (error) {
      console.error(`❌ Failed to parse WebSocket message:`, error);
      return;
    }
    
    console.log(`📨 Received WebSocket message: ${data.type}`, data);
    
    // Handle heartbeat automatically
    if (data.type === "HeartBeat") {
      this.handleHeartbeat(data);
    }
    
    // Notify registered handlers
    if (this.messageHandlers.has(data.type)) {
      this.messageHandlers.get(data.type).forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`❌ Error in message handler for ${data.type}:`, error);
        }
      });
    }
    
    // Notify wildcard handlers
    if (this.messageHandlers.has('*')) {
      this.messageHandlers.get('*').forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`❌ Error in wildcard message handler:`, error);
        }
      });
    }
  }
  
  /**
   * Handle heartbeat message
   * @private
   * @param {Object} data - Heartbeat message data
   */
  handleHeartbeat(data) {
    const heartbeatId = data.data?.heartbeat_id || data.heartbeat_id;
    
    if (heartbeatId && this.ws && this.ws.readyState === WebSocket.OPEN) {
      const response = {
        type: "HeartBeat",
        ts: data.ts,
        data: { heartbeat_id: heartbeatId }
      };
      
      this.send(response);
      this.stats.lastHeartbeat = Date.now();
      console.log(`💓 Sent heartbeat response: ${heartbeatId}`);
      
      // Reset heartbeat timeout
      if (this.heartbeatTimeout) {
        clearTimeout(this.heartbeatTimeout);
      }
      
      this.heartbeatTimeout = setTimeout(() => {
        console.warn(`💔 Heartbeat timeout - no heartbeat for 35 seconds`);
        if (this.ws) {
          this.ws.close(1000, 'Heartbeat timeout');
        }
      }, 35000);
    }
  }
  
  /**
   * Schedule reconnection attempt
   * @private
   */
  scheduleReconnect() {
    this.reconnectAttempts++;
    console.log(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectInterval/1000}s`);
    
    setTimeout(() => {
      if (this.shouldReconnect) {
        this.connect();
      }
    }, this.reconnectInterval);
  }
  
  /**
   * Notify connection change listeners
   * @private
   * @param {boolean} connected - Connection state
   * @param {string} status - Status string
   */
  notifyConnectionChange(connected, status) {
    this.connectionListeners.forEach(listener => {
      try {
        listener(connected, status);
      } catch (error) {
        console.error(`❌ Error in connection change listener:`, error);
      }
    });
  }
  
  /**
   * Cleanup resources
   * @private
   */
  cleanup() {
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }
    
    this.ws = null;
  }
  
  /**
   * Reset connection state
   */
  reset() {
    this.disconnect();
    this.reconnectAttempts = 0;
    this.shouldReconnect = true;
    this.stats = {
      connectAttempts: 0,
      messagesReceived: 0,
      messagesSent: 0,
      lastHeartbeat: null,
      connectionDuration: 0
    };
    console.log(`🔄 WebSocket service reset`);
  }
}

// Export singleton instance
export const realTimeWebSocket = new RealTimeWebSocketService();
export default realTimeWebSocket;