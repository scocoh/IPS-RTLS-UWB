/* Name: PortableTriggerRenderer.js */
/* Version: 0.1.5 */
/* Created: 250707 */
/* Modified: 250707 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Portable trigger renderer component - FIXED: Added position debouncing and reduced update frequency */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect, useRef } from "react";

const PortableTriggerRenderer = ({
  selectedZone,
  triggers,
  tagsData,
  isConnected,
  triggerStyle,
  portableTriggerContainment,
  onPortableTriggersUpdate
}) => {
  const [portableTriggerPolygons, setPortableTriggerPolygons] = useState([]);
  const updateIntervalRef = useRef(null);
  const lastUpdateTimeRef = useRef({});
  const lastPositionsRef = useRef({}); // ADDED: Track actual positions
  const debounceTimersRef = useRef({}); // ADDED: Individual debounce timers

  // ADDED: Configuration constants - ADJUST THESE TO TUNE RESPONSE TIME vs STABILITY
  const UPDATE_INTERVAL_MS = 2000; // How often to check for updates (2000ms = 2 sec)
                                   // FASTER: 1000ms = more responsive but more CPU usage
                                   // SLOWER: 3000ms = less responsive but more stable
  
  const POSITION_DEBOUNCE_MS = 1000; // Delay before applying position change (1000ms = 1 sec)
                                     // FASTER: 500ms = quicker response, may be jittery with GPS noise
                                     // SLOWER: 1500ms = smoother movement, slower to respond
  
  const POSITION_THRESHOLD = 0.05; // Minimum distance to trigger update (0.05 units)
                                   // SMALLER: 0.01 = updates on tiny movements, very responsive but jittery
                                   // LARGER: 0.1 = only updates on significant moves, very smooth but less precise
                                   // NOTE: Adjust based on your coordinate system scale

  // ADDED: Helper to calculate distance between positions
  const calculateDistance = (pos1, pos2) => {
    if (!pos1 || !pos2) return Infinity;
    const dx = pos1.x - pos2.x;
    const dy = pos1.y - pos2.y;
    return Math.sqrt(dx * dx + dy * dy);
  };

  // Debug logging - REDUCED frequency
  const debugCount = useRef(0);
  const shouldDebug = () => {
    debugCount.current++;
    return debugCount.current % 10 === 1; // Only debug every 10th call
  };

  if (shouldDebug()) {
    console.log("PortableTriggerRenderer DEBUG:", {
      selectedZone: selectedZone?.i_zn,
      totalTriggers: triggers?.length,
      portableTriggers: triggers?.filter(t => t.is_portable)?.length,
      tagsDataKeys: Object.keys(tagsData || {}),
      tagsDataFull: tagsData,
      isConnected,
      currentPolygons: portableTriggerPolygons.length
    });
  }

  // Get portable triggers for current zone
  const getPortableTriggers = () => {
    if (!selectedZone || !triggers) return [];
    
    const zoneTriggers = triggers.filter(t => 
      t.zone_id === parseInt(selectedZone.i_zn) || t.zone_id == null
    );
    
    const portableTriggers = zoneTriggers.filter(t => t.is_portable);
    
    if (shouldDebug()) {
      console.log(`📍 Found ${portableTriggers.length} portable triggers for zone ${selectedZone.i_zn}:`, 
        portableTriggers.map(t => `${t.i_trg}(${t.x_nm_trg})`));
    }
    
    return portableTriggers;
  };

  // MODIFIED: Debounced position update function
  const updateTriggerPosition = (trigger, tagData) => {
    const triggerId = trigger.i_trg;
    const newPosition = { x: tagData.x, y: tagData.y };
    const lastPosition = lastPositionsRef.current[triggerId];
    
    // Check if position changed significantly
    const distance = calculateDistance(lastPosition, newPosition);
    if (distance < POSITION_THRESHOLD) {
      if (shouldDebug()) {
        console.log(`⏸️ Trigger ${triggerId} position unchanged: distance ${distance.toFixed(3)} < threshold ${POSITION_THRESHOLD}`);
      }
      return false; // No significant change
    }

    // Clear existing debounce timer
    if (debounceTimersRef.current[triggerId]) {
      clearTimeout(debounceTimersRef.current[triggerId]);
    }

    // Set new debounce timer
    debounceTimersRef.current[triggerId] = setTimeout(() => {
      const positionKey = `${newPosition.x.toFixed(2)}_${newPosition.y.toFixed(2)}`;
      const lastPositionKey = lastPosition ? `${lastPosition.x.toFixed(2)}_${lastPosition.y.toFixed(2)}` : 'none';
      
      console.log(`📍 Trigger ${triggerId} position changed: ${lastPositionKey} → ${positionKey} at ${new Date().toLocaleTimeString()}`);
      
      // Store the new position
      lastPositionsRef.current[triggerId] = newPosition;
      lastUpdateTimeRef.current[triggerId] = Date.now();
      
      // Update the polygon
      updatePortablePositions();
      
      // Clean up timer reference
      delete debounceTimersRef.current[triggerId];
    }, POSITION_DEBOUNCE_MS);

    return true; // Position update queued
  };

  // MODIFIED: Update portable trigger positions with debouncing
  const updatePortablePositions = () => {
    const portableTriggers = getPortableTriggers();
    
    if (portableTriggers.length === 0) {
      if (shouldDebug()) {
        console.log("🚫 No portable triggers to update");
      }
      setPortableTriggerPolygons([]);
      onPortableTriggersUpdate?.([]);
      return;
    }

    if (shouldDebug()) {
      console.log("🔄 Updating portable trigger positions...");
    }
    
    const updatedPolygons = portableTriggers.map(trigger => {
      const tagId = trigger.assigned_tag_id;
      const tagData = tagsData[tagId];
      
      if (!tagData) {
        if (shouldDebug()) {
          console.warn(`⚠️ No position data for tag ${tagId} assigned to trigger ${trigger.i_trg}`);
        }
        return {
          id: trigger.i_trg,
          name: trigger.x_nm_trg,
          isPortable: true,
          pending: true,
          assigned_tag_id: trigger.assigned_tag_id,
          radius_ft: trigger.radius_ft,
          style: {
            fillOpacity: triggerStyle.portableFillOpacity / 100,
            lineOpacity: triggerStyle.portableLineOpacity / 100,
            color: triggerStyle.portableColor
          }
        };
      }

      // Use stored position if available, otherwise current position
      const storedPosition = lastPositionsRef.current[trigger.i_trg];
      const currentPosition = storedPosition || { x: tagData.x, y: tagData.y };
      
      // Create position key for tracking
      const positionKey = `${currentPosition.x.toFixed(2)}_${currentPosition.y.toFixed(2)}`;

      const polygon = {
        id: trigger.i_trg,
        name: trigger.x_nm_trg,
        center: [currentPosition.y, currentPosition.x], // [lat, lng] format for Leaflet
        radius: trigger.radius_ft,
        isPortable: true,
        assigned_tag_id: trigger.assigned_tag_id,
        radius_ft: trigger.radius_ft,
        lastUpdate: Date.now(),
        positionKey: positionKey,
        uniqueKey: `${trigger.i_trg}-${positionKey}`,
        isContained: Object.keys(portableTriggerContainment[trigger.i_trg] || {}).some(
          tagId => portableTriggerContainment[trigger.i_trg][tagId]
        ),
        style: {
          fillOpacity: triggerStyle.portableFillOpacity / 100,
          lineOpacity: triggerStyle.portableLineOpacity / 100,
          color: triggerStyle.portableColor
        }
      };

      if (shouldDebug()) {
        console.log(`✅ Updated trigger ${trigger.i_trg} at [${currentPosition.y}, ${currentPosition.x}] radius ${trigger.radius_ft}ft at ${new Date().toLocaleTimeString()}`);
        console.log(`🔑 Unique key: ${polygon.uniqueKey}`);
      }
      
      return polygon;
    });

    // Filter out null results
    const validPolygons = updatedPolygons.filter(p => p);
    
    if (shouldDebug()) {
      console.log(`📊 Created ${validPolygons.length} valid portable polygons`);
    }
    
    // Update state
    setPortableTriggerPolygons(validPolygons);
    
    // Notify parent component
    onPortableTriggersUpdate?.(validPolygons);
  };

  // MODIFIED: Less frequent interval updates
  useEffect(() => {
    if (shouldDebug()) {
      console.log("🚀 Portable trigger interval useEffect triggered", {
        selectedZone: selectedZone?.i_zn,
        isConnected,
        hasUpdateInterval: !!updateIntervalRef.current
      });
    }
    
    if (!selectedZone || !isConnected) {
      if (shouldDebug()) {
        console.log("🚫 Clearing portable triggers - no zone or not connected");
      }
      setPortableTriggerPolygons([]);
      onPortableTriggersUpdate?.([]);
      
      if (updateIntervalRef.current) {
        clearInterval(updateIntervalRef.current);
        updateIntervalRef.current = null;
      }
      return;
    }

    if (shouldDebug()) {
      console.log("🚀 Starting portable trigger updates for zone", selectedZone.i_zn);
    }
    
    // Initial update
    updatePortablePositions();
    
    // Set up interval for periodic updates (REDUCED frequency)
    if (!updateIntervalRef.current) {
      updateIntervalRef.current = setInterval(updatePortablePositions, UPDATE_INTERVAL_MS);
      console.log(`⏰ Portable trigger update interval started (${UPDATE_INTERVAL_MS}ms)`);
    }

    return () => {
      if (updateIntervalRef.current) {
        clearInterval(updateIntervalRef.current);
        updateIntervalRef.current = null;
        console.log("🛑 Portable trigger update interval stopped");
      }
      
      // Clear all debounce timers
      Object.values(debounceTimersRef.current).forEach(timer => {
        if (timer) clearTimeout(timer);
      });
      debounceTimersRef.current = {};
    };
  }, [selectedZone, isConnected]);

  // MODIFIED: Smart dependency-based updates with debouncing
  useEffect(() => {
    if (!selectedZone || !isConnected || Object.keys(tagsData).length === 0) return;

    if (shouldDebug()) {
      console.log("🔄 Dependencies changed, updating portable positions");
    }
    
    // Check each portable trigger for position changes and debounce updates
    const portableTriggers = getPortableTriggers();
    let hasUpdates = false;
    
    portableTriggers.forEach(trigger => {
      const tagId = trigger.assigned_tag_id;
      const tagData = tagsData[tagId];
      
      if (tagData) {
        const updated = updateTriggerPosition(trigger, tagData);
        if (updated) hasUpdates = true;
      }
    });

    // If no debounced updates are pending, do immediate update for missing positions
    if (!hasUpdates) {
      updatePortablePositions();
    }
  }, [triggers, tagsData, triggerStyle, portableTriggerContainment]);

  // This component doesn't render anything directly
  // It manages state and notifies parent via callback
  return null;
};

export default PortableTriggerRenderer;