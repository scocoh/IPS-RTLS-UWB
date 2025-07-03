/* Name: useTriggerContainment.js */
/* Version: 0.1.0 */
/* Created: 250625 */
/* Modified: 250625 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Trigger containment checking hook for NewTriggerDemo */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useCallback } from 'react';
import { triggerApi } from '../services/triggerApi';
import { zoneApi } from '../services/zoneApi';

export const useTriggerContainment = ({
  triggers,
  tagsData,
  selectedZone,
  zones,
  triggerDirections,
  showTriggerEventsRef,
  setTriggerEvents,
  getFormattedTimestamp
}) => {
  const [portableTriggerContainment, setPortableTriggerContainment] = useState({});
  const [triggerContainmentState, setTriggerContainmentState] = useState({});

  const checkTriggerContainment = useCallback(async (triggerId, tagId, x, y, z, isPortable) => {
    try {
      const trigger = triggers.find(t => t.i_trg === triggerId);
      if (!trigger) return;

      // Verify tag is in a valid zone
      const zoneData = await zoneApi.getZonesByPoint(x, y, z);
      if (!zoneData.length) {
        console.log(`Tag ${tagId} at (${x}, ${y}, ${z}) not in any zone, skipping containment check`);
        return;
      }

      let contains = false;
      
      if (isPortable && trigger.assigned_tag_id) {
        // Check portable trigger containment (client-side calculation)
        const assignedTagData = tagsData[trigger.assigned_tag_id];
        if (assignedTagData) {
          const dx = x - assignedTagData.x;
          const dy = y - assignedTagData.y;
          const dz = z - assignedTagData.z;
          const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
          contains = distance <= trigger.radius_ft;
          
          console.log(`Portable trigger ${triggerId} containment: tag ${tagId} at (${x}, ${y}, ${z}), ` +
            `center (${assignedTagData.x}, ${assignedTagData.y}, ${assignedTagData.z}), ` +
            `distance=${distance}, radius=${trigger.radius_ft}, contains=${contains}`);
        } else {
          console.log(`No position data for assigned tag ${trigger.assigned_tag_id} for portable trigger ${triggerId}`);
        }
      } else {
        // Check static trigger containment (server-side)
        const data = await triggerApi.checkTriggerContainment(triggerId, x, y, z);
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
          
          // Generate events based on trigger direction
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
  }, [triggers, tagsData, selectedZone, zones, triggerDirections, showTriggerEventsRef, setTriggerEvents, getFormattedTimestamp]);

  return {
    portableTriggerContainment,
    triggerContainmentState,
    checkTriggerContainment
  };
};