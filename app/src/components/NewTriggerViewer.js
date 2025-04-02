// /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerViewer.js
// Version: 0.0.10 - Restore initial bounds, maintain zoom after connect and interaction
import React, { useEffect, useRef, useState, memo } from "react";
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
  tagData,
  isConnected // New prop
}) => {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const canvasRef = useRef(null);
  const [mapData, setMapData] = useState(null);
  const [zoneVertices, setZoneVertices] = useState([]);
  const [error, setError] = useState(null);
  const isInitialized = useRef(false);
  const ctxRef = useRef(null);
  const imageRef = useRef(null);
  const drawnItems = useRef(new L.FeatureGroup());
  const canvasBounds = useRef({ x: 0, y: 0, width: 800, height: 600 });
  const tagMarkerRef = useRef(null);
  const userInteracted = useRef(false); // Track user zoom/pan

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
            n_ord: vertex.order,
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
      };

      img.onerror = () => setError("Failed to load map image.");
      isInitialized.current = true;
    }
  }, [mapData, useLeaflet, zoneVertices]);

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

  useEffect(() => {
    if (useLeaflet && mapData && mapRef.current && !mapInstance.current) {
      mapInstance.current = L.map(mapRef.current, { 
        crs: L.CRS.Simple,
        zoomControl: true
      }).fitBounds(mapData.bounds); // Restore initial full view
      L.imageOverlay(mapData.imageUrl, mapData.bounds).addTo(mapInstance.current);
      mapInstance.current.addLayer(drawnItems.current);
      console.log("Map bounds:", mapData.bounds);

      // Track user interaction
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

      if (tagData && !tagMarkerRef.current) {
        tagMarkerRef.current = L.circle([tagData.y, tagData.x], {
          color: "red",
          fillColor: "red",
          fillOpacity: 0.8,
          radius: 0.4572,
          zIndexOffset: 1000
        }).addTo(mapInstance.current);
        console.log("Tag marker created at:", [tagData.y, tagData.x]);
      }
    }

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
        tagMarkerRef.current = null;
        userInteracted.current = false;
      }
    };
  }, [mapData, useLeaflet, zoneVertices, checkedZones, enableDrawing, onDrawComplete, showExistingTriggers, existingTriggerPolygons]);

  useEffect(() => {
    if (!useLeaflet || !mapInstance.current) return;

    if (tagData && !tagMarkerRef.current) {
      tagMarkerRef.current = L.circle([tagData.y, tagData.x], {
        color: "red",
        fillColor: "red",
        fillOpacity: 0.8,
        radius: 0.4572,
        zIndexOffset: 1000
      }).addTo(mapInstance.current);
      console.log("Tag marker created at:", [tagData.y, tagData.x]);
    } else if (tagData && tagMarkerRef.current) {
      tagMarkerRef.current.setLatLng([tagData.y, tagData.x]);
      console.log("Tag marker updated to:", [tagData.y, tagData.x]);
      // Only reset to full bounds if not connected or not interacted
      if (!isConnected || !userInteracted.current) {
        mapInstance.current.fitBounds(mapData.bounds);
      }
    } else if (!tagData && tagMarkerRef.current) {
      mapInstance.current.removeLayer(tagMarkerRef.current);
      tagMarkerRef.current = null;
      console.log("Tag marker removed");
      mapInstance.current.fitBounds(mapData.bounds); // Reset view when disconnected
    }
  }, [useLeaflet, tagData, isConnected, mapData]);

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