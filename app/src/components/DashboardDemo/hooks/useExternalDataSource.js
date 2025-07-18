/* Name: useExternalDataSource.js */
/* Version: 0.1.0 */
/* Created: 250714 */
/* Modified: 250714 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Vendor-neutral external data source WebSocket hook for ParcoRTLS Dashboard */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/DashboardDemo/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useEffect } from 'react';

const useExternalDataSource = (sourceId = 'AllTraqAppAPI', customerId = 1) => {
  const [tagPositions, setTagPositions] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [lastUpdate, setLastUpdate] = useState(null);
  const [messageCount, setMessageCount] = useState(0);
  const [activeDataSource, setActiveDataSource] = useState(sourceId);

  useEffect(() => {
    const ws = new WebSocket(`ws://192.168.210.226:8008/ws/dashboard/${customerId}`);
    
    ws.onopen = () => {
      setConnectionStatus('connected');
      console.log(`Connected to external data source: ${sourceId}`);
      // Send initial ping
      ws.send(JSON.stringify({ type: 'ping' }));
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'rtls_data') {
        // Filter data by source if multiple sources are active
        const relevantData = data.data.filter(item => {
          // This filtering logic can be enhanced based on data source metadata
          return true; // For now, accept all RTLS data
        });
        
        setTagPositions(prev => {
          // Update or add new tag positions
          const updated = [...prev];
          relevantData.forEach(newTag => {
            const existingIndex = updated.findIndex(t => t.tag_id === newTag.tag_id);
            if (existingIndex >= 0) {
              updated[existingIndex] = { ...newTag, source: sourceId };
            } else {
              updated.push({ ...newTag, source: sourceId });
            }
          });
          return updated;
        });
        setLastUpdate(new Date());
        setMessageCount(prev => prev + 1);
      }
    };
    
    ws.onclose = () => {
      setConnectionStatus('disconnected');
      console.log(`Disconnected from external data source: ${sourceId}`);
    };
    
    ws.onerror = () => {
      setConnectionStatus('error');
      console.error(`Error with external data source: ${sourceId}`);
    };
    
    return () => ws.close();
  }, [customerId, sourceId]);

  return {
    tagPositions,
    connectionStatus, 
    lastUpdate,
    messageCount,
    activeDataSource
  };
};

export default useExternalDataSource;