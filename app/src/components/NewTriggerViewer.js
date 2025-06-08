/* Name: NewTriggerViewer.js */
/* Version: 0.1.2 */
/* Created: 971201 */
/* Modified: 250526 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: JavaScript file for ParcoRTLS frontend */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerViewer.js
// Version: v0.1.2-250526 - Fixed triggers undefined error with default prop and optional chaining, retained WebSocket heartbeat logic, bumped from v0.1.1
// Previous: Added WebSocket connection for heartbeat handling, bumped from v0.1.0
// Previous: Removed division scaling for portable trigger radii to match map scale, bumped from v0.0.33
// Previous: Scaled tag markers based on associated trigger radius_ft, bumped from v0.0.32 (v0.0.33)
// Previous: Fixed map size invalidation loop by memoizing trigger polygons, bumped from v0.0.31 (v0.0.32)
// Previous: Added portable trigger rendering in canvas mode, enhanced logging (v0.0.31)
// Previous: Added non-portable trigger rendering in canvas mode, added debug logging (v0.0.30)
// Previous: Fixed marker scaling with divIcon, added debug logging (v0.0.29)

import React, { useEffect, useRef, useState, memo, useMemo } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import "leaflet-draw";
import "./Map.css";

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
  triggers = [] // Default to empty array
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

  // WebSocket connection for heartbeats
  useEffect(() => {
    const ws = new WebSocket(`ws://192.168.210.226:8002/ws/realtime?client_id=trigger_viewer_${Date.now()}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("✅ WebSocket connected to ws://192.168.210.226:8002/ws/realtime");
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
  }, []);

  useEffect(() => {
    if (mapId) {
      const fetchMapData = async () => {
        try {
          const response = await fetch(`http://192.168.210.226:8000/zoneviewer/get_map_data/${mapId}`);
          if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
          const data = await response.json();
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
  }, [mapId]);

  useEffect(() => {
    if (checkedZones.length === 0) {
      setZoneVertices([]);
      if (onVerticesUpdate) onVerticesUpdate([]);
      return;
    }

    const fetchZoneVertices = async () => {
      try {
        const verticesPromises = checkedZones.map(async (zoneId) => {
          const response = await fetch(`http://192.168.210.226:8000/zoneviewer/get_vertices_for_campus/${zoneId}`);
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
  }, [checkedZones, onVerticesUpdate]);

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

  useEffect(() => {
    if (useLeaflet && mapData && mapRef.current && !mapInstance.current) {
      mapInstance.current = L.map(mapRef.current, { 
        crs: L.CRS.Simple,
        zoomControl: true,
        minZoom: -5,
        maxZoom: 7
      }).fitBounds(mapData.bounds);
      L.imageOverlay(mapData.imageUrl, mapData.bounds).addTo(mapInstance.current);
      mapInstance.current.addLayer(drawnItems.current);
      console.log("Map bounds:", mapData.bounds);

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
      console.log("Leaflet map initialized");
    }

    return () => {
      if (mapInstance.current) {
        try {
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
  }, [mapData?.imageUrl, mapData?.bounds, useLeaflet, enableDrawing, onDrawComplete]);

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
              L.polygon(trigger.latLngs, { color: "blue", fill: false }).addTo(drawnItems.current);
              const centroid = trigger.latLngs.reduce((acc, [lat, lng]) => [acc[0] + lat, acc[1] + lng], [0, 0]);
              centroid[0] /= trigger.latLngs.length;
              centroid[1] /= trigger.latLngs.length;
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

  useEffect(() => {
    console.log("Tag marker useEffect triggered", { tagsData, isConnected, mapInstance: !!mapInstance.current, mapInitialized, triggers });
    if (!useLeaflet || !mapInstance.current || !mapData || !mapInitialized) return;

    if (updateTimeout.current) {
      clearTimeout(updateTimeout.current);
    }

    updateTimeout.current = setTimeout(() => {
      const selectedZoneId = zones[0]?.i_zn || "N/A";

      Object.keys(tagMarkersRef.current).forEach(tagId => {
        const tagData = tagsData[tagId];
        const tagZoneId = tagData?.zone_id || selectedZoneId;
        if (!tagData || tagZoneId !== selectedZoneId) {
          const marker = tagMarkersRef.current[tagId];
          if (marker && mapInstance.current.hasLayer(marker)) {
            mapInstance.current.removeLayer(marker);
            console.log(`Tag marker for ${tagId} removed due to zone mismatch or no tag data`, { tagZoneId, selectedZoneId });
          }
          delete tagMarkersRef.current[tagId];
        }
      });

      if (!isConnected) {
        Object.values(tagMarkersRef.current).forEach(marker => {
          marker.setStyle({ color: "gray", fillColor: "gray" });
          console.log("Tag marker turned gray due to disconnect");
        });
        return;
      }

      Object.entries(tagsData).forEach(([tagId, tagData]) => {
        const tagZoneId = tagData.zone_id || selectedZoneId;
        if (tagZoneId !== selectedZoneId) return;

        const { x, y } = tagData;
        const latLng = [y, x];

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
          marker = L.marker(latLng, {
            icon: L.divIcon({
              className: "tag-marker",
              html: `<div style="background-color: red; width: ${markerSize}px; height: ${markerSize}px; border-radius: 50%;"></div>`,
              iconSize: [markerSize, markerSize],
              iconAnchor: [markerSize / 2, markerSize / 2]
            }),
            zIndexOffset: 1000
          }).addTo(mapInstance.current);
          marker.bindTooltip(`Tag ${tagId}`, { permanent: false, direction: "top" });
          tagMarkersRef.current[tagId] = marker;
          console.log(`Tag marker created for ${tagId} at:`, latLng);
        } else {
          marker.setLatLng(latLng);
          marker.setIcon(L.divIcon({
            className: "tag-marker",
            html: `<div style="background-color: red; width: ${markerSize}px; height: ${markerSize}px; border-radius: 50%;"></div>`,
            iconSize: [markerSize, markerSize],
            iconAnchor: [markerSize / 2, markerSize / 2]
          }));
          console.log(`Tag marker updated for ${tagId} to:`, latLng);
        }

        if (firstTagAppearance.current && !userInteracted.current) {
          const tagBounds = L.latLngBounds(latLng, latLng);
          mapInstance.current.setView(latLng, 7, { animate: false });
          console.log(`Map zoomed to tag ${tagId} at:`, latLng);
          firstTagAppearance.current = false;
        }
      });
    }, 100);

    return () => {
      if (updateTimeout.current) {
        clearTimeout(updateTimeout.current);
      }
    };
  }, [useLeaflet, tagsData, isConnected, mapData, zones, mapInitialized, triggers]);

  return (
    <div>
      {error && <div style={{ color: "red" }}>{error}</div>}
      {useLeaflet ? (
        <div ref={mapRef} style={{ height: "600px", width: "800px", border: "2px solid black" }} />
      ) : (
        <canvas ref={canvasRef} style={{ border: "2px solid black" }} />
      )}
    </div>
  );
});

NewTriggerViewer.defaultProps = {
  triggers: []
};

export default NewTriggerViewer;