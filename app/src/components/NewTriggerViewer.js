// /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerViewer.js
// Version: 0.0.13 - Fixed sporadic marker display with delayed updates, improved map view stability, enhanced logging
// Enhanced with detailed comments for clarity
import React, { useEffect, useRef, useState, memo } from "react"; // Core React imports for state and effects
import L from "leaflet"; // Leaflet library for interactive maps
import "leaflet/dist/leaflet.css"; // Leaflet base styles
import "leaflet-draw/dist/leaflet.draw.css"; // Styles for drawing plugin
import "leaflet-draw"; // Plugin for drawing shapes on the map
import "./Map.css"; // Custom styles for this component

// Memoized component to prevent unnecessary re-renders
const NewTriggerViewer = memo(({
  mapId,              // ID of the map to fetch from API
  zones,              // Array of zone objects
  checkedZones,       // Array of zone IDs currently selected
  vertices,           // Pre-fetched vertices (not used directly here)
  onVerticesUpdate,   // Callback to notify parent of vertex changes
  useLeaflet,         // Boolean to toggle between Leaflet and canvas rendering
  enableDrawing,      // Boolean to enable polygon drawing
  onDrawComplete,     // Callback when drawing is completed
  showExistingTriggers, // Boolean to display existing triggers
  existingTriggerPolygons, // Array of existing trigger polygons
  tagData,            // Current tag position data (x, y, z, etc.)
  isConnected         // WebSocket connection status
}) => {
  // Refs for managing DOM and Leaflet elements
  const mapRef = useRef(null);           // DOM reference for Leaflet map container
  const mapInstance = useRef(null);      // Leaflet map instance
  const canvasRef = useRef(null);        // DOM reference for canvas (non-Leaflet mode)
  const [mapData, setMapData] = useState(null); // State for map data (image URL, bounds)
  const [zoneVertices, setZoneVertices] = useState([]); // State for fetched zone vertices
  const [error, setError] = useState(null); // State for error messages
  const isInitialized = useRef(false);   // Flag to prevent multiple initializations
  const ctxRef = useRef(null);           // Canvas 2D context for drawing
  const imageRef = useRef(null);         // Image object for canvas map
  const drawnItems = useRef(new L.FeatureGroup()); // Leaflet group for drawn layers
  const canvasBounds = useRef({ x: 0, y: 0, width: 800, height: 600 }); // Canvas drawing area
  const tagMarkerRef = useRef(null);     // Reference to the tag’s marker on the map
  const userInteracted = useRef(false);  // Tracks if user has manually zoomed/panned
  const updateTimeout = useRef(null);    // Timeout for delayed marker updates

  // Effect to fetch map data when mapId changes
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

  // Effect to fetch zone vertices when checkedZones change
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

  // Effect to initialize canvas-based map (non-Leaflet mode)
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
  }, [mapData, useLeaflet, zoneVertices]);

  // Function to draw zone boundaries on the canvas
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

  // Effect to initialize Leaflet map and draw initial elements
  useEffect(() => {
    if (useLeaflet && mapData && mapRef.current && !mapInstance.current) {
      mapInstance.current = L.map(mapRef.current, { 
        crs: L.CRS.Simple,
        zoomControl: true,
        minZoom: -5,
        maxZoom: 5
      }).fitBounds(mapData.bounds);
      L.imageOverlay(mapData.imageUrl, mapData.bounds).addTo(mapInstance.current);
      mapInstance.current.addLayer(drawnItems.current);
      console.log("Map bounds:", mapData.bounds);

      mapInstance.current.on('zoomend moveend', () => {
        userInteracted.current = true;
        console.log("User interacted with map, zoom/center locked");
      });

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

      if (showExistingTriggers && existingTriggerPolygons && existingTriggerPolygons.length > 0) {
        existingTriggerPolygons.forEach(trigger => {
          if (trigger && trigger.latLngs) {
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
        });
      }

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
    }

    return () => {
      if (mapInstance.current) {
        try {
          mapInstance.current.off();
          mapInstance.current.remove();
          console.log("Leaflet map cleaned up");
        } catch (error) {
          console.error("Error cleaning up Leaflet map:", error);
        }
        mapInstance.current = null;
        tagMarkerRef.current = null;
        userInteracted.current = false;
        isInitialized.current = false;
        if (updateTimeout.current) {
          clearTimeout(updateTimeout.current);
          updateTimeout.current = null;
        }
      }
    };
  }, [mapData, useLeaflet, zoneVertices, checkedZones, enableDrawing, onDrawComplete, showExistingTriggers, existingTriggerPolygons]);

  // Effect to manage tag marker updates and map view adjustments
  useEffect(() => {
    if (!useLeaflet || !mapInstance.current || !mapData) return;

    // Clear any existing timeout to prevent multiple updates
    if (updateTimeout.current) {
      clearTimeout(updateTimeout.current);
    }

    // Delay marker update to reduce flickering
    updateTimeout.current = setTimeout(() => {
      if (tagData && isConnected) {
        const { x, y } = tagData;
        const latLng = [y, x];

        // Check if the position is within map bounds
        const bounds = L.latLngBounds(mapData.bounds);
        if (!bounds.contains(latLng)) {
          console.warn(`Tag position ${latLng} is outside map bounds:`, mapData.bounds);
          return;
        }

        if (!tagMarkerRef.current) {
          // Create a new marker
          tagMarkerRef.current = L.circle(latLng, {
            color: "red",
            fillColor: "red",
            fillOpacity: 0.8,
            radius: 0.4572,
            zIndexOffset: 1000
          }).addTo(mapInstance.current);
          console.log("Tag marker created at:", latLng);
        } else {
          // Update existing marker position
          tagMarkerRef.current.setLatLng(latLng);
          tagMarkerRef.current.setStyle({ color: "red", fillColor: "red" });
          console.log("Tag marker updated to:", latLng);
        }

        if (!userInteracted.current) {
          const tagBounds = L.latLngBounds(latLng, latLng);
          mapInstance.current.fitBounds(tagBounds.pad(0.5), { animate: false });
          console.log("Map centered on tag:", latLng);
        }
      } else if (tagData && !isConnected && tagMarkerRef.current) {
        // Change marker to gray when disconnected
        tagMarkerRef.current.setStyle({ color: "gray", fillColor: "gray" });
        console.log("Tag marker turned gray due to disconnect");
        if (!userInteracted.current) {
          mapInstance.current.fitBounds(mapData.bounds);
          console.log("Map reset to full view on disconnect");
        }
      } else if (!tagData && tagMarkerRef.current) {
        // Remove marker if tag data is cleared
        mapInstance.current.removeLayer(tagMarkerRef.current);
        tagMarkerRef.current = null;
        console.log("Tag marker removed due to no tag data");
        if (!userInteracted.current) {
          mapInstance.current.fitBounds(mapData.bounds);
          console.log("Map reset to full view");
        }
      }
    }, 100); // 100ms delay to reduce flickering

    return () => {
      if (updateTimeout.current) {
        clearTimeout(updateTimeout.current);
      }
    };
  }, [useLeaflet, tagData, isConnected, mapData]);

  // Render the component: either Leaflet map or canvas
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

export default NewTriggerViewer;