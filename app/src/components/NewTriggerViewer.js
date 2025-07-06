/* Name: NewTriggerViewer.js */
/* Version: 0.1.7 */
/* Created: 971201 */
/* Modified: 250706 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: JavaScript file for ParcoRTLS frontend - Enhanced with responsive UI and map controls */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// Version: v0.1.7-250706 - Enhanced UI with responsive sizing, map controls, and tag visibility toggles
// Previous: Extended marker timeout (5s→10s stale, 30s→5min removal) to reduce flicker, bumped from v0.1.5

import React, { useEffect, useRef, useState, memo, useMemo } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import "leaflet-draw";
import "./Map.css";
import { useKeyboardShortcuts } from "./NewTriggerDemo/hooks/useKeyboardShortcuts";

const NewTriggerViewer = memo(({
  mapId,
  zones,
  checkedZones,
  vertices,
  onVerticesUpdate,
  useLeaflet,
  enableDrawing,
  onDrawComplete,
  showExistingTriggers,
  existingTriggerPolygons,
  tagsData,
  propIsConnected,
  triggers = [], // Default to empty array
  enableResponsive = true, // NEW: Enable responsive sizing
  enableControls = true, // NEW: Enable enhanced controls
  height = "600px", // NEW: Configurable height
  width = "100%", // NEW: Configurable width (responsive by default)
  enableKeyboardShortcuts = true // NEW: Enable keyboard shortcuts
}) => {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const canvasRef = useRef(null);
  const [mapData, setMapData] = useState(null);
  const [zoneVertices, setZoneVertices] = useState([]);
  const [error, setError] = useState(null);
  const [mapInitialized, setMapInitialized] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const isInitialized = useRef(false);
  const ctxRef = useRef(null);
  const imageRef = useRef(null);
  const drawnItems = useRef(new L.FeatureGroup());
  const canvasBounds = useRef({ x: 0, y: 0, width: 800, height: 600 });
  const tagMarkersRef = useRef({});
  const zoneLabelRef = useRef(null);
  const userInteracted = useRef(false);
  const updateTimeout = useRef(null);
  const firstTagAppearance = useRef(true);
  const wsRef = useRef(null);
  
  // NEW: Enhanced UI state
  const [hiddenTags, setHiddenTags] = useState(new Set());
  const [showControls, setShowControls] = useState(enableControls);
  const [showLegend, setShowLegend] = useState(true);
  const [mapMode, setMapMode] = useState('view'); // 'view', 'analyze', 'debug'
  const homeControlRef = useRef(null);
  const fitDataControlRef = useRef(null);
  const scaleControlRef = useRef(null);
  
  // Zoom-aware update control
  const isZoomingRef = useRef(false);
  const pendingUpdateRef = useRef(false);

  // Enhanced tag marker management refs with EXTENDED timeouts
  const tagLastSeenRef = useRef({}); // Track when each tag was last seen
  const tagTimeoutRef = useRef({}); // Track timeout handlers for each tag
  const tagLastPositionRef = useRef({}); // Track last known positions

  // Dynamic server host configuration
  const server_host = window.location.hostname || 'localhost';

  // NEW: Home/Reset View function
  const resetMapView = () => {
    if (!mapInstance.current || !mapData) return;
    mapInstance.current.fitBounds(mapData.bounds);
    userInteracted.current = false; // Reset user interaction flag
    console.log("🏠 Map view reset to default bounds");
  };

  // NEW: Fit to Data function
  const fitToData = () => {
    if (!mapInstance.current) return;
    
    const bounds = [];
    
    // Add tag marker positions to bounds
    Object.entries(tagMarkersRef.current).forEach(([tagId, marker]) => {
      if (!hiddenTags.has(tagId) && mapInstance.current.hasLayer(marker)) {
        bounds.push(marker.getLatLng());
      }
    });
    
    // Add trigger polygons to bounds
    if (showExistingTriggers && existingTriggerPolygons) {
      existingTriggerPolygons.forEach(trigger => {
        if (trigger.isPortable && trigger.center) {
          bounds.push(trigger.center);
        } else if (trigger.latLngs) {
          bounds.push(...trigger.latLngs);
        }
      });
    }
    
    if (bounds.length > 0) {
      const latLngBounds = L.latLngBounds(bounds);
      mapInstance.current.fitBounds(latLngBounds, { padding: [20, 20] });
      console.log("📏 Map fitted to data bounds:", bounds.length, "points");
    } else {
      resetMapView(); // Fallback to default view
    }
  };

  // NEW: Toggle tag visibility
  const toggleTagVisibility = (tagId) => {
    const newHiddenTags = new Set(hiddenTags);
    if (hiddenTags.has(tagId)) {
      newHiddenTags.delete(tagId);
      // Show the marker if it exists
      const marker = tagMarkersRef.current[tagId];
      if (marker && mapInstance.current && !mapInstance.current.hasLayer(marker)) {
        mapInstance.current.addLayer(marker);
      }
    } else {
      newHiddenTags.add(tagId);
      // Hide the marker
      const marker = tagMarkersRef.current[tagId];
      if (marker && mapInstance.current && mapInstance.current.hasLayer(marker)) {
        mapInstance.current.removeLayer(marker);
      }
    }
    setHiddenTags(newHiddenTags);
    console.log(`👁️ Tag ${tagId} visibility toggled:`, !hiddenTags.has(tagId) ? 'hidden' : 'visible');
  };

  // NEW: Toggle all tag visibility
  const toggleAllTagVisibility = () => {
    const activeTags = Object.keys(tagsData);
    if (hiddenTags.size === 0) {
      // Hide all tags
      setHiddenTags(new Set(activeTags));
      activeTags.forEach(tagId => {
        const marker = tagMarkersRef.current[tagId];
        if (marker && mapInstance.current && mapInstance.current.hasLayer(marker)) {
          mapInstance.current.removeLayer(marker);
        }
      });
    } else {
      // Show all tags
      setHiddenTags(new Set());
      activeTags.forEach(tagId => {
        const marker = tagMarkersRef.current[tagId];
        if (marker && mapInstance.current && !mapInstance.current.hasLayer(marker)) {
          mapInstance.current.addLayer(marker);
        }
      });
    }
  };

  // NEW: Cycle map mode
  const cycleMapMode = () => {
    const modes = ['view', 'analyze', 'debug'];
    const currentIndex = modes.indexOf(mapMode);
    const nextIndex = (currentIndex + 1) % modes.length;
    setMapMode(modes[nextIndex]);
    console.log(`🔄 Map mode changed to: ${modes[nextIndex]}`);
  };

  // Get list of active tags for the visibility controls
  const activeTags = Object.keys(tagsData);

  // NEW: Keyboard shortcuts integration (after all functions are defined)
  const { shortcutsInfo, showShortcutsHelp } = useKeyboardShortcuts({
    isEnabled: enableKeyboardShortcuts && useLeaflet && mapInitialized,
    onHomeView: resetMapView,
    onFitToData: fitToData,
    onToggleLegend: () => setShowLegend(prev => !prev),
    onToggleControls: () => setShowControls(prev => !prev),
    onToggleTriggers: null, // Could be passed from parent
    onToggleTagVisibility: toggleAllTagVisibility,
    onCycleMapMode: cycleMapMode,
    onClearEvents: null, // Could be passed from parent
    mapInstance: mapInstance.current
  });

  // WebSocket connection for heartbeats
  useEffect(() => {
    const ws = new WebSocket(`ws://${server_host}:8002/ws/realtime?client_id=trigger_viewer_${Date.now()}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log(`✅ WebSocket connected to ws://${server_host}:8002/ws/realtime`);
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("📩 WebSocket message received:", data);
        if (data.type === "HeartBeat" && data.data?.heartbeat_id) {
          const response = {
            type: "HeartBeat",
            ts: data.ts,
            data: { heartbeat_id: data.data.heartbeat_id }
          };
          ws.send(JSON.stringify(response));
          console.log("📤 Sent heartbeat response:", response);
        }
      } catch (error) {
        console.error("❌ Error parsing WebSocket message:", error);
      }
    };

    ws.onclose = () => {
      console.log("❌ WebSocket disconnected");
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error("❌ WebSocket error:", error);
      setIsConnected(false);
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        console.log("🧹 WebSocket cleaned up");
      }
    };
  }, [server_host]);

  useEffect(() => {
    if (mapId) {
      const fetchMapData = async () => {
        try {
          const response = await fetch(`http://${server_host}:8000/zoneviewer/get_map_data/${mapId}`);
          if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
          const data = await response.json();
          
          // Fix imageUrl to use correct server host if it contains localhost/127.0.0.1
          if (data.imageUrl && (data.imageUrl.includes('127.0.0.1') || data.imageUrl.includes('localhost'))) {
            data.imageUrl = data.imageUrl.replace(/https?:\/\/(127\.0\.0\.1|localhost)(:\d+)?/, `http://${server_host}:8000`);
            console.log("✅ Fixed imageUrl to use correct server host:", data.imageUrl);
          }
          
          console.log("✅ Fetched map data:", data);
          setMapData(data);
          setError(null);
        } catch (error) {
          console.error("❌ Error fetching map data:", error);
          setError(`Error fetching map data: ${error.message}`);
        }
      };
      fetchMapData();
    }
  }, [mapId, server_host]);

  useEffect(() => {
    if (checkedZones.length === 0) {
      setZoneVertices([]);
      if (onVerticesUpdate) onVerticesUpdate([]);
      return;
    }

    const fetchZoneVertices = async () => {
      try {
        const verticesPromises = checkedZones.map(async (zoneId) => {
          const response = await fetch(`http://${server_host}:8000/zoneviewer/get_vertices_for_campus/${zoneId}`);
          if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
          const data = await response.json();
          return data.vertices.map(vertex => ({
            i_vtx: vertex.vertex_id,
            zone_id: vertex.zone_id,
            n_x: Number(vertex.x).toFixed(6),
            n_y: Number(vertex.y).toFixed(6),
            n_z: Number(vertex.z).toFixed(6),
            n_ord: vertex.order
          }));
        });

        const allVertices = (await Promise.all(verticesPromises)).flat();
        console.log("✅ Fetched vertices for checked zones:", allVertices);
        setZoneVertices(allVertices);
        if (onVerticesUpdate) onVerticesUpdate(allVertices);
      } catch (error) {
        console.error("❌ Error fetching vertices:", error);
        setError(`Error fetching vertices: ${error.message}`);
      }
    };

    fetchZoneVertices();
  }, [checkedZones, onVerticesUpdate, server_host]);

  useEffect(() => {
    if (!useLeaflet && mapData && canvasRef.current && !isInitialized.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");
      ctxRef.current = ctx;
      canvas.width = 800;
      canvas.height = 600;

      const img = new Image();
      img.crossOrigin = "anonymous";
      img.src = mapData.imageUrl;
      imageRef.current = img;

      img.onload = () => {
        const boundsWidth = mapData.bounds[1][1] - mapData.bounds[0][1];
        const boundsHeight = mapData.bounds[1][0] - mapData.bounds[0][0];
        const mapAspect = boundsWidth / boundsHeight;
        const canvasAspect = canvas.width / canvas.height;
        let drawWidth = canvas.width;
        let drawHeight = canvas.height;
        let offsetX = 0;
        let offsetY = 0;

        if (mapAspect > canvasAspect) {
          drawHeight = canvas.width / mapAspect;
          offsetY = (canvas.height - drawHeight) / 2;
        } else {
          drawWidth = canvas.height * mapAspect;
          offsetX = (canvas.width - drawWidth) / 2;
        }

        canvasBounds.current = { x: offsetX, y: offsetY, width: drawWidth, height: drawHeight };
        ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
        drawZones(ctx, offsetX, offsetY, drawWidth, drawHeight, boundsWidth, boundsHeight);
        drawTriggers(ctx, offsetX, offsetY, drawWidth, drawHeight, boundsWidth, boundsHeight);
      };

      img.onerror = () => setError("Failed to load map image.");
      isInitialized.current = true;
    }

    return () => {
      if (!useLeaflet && canvasRef.current) {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        isInitialized.current = false;
      }
    };
  }, [mapData, useLeaflet, zoneVertices, showExistingTriggers, existingTriggerPolygons]);

  const drawZones = (ctx, offsetX, offsetY, drawWidth, drawHeight, boundsWidth, boundsHeight) => {
    const seniorZone = checkedZones.length > 1 ? Math.min(...checkedZones) : checkedZones[0];
    checkedZones.forEach(zoneId => {
      const filteredVertices = zoneVertices.filter(v => v.zone_id === zoneId);
      if (filteredVertices.length > 0) {
        ctx.beginPath();
        filteredVertices.forEach((v, i) => {
          const x = offsetX + (v.n_x - mapData.bounds[0][1]) * (drawWidth / boundsWidth);
          const y = offsetY + (mapData.bounds[1][0] - v.n_y) * (drawHeight / boundsHeight);
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
          ctx.fillStyle = "red";
          ctx.fillRect(x - 2, y - 2, 4, 4);
          if (zoneId === seniorZone) {
            ctx.font = "12px Arial";
            ctx.fillStyle = "black";
            ctx.fillText(v.i_vtx, x + 5, y - 5);
          }
        });
        ctx.closePath();
        ctx.strokeStyle = "red";
        ctx.stroke();
      } else {
        console.log(`ℹ️ No vertices to render for zone ${zoneId}`);
      }
    });
  };

  const drawTriggers = (ctx, offsetX, offsetY, drawWidth, drawHeight, boundsWidth, boundsHeight) => {
    if (!showExistingTriggers || !existingTriggerPolygons || existingTriggerPolygons.length === 0) {
      console.log("No triggers to render in canvas mode", { showExistingTriggers, existingTriggerPolygons });
      return;
    }

    const zoneBoundingBox = { xMin: Infinity, xMax: -Infinity, yMin: Infinity, yMax: -Infinity };
    checkedZones.forEach(zoneId => {
      const filteredVertices = zoneVertices.filter(v => v.zone_id === zoneId);
      filteredVertices.forEach(v => {
        const x = Number(v.n_x);
        const y = Number(v.n_y);
        zoneBoundingBox.xMin = Math.min(zoneBoundingBox.xMin, x);
        zoneBoundingBox.xMax = Math.max(zoneBoundingBox.xMax, x);
        zoneBoundingBox.yMin = Math.min(zoneBoundingBox.yMin, y);
        zoneBoundingBox.yMax = Math.max(zoneBoundingBox.yMax, y);
      });
    });

    existingTriggerPolygons.forEach(trigger => {
      if (!trigger) return;

      if (trigger.isPortable && trigger.center && trigger.radius) {
        // Render portable triggers as circles
        const [centerY, centerX] = trigger.center;
        const x = offsetX + (centerX - mapData.bounds[0][1]) * (drawWidth / boundsWidth);
        const y = offsetY + (mapData.bounds[1][0] - centerY) * (drawHeight / boundsHeight);
        const scaledRadius = trigger.radius * (drawWidth / boundsWidth);

        ctx.beginPath();
        ctx.arc(x, y, scaledRadius, 0, 2 * Math.PI);
        ctx.strokeStyle = trigger.isContained ? "red" : "purple";
        ctx.fillStyle = trigger.isContained ? "rgba(255, 0, 0, 0.5)" : "rgba(128, 0, 128, 0.5)";
        ctx.fill();
        ctx.stroke();

        ctx.font = "12px Arial";
        ctx.fillStyle = "black";
        ctx.fillText(trigger.id, x + 5, y - 5);
        console.log(`Rendered portable trigger ${trigger.id} on canvas at center [${x}, ${y}] with radius ${scaledRadius}`);
      } else if (trigger.latLngs) {
        // Render non-portable triggers as polygons
        const isWithinBoundingBox = trigger.latLngs.some(([lat, lng]) => {
          return (
            lng >= zoneBoundingBox.xMin &&
            lng <= zoneBoundingBox.xMax &&
            lat >= zoneBoundingBox.yMin &&
            lat <= zoneBoundingBox.yMax
          );
        });

        if (isWithinBoundingBox) {
          ctx.beginPath();
          trigger.latLngs.forEach(([lat, lng], i) => {
            const x = offsetX + (lng - mapData.bounds[0][1]) * (drawWidth / boundsWidth);
            const y = offsetY + (mapData.bounds[1][0] - lat) * (drawHeight / boundsHeight);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          });
          ctx.closePath();
          ctx.strokeStyle = "blue";
          ctx.stroke();

          const centroid = trigger.latLngs.reduce((acc, [lat, lng]) => [acc[0] + lat, acc[1] + lng], [0, 0]);
          centroid[0] /= trigger.latLngs.length;
          centroid[1] /= trigger.latLngs.length;
          const centroidX = offsetX + (centroid[1] - mapData.bounds[0][1]) * (drawWidth / boundsWidth);
          const centroidY = offsetY + (mapData.bounds[1][0] - centroid[0]) * (drawHeight / boundsHeight);
          ctx.font = "12px Arial";
          ctx.fillStyle = "black";
          ctx.fillText(trigger.id, centroidX + 5, centroidY - 5);
          console.log(`Rendered non-portable trigger ${trigger.id} on canvas at centroid [${centroidX}, ${centroidY}]`);
        } else {
          console.log(`Non-portable trigger ${trigger.id} not within bounding box`, zoneBoundingBox);
        }
      } else {
        console.log(`Trigger ${trigger.id} skipped: missing latLngs or center/radius`, trigger);
      }
    });
  };

  // Function to execute pending marker updates after zoom ends
  const executeMarkerUpdate = () => {
    if (!useLeaflet || !mapInstance.current || !mapData || !mapInitialized) return;

    const selectedZoneId = zones[0]?.i_zn || "N/A";
    const now = Date.now();

    // Process existing tags that have new data
    Object.entries(tagsData).forEach(([tagId, tagData]) => {
      const tagZoneId = tagData.zone_id || selectedZoneId;
      console.log(`Tag ${tagId} processing:`, {
        tagZoneId,
        selectedZoneId,
        zoneMatch: tagZoneId === selectedZoneId,
        tagData
      });
      
      if (tagZoneId !== selectedZoneId) {
        console.log(`Tag ${tagId} filtered out due to zone mismatch: ${tagZoneId} !== ${selectedZoneId}`);
        return;
      }

      // Skip if tag is hidden
      if (hiddenTags.has(tagId)) {
        console.log(`Tag ${tagId} skipped - hidden by user`);
        return;
      }

      // Update last seen time for active tags
      tagLastSeenRef.current[tagId] = now;
      
      // Clear any existing timeout for this tag
      if (tagTimeoutRef.current[tagId]) {
        clearTimeout(tagTimeoutRef.current[tagId]);
        delete tagTimeoutRef.current[tagId];
      }

      const { x, y } = tagData;
      const latLng = [y, x];
      const positionKey = `${x},${y}`; // Create position identifier

      // Check if position actually changed
      const lastPosition = tagLastPositionRef.current[tagId];
      const positionChanged = lastPosition !== positionKey;

      // Update last position
      tagLastPositionRef.current[tagId] = positionKey;

      const bounds = L.latLngBounds(mapData.bounds);
      if (!bounds.contains(latLng)) {
        console.warn(`Tag ${tagId} position ${latLng} is outside map bounds:`, mapData.bounds);
        return;
      }

      const associatedTrigger = triggers?.find(t => t.is_portable && t.assigned_tag_id === tagId);
      let markerSize = 10;
      if (associatedTrigger && associatedTrigger.radius_ft) {
        markerSize = Math.round(10 * (associatedTrigger.radius_ft / 3));
        console.log(`Scaling marker for tag ${tagId}: radius_ft=${associatedTrigger.radius_ft}, markerSize=${markerSize}px`);
      }

      let marker = tagMarkersRef.current[tagId];
      if (!marker) {
        // Create new marker - red/active (keeping original color scheme)
        marker = L.marker(latLng, {
          icon: L.divIcon({
            className: "tag-marker",
            html: `<div style="background-color: red; width: ${markerSize}px; height: ${markerSize}px; border-radius: 50%;"></div>`,
            iconSize: [markerSize, markerSize],
            iconAnchor: [markerSize / 2, markerSize / 2]
          }),
          zIndexOffset: 1000
        }).addTo(mapInstance.current);
        
        // Enhanced tooltip with more information
        const tooltip = `Tag ${tagId}<br/>Zone: ${tagZoneId}<br/>Pos: (${x.toFixed(2)}, ${y.toFixed(2)})`;
        marker.bindTooltip(tooltip, { permanent: false, direction: "top" });
        tagMarkersRef.current[tagId] = marker;
        tagLastPositionRef.current[tagId] = positionKey; // Store initial position
        console.log(`Tag marker created for ${tagId} at:`, latLng);
        
        // Only auto-zoom on very first tag appearance if user hasn't interacted and only 1 tag exists
        if (firstTagAppearance.current && !userInteracted.current && Object.keys(tagMarkersRef.current).length === 1) {
          mapInstance.current.setView(latLng, 7, { animate: false });
          console.log(`Initial map view set to tag ${tagId} at:`, latLng);
          firstTagAppearance.current = false;
        }
      } else {
        // Only update if position actually changed
        if (positionChanged) {
          marker.setLatLng(latLng);
          console.log(`Tag marker position updated for ${tagId} to:`, latLng);
        }
        
        // Update tooltip with current info
        const tooltip = `Tag ${tagId}<br/>Zone: ${tagZoneId}<br/>Pos: (${x.toFixed(2)}, ${y.toFixed(2)})`;
        marker.setTooltipContent(tooltip);
        
        // Only update icon if size changed (not every update)
        const currentSize = marker.options.icon.options.iconSize[0];
        if (currentSize !== markerSize) {
          marker.setIcon(L.divIcon({
            className: "tag-marker",
            html: `<div style="background-color: red; width: ${markerSize}px; height: ${markerSize}px; border-radius: 50%;"></div>`,
            iconSize: [markerSize, markerSize],
            iconAnchor: [markerSize / 2, markerSize / 2]
          }));
          console.log(`Tag marker size updated for ${tagId} to: ${markerSize}px`);
        }
      }
    });

    // Check for stale tags that haven't sent data recently - EXTENDED TIMEOUTS
    Object.keys(tagMarkersRef.current).forEach(tagId => {
      const lastSeen = tagLastSeenRef.current[tagId];
      const timeSinceLastSeen = now - (lastSeen || 0);
      
      if (!tagsData[tagId]) {
        // Tag not in current data - check how long it's been missing
        if (timeSinceLastSeen > 300000) { // 5 minutes (EXTENDED from 30 seconds)
          // Remove marker completely after 5 minutes
          const marker = tagMarkersRef.current[tagId];
          if (marker && mapInstance.current.hasLayer(marker)) {
            mapInstance.current.removeLayer(marker);
            console.log(`Tag marker for ${tagId} removed after 5 minutes of no data`);
          }
          delete tagMarkersRef.current[tagId];
          delete tagLastSeenRef.current[tagId];
          delete tagLastPositionRef.current[tagId];
          if (tagTimeoutRef.current[tagId]) {
            clearTimeout(tagTimeoutRef.current[tagId]);
            delete tagTimeoutRef.current[tagId];
          }
        } else if (timeSinceLastSeen > 10000) { // 10 seconds (EXTENDED from 5 seconds)
          // Turn marker gray if data stopped coming for 10+ seconds
          const marker = tagMarkersRef.current[tagId];
          if (marker) {
            const markerSize = 10; // Default size for gray markers
            marker.setIcon(L.divIcon({
              className: "tag-marker-stale",
              html: `<div style="background-color: gray; width: ${markerSize}px; height: ${markerSize}px; border-radius: 50%; opacity: 0.7;"></div>`,
              iconSize: [markerSize, markerSize],
              iconAnchor: [markerSize / 2, markerSize / 2]
            }));
            console.log(`Tag marker for ${tagId} turned gray (no data for ${(timeSinceLastSeen/1000).toFixed(1)}s)`);
            
            // Set timeout to remove after 5 minutes total
            if (!tagTimeoutRef.current[tagId]) {
              tagTimeoutRef.current[tagId] = setTimeout(() => {
                const marker = tagMarkersRef.current[tagId];
                if (marker && mapInstance.current.hasLayer(marker)) {
                  mapInstance.current.removeLayer(marker);
                  console.log(`Tag marker for ${tagId} removed after timeout`);
                }
                delete tagMarkersRef.current[tagId];
                delete tagLastSeenRef.current[tagId];
                delete tagLastPositionRef.current[tagId];
                delete tagTimeoutRef.current[tagId];
              }, 300000 - timeSinceLastSeen); // 5 minutes total
            }
          }
        }
      }
    });

    // Handle disconnection state
    if (!isConnected) {
      Object.values(tagMarkersRef.current).forEach(marker => {
        const markerSize = 10;
        marker.setIcon(L.divIcon({
          className: "tag-marker-disconnected",
          html: `<div style="background-color: red; width: ${markerSize}px; height: ${markerSize}px; border-radius: 50%; opacity: 0.5;"></div>`,
          iconSize: [markerSize, markerSize],
          iconAnchor: [markerSize / 2, markerSize / 2]
        }));
      });
      console.log("All tag markers turned red due to disconnection");
    }
  };

  useEffect(() => {
    if (useLeaflet && mapData && mapRef.current && !mapInstance.current) {
      mapInstance.current = L.map(mapRef.current, { 
        crs: L.CRS.Simple,
        zoomControl: true,
        minZoom: -5,
        maxZoom: 7,
        // Disable problematic animations
        zoomAnimation: false,
        fadeAnimation: false,
        markerZoomAnimation: false
      }).fitBounds(mapData.bounds);
      
      L.imageOverlay(mapData.imageUrl, mapData.bounds).addTo(mapInstance.current);
      mapInstance.current.addLayer(drawnItems.current);
      console.log("Map bounds:", mapData.bounds);

      // NEW: Add enhanced controls if enabled
      if (enableControls) {
        // Home/Reset View Control
        const HomeControl = L.Control.extend({
          onAdd: function(map) {
            const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
            container.style.backgroundColor = 'white';
            container.style.width = '30px';
            container.style.height = '30px';
            container.style.cursor = 'pointer';
            container.title = 'Reset to default view';
            container.innerHTML = '🏠';
            container.style.fontSize = '16px';
            container.style.textAlign = 'center';
            container.style.lineHeight = '30px';
            
            container.onclick = function() {
              resetMapView();
            };
            
            return container;
          },
          onRemove: function(map) {}
        });
        
        homeControlRef.current = new HomeControl({ position: 'topleft' });
        homeControlRef.current.addTo(mapInstance.current);

        // Fit to Data Control
        const FitDataControl = L.Control.extend({
          onAdd: function(map) {
            const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
            container.style.backgroundColor = 'white';
            container.style.width = '30px';
            container.style.height = '30px';
            container.style.cursor = 'pointer';
            container.title = 'Fit map to show all data';
            container.innerHTML = '📏';
            container.style.fontSize = '16px';
            container.style.textAlign = 'center';
            container.style.lineHeight = '30px';
            
            container.onclick = function() {
              fitToData();
            };
            
            return container;
          },
          onRemove: function(map) {}
        });
        
        fitDataControlRef.current = new FitDataControl({ position: 'topleft' });
        fitDataControlRef.current.addTo(mapInstance.current);

        // Help Control (NEW)
        const HelpControl = L.Control.extend({
          onAdd: function(map) {
            const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
            container.style.backgroundColor = 'white';
            container.style.width = '30px';
            container.style.height = '30px';
            container.style.cursor = 'pointer';
            container.title = 'Show keyboard shortcuts (?)';
            container.innerHTML = '?';
            container.style.fontSize = '16px';
            container.style.textAlign = 'center';
            container.style.lineHeight = '30px';
            container.style.fontWeight = 'bold';
            
            container.onclick = function() {
              showShortcutsHelp();
            };
            
            return container;
          },
          onRemove: function(map) {}
        });
        
        const helpControl = new HelpControl({ position: 'topleft' });
        helpControl.addTo(mapInstance.current);

        // Scale control
        scaleControlRef.current = L.control.scale({ position: 'bottomleft' });
        scaleControlRef.current.addTo(mapInstance.current);
      }

      // Set up zoom event handlers for coordinated updates
      mapInstance.current.on('zoomstart', () => {
        isZoomingRef.current = true;
        console.log("🔄 Zoom started - pausing marker updates");
      });

      mapInstance.current.on('zoomend', () => {
        isZoomingRef.current = false;
        console.log("✅ Zoom ended - resuming marker updates");
        
        // Execute any pending marker update immediately after zoom
        if (pendingUpdateRef.current) {
          pendingUpdateRef.current = false;
          executeMarkerUpdate();
          console.log("🔄 Executed pending marker update after zoom");
        }
      });

      mapInstance.current.on('zoomend moveend', () => {
        userInteracted.current = true;
        console.log("User interacted with map, zoom/center locked");
      });

      if (enableDrawing && mapInstance.current) {
        const drawControl = new L.Control.Draw({
          draw: {
            polygon: true,
            polyline: false,
            rectangle: false,
            circle: false,
            marker: false,
            circlemarker: false
          },
          edit: {
            featureGroup: drawnItems.current,
            remove: true
          }
        });
        mapInstance.current.addControl(drawControl);

        mapInstance.current.on(L.Draw.Event.CREATED, (e) => {
          const layer = e.layer;
          drawnItems.current.addLayer(layer);
          const coords = layer.getLatLngs()[0];
          if (onDrawComplete) onDrawComplete(coords);
        });
      }

      setMapInitialized(true);
      console.log("Leaflet map initialized with enhanced controls and responsive sizing");
    }

    return () => {
      if (mapInstance.current) {
        try {
          // Clean up custom controls
          if (homeControlRef.current) {
            mapInstance.current.removeControl(homeControlRef.current);
            homeControlRef.current = null;
          }
          if (fitDataControlRef.current) {
            mapInstance.current.removeControl(fitDataControlRef.current);
            fitDataControlRef.current = null;
          }
          if (scaleControlRef.current) {
            mapInstance.current.removeControl(scaleControlRef.current);
            scaleControlRef.current = null;
          }
          
          mapInstance.current.off();
          mapInstance.current.off(L.Draw.Event.CREATED);
          mapInstance.current.remove();
          console.log("Leaflet map cleaned up");
        } catch (error) {
          console.error("Error cleaning up Leaflet map:", error);
        }
        mapInstance.current = null;
        tagMarkersRef.current = {};
        zoneLabelRef.current = null;
        isInitialized.current = false;
        if (updateTimeout.current) {
          clearTimeout(updateTimeout.current);
          updateTimeout.current = null;
        }
        setMapInitialized(false);
      }
    };
  }, [mapData?.imageUrl, mapData?.bounds, useLeaflet, enableDrawing, onDrawComplete, enableControls]);

  // Update zone label when zones change
  useEffect(() => {
    if (!useLeaflet || !mapInstance.current || !mapData || !mapInitialized) return;

    // Remove existing zone label if it exists
    if (zoneLabelRef.current) {
      mapInstance.current.removeLayer(zoneLabelRef.current);
      zoneLabelRef.current = null;
      console.log("Removed existing zone label");
    }

    // Add new zone label
    const zoneId = zones[0]?.i_zn || "N/A";
    zoneLabelRef.current = L.marker([mapData.bounds[0][0] + 10, mapData.bounds[0][1] + 10], {
      icon: L.divIcon({
        className: "zone-label",
        html: `<span style="background-color: white; padding: 2px 5px; border: 1px solid black;">Zone ${zoneId}</span>`,
        iconSize: [50, 20]
      })
    }).addTo(mapInstance.current);
    console.log("Zone label updated to:", `Zone ${zoneId}`);
  }, [useLeaflet, mapData, zones, mapInitialized]);

  const memoizedTriggerPolygons = useMemo(() => {
    if (!showExistingTriggers || !existingTriggerPolygons || existingTriggerPolygons.length === 0) {
      return [];
    }
    return existingTriggerPolygons.map(trigger => ({
      ...trigger,
      key: `${trigger.id}-${trigger.isPortable ? (trigger.center?.join(",") || "pending") : trigger.latLngs?.map(coord => coord.join(",")).join("|")}-${trigger.isContained || false}`,
    }));
  }, [showExistingTriggers, existingTriggerPolygons]);

  useEffect(() => {
    if (!useLeaflet || !mapInstance.current || !mapData) return;

    drawnItems.current.clearLayers();

    const seniorZone = checkedZones.length > 1 ? Math.min(...checkedZones) : checkedZones[0];
    const zoneBoundingBox = { xMin: Infinity, xMax: -Infinity, yMin: Infinity, yMax: -Infinity };
    checkedZones.forEach(zoneId => {
      const filteredVertices = zoneVertices.filter(v => v.zone_id === zoneId);
      filteredVertices.forEach(v => {
        const x = Number(v.n_x);
        const y = Number(v.n_y);
        zoneBoundingBox.xMin = Math.min(zoneBoundingBox.xMin, x);
        zoneBoundingBox.xMax = Math.max(zoneBoundingBox.xMax, x);
        zoneBoundingBox.yMin = Math.min(zoneBoundingBox.yMin, y);
        zoneBoundingBox.yMax = Math.max(zoneBoundingBox.yMax, y);
      });

      if (filteredVertices.length > 0) {
        const latLngs = filteredVertices.map(v => [Number(v.n_y), Number(v.n_x)]);
        L.polygon(latLngs, { color: "red", fill: false }).addTo(drawnItems.current);
        if (zoneId === seniorZone) {
          filteredVertices.forEach(v => {
            L.marker([Number(v.n_y), Number(v.n_x)], {
              icon: L.divIcon({
                className: "vertex-label",
                html: `<span>${v.i_vtx}</span>`,
                iconSize: [20, 20],
              })
            }).addTo(drawnItems.current);
          });
        }
      }
    });

    if (memoizedTriggerPolygons.length > 0) {
      console.log("Trigger rendering useEffect running with memoizedTriggerPolygons:", memoizedTriggerPolygons);
      memoizedTriggerPolygons.forEach(trigger => {
        if (trigger) {
          if (trigger.isPortable && trigger.center && trigger.radius) {
            console.log(`Rendering portable trigger ${trigger.id} at center ${trigger.center} with radius ${trigger.radius}`);
            const circle = L.circle(trigger.center, {
              radius: trigger.radius,
              color: trigger.isContained ? "red" : "purple",
              fillOpacity: 0.5,
              zIndexOffset: 800
            }).addTo(drawnItems.current);
            
            // Add click popup with trigger details
            circle.bindPopup(`
              <div>
                <h4>Trigger ${trigger.id}</h4>
                <p><strong>Type:</strong> Portable</p>
                <p><strong>Center:</strong> (${trigger.center[1].toFixed(2)}, ${trigger.center[0].toFixed(2)})</p>
                <p><strong>Radius:</strong> ${trigger.radius.toFixed(2)} units</p>
                <p><strong>Status:</strong> ${trigger.isContained ? 'Contained' : 'Not Contained'}</p>
              </div>
            `);
            
            L.marker(trigger.center, {
              icon: L.divIcon({
                className: "trigger-label",
                html: `<span>${trigger.id}</span>`,
                iconSize: [20, 20],
              })
            }).addTo(drawnItems.current);
          } else if (trigger.latLngs) {
            const isWithinBoundingBox = trigger.latLngs.some(([lat, lng]) => {
              return (
                lng >= zoneBoundingBox.xMin &&
                lng <= zoneBoundingBox.xMax &&
                lat >= zoneBoundingBox.yMin &&
                lat <= zoneBoundingBox.yMax
              );
            });

            if (isWithinBoundingBox) {
              const polygon = L.polygon(trigger.latLngs, { color: "blue", fill: false }).addTo(drawnItems.current);
              
              // Add click popup with trigger details
              const centroid = trigger.latLngs.reduce((acc, [lat, lng]) => [acc[0] + lat, acc[1] + lng], [0, 0]);
              centroid[0] /= trigger.latLngs.length;
              centroid[1] /= trigger.latLngs.length;
              
              polygon.bindPopup(`
                <div>
                  <h4>Trigger ${trigger.id}</h4>
                  <p><strong>Type:</strong> Zone-based</p>
                  <p><strong>Center:</strong> (${centroid[1].toFixed(2)}, ${centroid[0].toFixed(2)})</p>
                  <p><strong>Vertices:</strong> ${trigger.latLngs.length}</p>
                </div>
              `);
              
              L.marker(centroid, {
                icon: L.divIcon({
                  className: "trigger-label",
                  html: `<span>${trigger.id}</span>`,
                  iconSize: [20, 20],
                })
              }).addTo(drawnItems.current);
            }
          }
        }
      });
      if (mapInstance.current) {
        mapInstance.current.invalidateSize();
        console.log("Map size invalidated to force refresh");
      }
    } else {
      console.log("No triggers to render or showExistingTriggers is false", { showExistingTriggers, memoizedTriggerPolygons });
    }
  }, [useLeaflet, mapData, zoneVertices, checkedZones, memoizedTriggerPolygons, mapInitialized]);

  // Zoom-aware tag marker updates with extended timeouts and visibility filtering
  useEffect(() => {
    console.log("Tag marker useEffect triggered", { tagsData, isConnected, mapInstance: !!mapInstance.current, mapInitialized, triggers });
    if (!useLeaflet || !mapInstance.current || !mapData || !mapInitialized) return;

    if (updateTimeout.current) {
      clearTimeout(updateTimeout.current);
    }

    updateTimeout.current = setTimeout(() => {
      // Check if zoom is in progress
      if (isZoomingRef.current) {
        console.log("⏸️ Skipping marker update - zoom in progress");
        pendingUpdateRef.current = true; // Mark that we have a pending update
        return;
      }

      // Execute the marker update
      executeMarkerUpdate();
    }, 100);

    return () => {
      if (updateTimeout.current) {
        clearTimeout(updateTimeout.current);
      }
    };
  }, [useLeaflet, tagsData, isConnected, mapData, zones, mapInitialized, triggers, hiddenTags]);

  // Cleanup function for component unmount
  useEffect(() => {
    return () => {
      // Clear all timeouts on unmount
      Object.values(tagTimeoutRef.current).forEach(timeout => {
        clearTimeout(timeout);
      });
      tagTimeoutRef.current = {};
      tagLastSeenRef.current = {};
      tagLastPositionRef.current = {};
    };
  }, []);

  // Responsive map style
  const mapStyle = {
    height: height,
    width: enableResponsive ? width : "800px",
    border: "2px solid black",
    position: "relative"
  };

  // Legend component
  const Legend = () => (
    <div style={{
      position: 'absolute',
      top: '10px',
      right: '10px',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      padding: '10px',
      borderRadius: '5px',
      border: '1px solid #ccc',
      fontSize: '12px',
      zIndex: 1000,
      minWidth: '150px'
    }}>
      <h4 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>Legend</h4>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
        <div style={{ width: '10px', height: '10px', backgroundColor: 'red', borderRadius: '50%', marginRight: '8px' }}></div>
        <span>Active Tag</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
        <div style={{ width: '10px', height: '10px', backgroundColor: 'gray', borderRadius: '50%', marginRight: '8px', opacity: 0.7 }}></div>
        <span>Stale Tag</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
        <div style={{ width: '10px', height: '10px', backgroundColor: 'red', borderRadius: '50%', marginRight: '8px', opacity: 0.5 }}></div>
        <span>Disconnected</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
        <div style={{ width: '10px', height: '2px', backgroundColor: 'blue', marginRight: '8px' }}></div>
        <span>Zone Trigger</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
        <div style={{ width: '10px', height: '10px', border: '2px solid purple', borderRadius: '50%', marginRight: '8px' }}></div>
        <span>Portable Trigger</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', marginTop: '8px' }}>
        <span style={{ color: isConnected ? 'green' : 'red' }}>
          ●
        </span>
        <span style={{ marginLeft: '4px' }}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
        {mapMode !== 'view' && (
          <span style={{ marginLeft: '8px', fontSize: '10px', color: '#666' }}>
            Mode: {mapMode}
          </span>
        )}
      </div>
    </div>
  );

  // Tag visibility controls
  const TagControls = () => (
    <div style={{
      position: 'absolute',
      bottom: '50px',
      right: '10px',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      padding: '10px',
      borderRadius: '5px',
      border: '1px solid #ccc',
      fontSize: '12px',
      zIndex: 1000,
      maxHeight: '200px',
      overflowY: 'auto',
      minWidth: '120px'
    }}>
      <h4 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>Tag Visibility</h4>
      {activeTags.length > 0 ? (
        activeTags.map(tagId => (
          <div key={tagId} style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
            <input
              type="checkbox"
              id={`tag-${tagId}`}
              checked={!hiddenTags.has(tagId)}
              onChange={() => toggleTagVisibility(tagId)}
              style={{ marginRight: '6px' }}
            />
            <label htmlFor={`tag-${tagId}`} style={{ cursor: 'pointer' }}>
              {tagId}
            </label>
          </div>
        ))
      ) : (
        <div style={{ color: '#666', fontStyle: 'italic' }}>No active tags</div>
      )}
      {enableKeyboardShortcuts && activeTags.length > 0 && (
        <div style={{ marginTop: '8px', fontSize: '10px', color: '#999', borderTop: '1px solid #ddd', paddingTop: '4px' }}>
          💡 Press V to toggle all tags, ? for shortcuts
        </div>
      )}
    </div>
  );

  return (
    <div style={{ position: 'relative' }}>
      {error && <div style={{ color: "red" }}>{error}</div>}
      {useLeaflet ? (
        <div style={mapStyle}>
          <div ref={mapRef} style={{ height: "100%", width: "100%" }} />
          {showLegend && <Legend />}
          {enableControls && activeTags.length > 0 && <TagControls />}
        </div>
      ) : (
        <canvas ref={canvasRef} style={{ border: "2px solid black" }} />
      )}
    </div>
  );
});

NewTriggerViewer.defaultProps = {
  triggers: [],
  enableResponsive: true,
  enableControls: true,
  height: "600px",
  width: "100%",
  enableKeyboardShortcuts: true
};

export default NewTriggerViewer;