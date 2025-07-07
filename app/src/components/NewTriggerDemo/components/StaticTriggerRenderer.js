/* Name: StaticTriggerRenderer.js */
/* Version: 0.1.0 */
/* Created: 250707 */
/* Modified: 250707 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Static trigger renderer component - Handles static polygon triggers */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect } from "react";
import { triggerApi } from "../services/triggerApi";

const StaticTriggerRenderer = ({
  selectedZone,
  triggers,
  triggerStyle,
  onStaticTriggersUpdate
}) => {
  const [staticTriggerPolygons, setStaticTriggerPolygons] = useState([]);

  // Debug logging
  console.log("StaticTriggerRenderer DEBUG:", {
    selectedZone: selectedZone?.i_zn,
    totalTriggers: triggers?.length,
    staticTriggers: triggers?.filter(t => !t.is_portable)?.length,
    currentPolygons: staticTriggerPolygons.length
  });

  // Get static triggers for current zone
  const getStaticTriggers = () => {
    if (!selectedZone || !triggers) return [];
    
    const zoneTriggers = triggers.filter(t => 
      t.zone_id === parseInt(selectedZone.i_zn) || t.zone_id == null
    );
    
    const staticTriggers = zoneTriggers.filter(t => !t.is_portable);
    
    console.log(`🔷 Found ${staticTriggers.length} static triggers for zone ${selectedZone.i_zn}:`, 
      staticTriggers.map(t => `${t.i_trg}(${t.x_nm_trg})`));
    
    return staticTriggers;
  };

  // Fetch static trigger polygons
  const fetchStaticPolygons = async () => {
    const staticTriggers = getStaticTriggers();
    
    if (staticTriggers.length === 0) {
      console.log("🚫 No static triggers to fetch");
      setStaticTriggerPolygons([]);
      onStaticTriggersUpdate?.([]);
      return;
    }

    console.log("📡 Fetching static trigger polygon details...");
    
    try {
      const polygons = await Promise.all(
        staticTriggers.map(async (trigger) => {
          try {
            console.log(`🔍 Fetching details for static trigger ${trigger.i_trg} (${trigger.x_nm_trg})`);
            
            const data = await triggerApi.getTriggerDetails(trigger.i_trg);
            console.log(`📦 Trigger ${trigger.i_trg} details:`, data);
            
            if (Array.isArray(data.vertices) && data.vertices.length > 0) {
              const latLngs = data.vertices.map(v => [v.y, v.x]); // [lat, lng] format for Leaflet
              
              console.log(`✅ Trigger ${trigger.i_trg} has ${latLngs.length} vertices`);
              
              return {
                id: trigger.i_trg,
                name: trigger.x_nm_trg,
                latLngs,
                isPortable: false,
                style: {
                  fillOpacity: triggerStyle.staticFillOpacity / 100,
                  lineOpacity: triggerStyle.staticLineOpacity / 100,
                  color: triggerStyle.staticColor
                }
              };
            } else {
              console.warn(`⚠️ Trigger ${trigger.i_trg} has no valid vertices:`, data.vertices);
              return null;
            }
          } catch (error) {
            console.error(`❌ Failed to fetch details for trigger ${trigger.i_trg}:`, error);
            return null;
          }
        })
      );
      
      const validPolygons = polygons.filter(p => p);
      console.log(`✅ Created ${validPolygons.length} valid static polygons`);
      
      setStaticTriggerPolygons(validPolygons);
      onStaticTriggersUpdate?.(validPolygons);
      
    } catch (error) {
      console.error("❌ Failed to fetch static trigger polygons:", error);
      setStaticTriggerPolygons([]);
      onStaticTriggersUpdate?.([]);
    }
  };

  // Fetch polygons when zone or triggers change
  useEffect(() => {
    if (!selectedZone) {
      console.log("🚫 Clearing static triggers - no zone selected");
      setStaticTriggerPolygons([]);
      onStaticTriggersUpdate?.([]);
      return;
    }

    console.log("🚀 Fetching static triggers for zone", selectedZone.i_zn);
    fetchStaticPolygons();
  }, [selectedZone, triggers]);

  // Update styling when triggerStyle changes
  useEffect(() => {
    if (staticTriggerPolygons.length > 0) {
      console.log("🎨 Updating static trigger styling");
      
      const updatedPolygons = staticTriggerPolygons.map(polygon => ({
        ...polygon,
        style: {
          fillOpacity: triggerStyle.staticFillOpacity / 100,
          lineOpacity: triggerStyle.staticLineOpacity / 100,
          color: triggerStyle.staticColor
        }
      }));
      
      setStaticTriggerPolygons(updatedPolygons);
      onStaticTriggersUpdate?.(updatedPolygons);
    }
  }, [triggerStyle]);

  // This component doesn't render anything directly
  // It manages state and notifies parent via callback
  return null;
};

export default StaticTriggerRenderer;