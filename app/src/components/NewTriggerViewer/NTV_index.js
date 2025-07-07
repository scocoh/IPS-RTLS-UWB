// components/NewTriggerViewer/NTV_index.js  • v0.2.9 - FIXED PORTABLE TRIGGER PERSISTENCE - NO MORE FLASHING
import React, { useRef, useState, useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./Map.css";   // ✔ local stylesheet

import { useMapSetup }   from "./hooks/useMapSetup";
import { useTagManager } from "./hooks/useTagManager";
import { useMapData }    from "./hooks/useMapData";
import { MapControls }   from "./components/MapControls";
import { Legend, TagControls } from "./components/MapUI";
import { useKeyboardShortcuts } from "../NewTriggerDemo/hooks/useKeyboardShortcuts"; // ✔ correct path

const NTV_index = ({
  mapId,
  zones,
  checkedZones,
  vertices,
  onVerticesUpdate,
  useLeaflet = true,
  enableDrawing = false,
  onDrawComplete,
  showExistingTriggers = true,
  showTriggerLabels = true, // Toggle for trigger ID labels
  existingTriggerPolygons = [],
  tagsData = {},
  propIsConnected = false,
  triggers = [],
  enableResponsive = true,
  enableControls = true,
  height = "600px",
  width = "100%",
  enableKeyboardShortcuts = true,
}) => {
  /* ─────────── refs / state ─────────── */
  const mapRef         = useRef(null);
  const mapInstanceRef = useRef(null);
  const isZoomingRef     = useRef(false);
  const pendingUpdateRef = useRef(false);
  
  // NEW: Portable trigger circle references (like tagMarkersRef)
  const portableTriggerCirclesRef = useRef({});
  const portableTriggerLabelsRef = useRef({});

  const [hiddenTags, setHiddenTags] = useState(new Set());
  const [showControls, setShowControls] = useState(enableControls);
  const [showLegend, setShowLegend]     = useState(true);
  const [mapMode, setMapMode]           = useState("view");
  const [mapInitialized, setMapInitialized] = useState(false);
  const [error, setError] = useState(null);

  /* ─────────── fetch map metadata ─────────── */
  const { mapData, isConnected } = useMapData({
    mapId,
    onError: setError,
  });

  /* ─────────── map setup ─────────── */
  useMapSetup({
    useLeaflet,
    mapRef,
    mapInstanceRef,
    mapData,
    enableDrawing,
    drawOptions: { onDrawComplete, onVerticesUpdate },
    enableControls: showControls,
    controlRefs: { isZoomingRef, pendingUpdateRef },
    onMapInitialized: () => {
      console.log("✅ Map initialization callback fired");
      setMapInitialized(true);
    },
  });

  /* ─────────── tag / trigger markers ─────────── */
  const { tagMarkersRef } = useTagManager({
    useLeaflet,
    mapInstanceRef,
    mapData,
    mapInitialized,
    zones,
    tagsData,
    triggers,
    hiddenTags,
    isConnected,
    isZoomingRef,
    pendingUpdateRef,
  });

  /* ─────────── FIXED: Portable trigger PERMANENT persistence system ─────────── */
  useEffect(() => {
    console.log("🟣 Portable trigger PERMANENT FIX useEffect triggered", {
      mapInitialized,
      hasMapInstance: !!mapInstanceRef.current,
      polygonCount: existingTriggerPolygons?.length,
      tagsDataKeys: Object.keys(tagsData)
    });

    if (!useLeaflet || !mapInstanceRef.current || !mapData || !mapInitialized) {
      console.log("🟣 Portable trigger updates skipped - map not ready");
      return;
    }

    // Get current portable triggers from polygons
    const portableTriggers = existingTriggerPolygons?.filter(p => p && p.isPortable) || [];
    const validPortableTriggers = portableTriggers.filter(p => p.center && p.radius);
    const pendingPortableTriggers = portableTriggers.filter(p => !p.center || !p.radius);
    
    console.log(`🟣 PERMANENT FIX: Processing ${portableTriggers.length} portable triggers: ${validPortableTriggers.length} valid, ${pendingPortableTriggers.length} pending`);

    // STEP 1: ONLY remove circles for triggers that no longer exist in ANY portable list
    Object.keys(portableTriggerCirclesRef.current).forEach(triggerId => {
      const stillExists = portableTriggers.find(p => p.id == triggerId);
      
      if (!stillExists) {
        // Trigger completely removed from system
        console.log(`🗑️ PERMANENT REMOVAL: Portable trigger ${triggerId} no longer exists`);
        const circle = portableTriggerCirclesRef.current[triggerId];
        const label = portableTriggerLabelsRef.current[triggerId];
        
        if (circle && mapInstanceRef.current.hasLayer(circle)) {
          mapInstanceRef.current.removeLayer(circle);
        }
        if (label && mapInstanceRef.current.hasLayer(label)) {
          mapInstanceRef.current.removeLayer(label);
        }
        
        delete portableTriggerCirclesRef.current[triggerId];
        delete portableTriggerLabelsRef.current[triggerId];
      }
    });

    // STEP 2: Handle pending triggers (temporarily hide, don't remove)
    pendingPortableTriggers.forEach(trigger => {
      const triggerId = trigger.id;
      const circle = portableTriggerCirclesRef.current[triggerId];
      const label = portableTriggerLabelsRef.current[triggerId];
      
      if (circle && mapInstanceRef.current.hasLayer(circle)) {
        console.log(`⏸️ TEMPORARILY HIDING: Pending portable trigger ${triggerId}`);
        mapInstanceRef.current.removeLayer(circle);
      }
      if (label && mapInstanceRef.current.hasLayer(label)) {
        mapInstanceRef.current.removeLayer(label);
      }
    });

    // STEP 3: Update or create circles for valid positioned triggers (SMART UPDATES)
    validPortableTriggers.forEach(trigger => {
      const triggerId = trigger.id;
      const center = trigger.center; // [lat, lng]
      const radius = trigger.radius;
      const isContained = trigger.isContained;
      const uniqueKey = trigger.uniqueKey || `${triggerId}-${center[0]}_${center[1]}`;

      console.log(`🟣 SMART UPDATE: Processing trigger ${triggerId} at [${center}] radius ${radius}`);

      // Get existing circle
      let circle = portableTriggerCirclesRef.current[triggerId];
      let label = portableTriggerLabelsRef.current[triggerId];

      if (!circle) {
        // CREATE NEW CIRCLE (first time only)
        console.log(`🆕 CREATING NEW: Portable trigger circle ${triggerId}`);
        circle = L.circle(center, {
          radius: radius,
          color: isContained ? "red" : "purple",
          fillOpacity: 0.3,
          weight: 2
        });
        
        // Store the unique key to prevent unnecessary recreation
        circle._triggerUniqueKey = uniqueKey;
        
        circle.addTo(mapInstanceRef.current);
        circle.bindPopup(`
          <div>
            <h4>Trigger ${triggerId}</h4>
            <p><strong>Name:</strong> ${trigger.name}</p>
            <p><strong>Type:</strong> Portable</p>
            <p><strong>Radius:</strong> ${radius} units</p>
            <p><strong>Status:</strong> ${isContained ? 'Contained' : 'Not Contained'}</p>
          </div>
        `);

        portableTriggerCirclesRef.current[triggerId] = circle;

        // Create label if enabled
        if (showTriggerLabels) {
          label = L.marker(center, {
            icon: L.divIcon({
              className: "trigger-label",
              html: `<span style="background-color: ${isContained ? "red" : "purple"}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px; font-weight: bold;">${triggerId}</span>`,
              iconSize: [30, 20],
              iconAnchor: [15, 10]
            })
          }).addTo(mapInstanceRef.current);
          
          portableTriggerLabelsRef.current[triggerId] = label;
        }
      } else {
        // SMART UPDATE: Only update if position actually changed
        const lastUniqueKey = circle._triggerUniqueKey;
        const positionChanged = lastUniqueKey !== uniqueKey;
        
        if (positionChanged) {
          console.log(`🔄 SMART POSITION UPDATE: Trigger ${triggerId} moved from ${lastUniqueKey} to ${uniqueKey}`);
          
          // Update position and properties
          circle.setLatLng(center);
          circle.setRadius(radius);
          circle.setStyle({
            color: isContained ? "red" : "purple"
          });
          
          // Update stored unique key
          circle._triggerUniqueKey = uniqueKey;
          
          // Update label position if it exists
          if (label) {
            label.setLatLng(center);
            label.setIcon(L.divIcon({
              className: "trigger-label",
              html: `<span style="background-color: ${isContained ? "red" : "purple"}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px; font-weight: bold;">${triggerId}</span>`,
              iconSize: [30, 20],
              iconAnchor: [15, 10]
            }));
          }
        } else {
          console.log(`⏸️ NO UPDATE NEEDED: Trigger ${triggerId} position unchanged (${uniqueKey})`);
        }
        
        // Ensure circle is visible (show if it was hidden)
        if (!mapInstanceRef.current.hasLayer(circle)) {
          console.log(`👁️ SHOWING: Portable trigger circle ${triggerId}`);
          mapInstanceRef.current.addLayer(circle);
        }

        // Handle label visibility
        if (showTriggerLabels) {
          if (!label) {
            // Create label if now enabled and doesn't exist
            label = L.marker(center, {
              icon: L.divIcon({
                className: "trigger-label",
                html: `<span style="background-color: ${isContained ? "red" : "purple"}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px; font-weight: bold;">${triggerId}</span>`,
                iconSize: [30, 20],
                iconAnchor: [15, 10]
              })
            }).addTo(mapInstanceRef.current);
            
            portableTriggerLabelsRef.current[triggerId] = label;
          } else if (!mapInstanceRef.current.hasLayer(label)) {
            // Show label if hidden
            mapInstanceRef.current.addLayer(label);
          }
        } else if (label) {
          // Remove label if now disabled
          if (mapInstanceRef.current.hasLayer(label)) {
            mapInstanceRef.current.removeLayer(label);
          }
          delete portableTriggerLabelsRef.current[triggerId];
        }
      }
    });

    console.log(`✅ PERMANENT FIX COMPLETE: Active circles: ${Object.keys(portableTriggerCirclesRef.current).length}, Visible circles: ${validPortableTriggers.length}`);
  }, [useLeaflet, mapInitialized, existingTriggerPolygons, showTriggerLabels]);

  /* ─────────── static trigger rendering (unchanged) ─────────── */
  useEffect(() => {
    console.log("🎨 Static trigger useEffect triggered, polygons:", existingTriggerPolygons?.length);
    
    if (!useLeaflet || !mapInstanceRef.current || !mapData || !mapInitialized) {
      console.log("Static trigger rendering skipped - map not ready");
      return;
    }
    
    if (!showExistingTriggers || !existingTriggerPolygons || existingTriggerPolygons.length === 0) {
      console.log("No triggers to render:", { showExistingTriggers, polygonCount: existingTriggerPolygons?.length });
      
      // Clear existing static trigger layers only
      mapInstanceRef.current.eachLayer((layer) => {
        if (layer.staticTriggerId || layer.staticTriggerLabelId) {
          mapInstanceRef.current.removeLayer(layer);
        }
      });
      return;
    }

    console.log("🎨 Rendering static triggers");

    // Clear existing static trigger layers only
    mapInstanceRef.current.eachLayer((layer) => {
      if (layer.staticTriggerId || layer.staticTriggerLabelId) {
        mapInstanceRef.current.removeLayer(layer);
      }
    });

    // Render static triggers only (portable triggers handled above)
    const staticTriggers = existingTriggerPolygons.filter(trigger => 
      trigger && !trigger.isPortable && trigger.latLngs && trigger.latLngs.length > 0
    );

    staticTriggers.forEach(trigger => {
      try {
        console.log(`🔷 Rendering static trigger ${trigger.id}:`, trigger.latLngs.length, "vertices");
        const polygon = L.polygon(trigger.latLngs, {
          color: "blue",
          fillColor: "blue", 
          fillOpacity: 0.2,
          weight: 2
        }).addTo(mapInstanceRef.current);
        
        polygon.staticTriggerId = trigger.id; // Mark for cleanup
        polygon.bindPopup(`
          <div>
            <h4>Trigger ${trigger.id}</h4>
            <p><strong>Name:</strong> ${trigger.name}</p>
            <p><strong>Type:</strong> Static Zone</p>
            <p><strong>Vertices:</strong> ${trigger.latLngs.length}</p>
          </div>
        `);

        // Add trigger ID label for static triggers if enabled
        if (showTriggerLabels) {
          // Calculate centroid from vertices
          const lats = trigger.latLngs.map(coord => coord[0]);
          const lngs = trigger.latLngs.map(coord => coord[1]);
          const centroidLat = (Math.min(...lats) + Math.max(...lats)) / 2;
          const centroidLng = (Math.min(...lngs) + Math.max(...lngs)) / 2;
          
          const labelMarker = L.marker([centroidLat, centroidLng], {
            icon: L.divIcon({
              className: "trigger-label",
              html: `<span style="background-color: blue; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px; font-weight: bold;">${trigger.id}</span>`,
              iconSize: [30, 20],
              iconAnchor: [15, 10]
            })
          }).addTo(mapInstanceRef.current);
          
          labelMarker.staticTriggerLabelId = trigger.id; // Mark for cleanup
          console.log(`🏷️ Added label for static trigger ${trigger.id}`);
        }
      } catch (error) {
        console.error(`❌ Error rendering static trigger ${trigger.id}:`, error);
      }
    });

    console.log("✅ Static trigger rendering complete");
  }, [useLeaflet, mapInitialized, showExistingTriggers, existingTriggerPolygons?.length, showTriggerLabels]);

  /* ─────────── helpers ─────────── */
  const resetMapView = () => {
    if (mapData && mapInstanceRef.current) {
      mapInstanceRef.current.fitBounds(mapData.bounds);
      console.log("🏠 Map view reset");
    }
  };

  const fitToData = () => {
    if (!mapInstanceRef.current) return;
    
    const bounds = [];
    Object.entries(tagMarkersRef.current).forEach(([id, m]) => {
      if (!hiddenTags.has(id) && mapInstanceRef.current?.hasLayer(m))
        bounds.push(m.getLatLng());
    });
    
    if (bounds.length) {
      mapInstanceRef.current.fitBounds(L.latLngBounds(bounds), {
        padding: [20, 20],
      });
      console.log("📏 Map fitted to data");
    } else {
      resetMapView();
    }
  };

  const toggleTagVisibility = (id) => {
    setHiddenTags((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
        // Show the marker if it exists
        const marker = tagMarkersRef.current[id];
        if (marker && mapInstanceRef.current && !mapInstanceRef.current.hasLayer(marker)) {
          mapInstanceRef.current.addLayer(marker);
        }
      } else {
        next.add(id);
        // Hide the marker
        const marker = tagMarkersRef.current[id];
        if (marker && mapInstanceRef.current && mapInstanceRef.current.hasLayer(marker)) {
          mapInstanceRef.current.removeLayer(marker);
        }
      }
      console.log(`👁️ Tag ${id} visibility toggled`);
      return next;
    });
  };

  const toggleAllTagVisibility = () => {
    const activeTags = Object.keys(tagsData);
    setHiddenTags((prev) => {
      if (prev.size === 0) {
        // Hide all tags
        activeTags.forEach(tagId => {
          const marker = tagMarkersRef.current[tagId];
          if (marker && mapInstanceRef.current && mapInstanceRef.current.hasLayer(marker)) {
            mapInstanceRef.current.removeLayer(marker);
          }
        });
        console.log("👁️ All tags hidden");
        return new Set(activeTags);
      } else {
        // Show all tags
        activeTags.forEach(tagId => {
          const marker = tagMarkersRef.current[tagId];
          if (marker && mapInstanceRef.current && !mapInstanceRef.current.hasLayer(marker)) {
            mapInstanceRef.current.addLayer(marker);
          }
        });
        console.log("👁️ All tags shown");
        return new Set();
      }
    });
  };

  const cycleMapMode = () =>
    setMapMode((m) => {
      const next = m === "view" ? "analyze" : m === "analyze" ? "debug" : "view";
      console.log(`🔄 Map mode: ${m} → ${next}`);
      return next;
    });

  /* ─────────── keyboard shortcuts ─────────── */
  useKeyboardShortcuts({
    isEnabled: enableKeyboardShortcuts && mapInitialized,
    onHomeView: resetMapView,
    onFitToData: fitToData,
    onToggleLegend: () => setShowLegend((p) => !p),
    onToggleControls: () => setShowControls((p) => !p),
    onToggleTagVisibility: toggleAllTagVisibility,
    onCycleMapMode: cycleMapMode,
  });

  /* ─────────── render ─────────── */
  const activeTags = Object.keys(tagsData);
  const mapStyle = {
    height,
    width: enableResponsive ? width : 800,
    border: "2px solid black",
    position: "relative",
  };

  // Enhanced map readiness check for controls
  const mapReady = mapInitialized && 
                  mapInstanceRef.current && 
                  mapInstanceRef.current._loaded && 
                  mapInstanceRef.current._controlCorners &&
                  mapInstanceRef.current._controlCorners.topleft;

  // Debug logging
  console.log("NTV_index DEBUG v0.2.9:", {
    mapId: mapId,
    triggers: triggers?.length || 0,
    existingTriggerPolygons: existingTriggerPolygons?.length || 0,
    portableCircles: Object.keys(portableTriggerCirclesRef.current).length,
    showExistingTriggers,
    showTriggerLabels,
    selectedZone: zones[0]?.i_zn,
    mapInitialized,
    mapReady
  });

  return (
    <div style={{ position: "relative" }}>
      {error && <div style={{ color: "red" }}>{error.toString()}</div>}

      <div style={{ marginBottom: "10px", fontSize: "12px", color: "#666" }}>
        Map Status: {mapInitialized ? "✅ Initialized" : "⏳ Loading"} | 
        Controls: {mapReady ? "✅ Ready" : "⏳ Waiting"} | 
        Tags: {activeTags.length} |
        Triggers: {existingTriggerPolygons?.length || 0} |
        Portable Circles: {Object.keys(portableTriggerCirclesRef.current).length} |
        Labels: {showTriggerLabels ? "ON" : "OFF"}
      </div>

      {useLeaflet ? (
        <div style={mapStyle}>
          <div ref={mapRef} style={{ height: "100%", width: "100%" }} />

          {/* Only render controls when map is fully ready */}
          {showControls && mapReady && (
            <MapControls
              mapInstance={mapInstanceRef.current}
              onHomeClick={resetMapView}
              onFitDataClick={fitToData}
              onHelpClick={() => cycleMapMode()}
            />
          )}

          {showLegend && <Legend isConnected={isConnected} mapMode={mapMode} />}

          {showControls && activeTags.length > 0 && (
            <TagControls
              activeTags={activeTags}
              hiddenTags={hiddenTags}
              onToggleTag={toggleTagVisibility}
              onToggleAll={toggleAllTagVisibility}
              showHotkeyHint={enableKeyboardShortcuts}
            />
          )}
        </div>
      ) : (
        <div
          style={{
            height,
            width,
            border: "2px solid black",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          Canvas mode TBD
        </div>
      )}
    </div>
  );
};

export default NTV_index;