// /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerViewer.js
// Version: v0.0.19 - Fixed tag marker not appearing after zone switch, updated zone label on zone switch, bumped from v0.0.18
// Previous: Added zone check for tag marker and ensured marker color updates (v0.0.18)
// Previous: Added zone ID label to Leaflet map (v0.0.17)
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
  isConnected
}) => {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const canvasRef = useRef(null);
  const [mapData, setMapData] = useState(null);
  const [zoneVertices, setZoneVertices] = useState([]);
  const [error, setError] = useState(null);
  const [mapInitialized, setMapInitialized] = useState(false); // Track map initialization
  const isInitialized = useRef(false);
  const ctxRef = useRef(null);
  const imageRef = useRef(null);
  const drawnItems = useRef(new L.FeatureGroup());
  const canvasBounds = useRef({ x: 0, y: 0, width: 800, height: 600 });
  const tagMarkerRef = useRef(null);
  const zoneLabelRef = useRef(null); // Ref for zone label
  const userInteracted = useRef(false);
  const updateTimeout = useRef(null);
  const firstTagAppearance = useRef(true);

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
          mapInstance.current.remove();
          console.log("Leaflet map cleaned up");
        } catch (error) {
          console.error("Error cleaning up Leaflet map:", error);
        }
        mapInstance.current = null;
        tagMarkerRef.current = null;
        zoneLabelRef.current = null;
        isInitialized.current = false;
        if (updateTimeout.current) {
          clearTimeout(updateTimeout.current);
          updateTimeout.current = null;
        }
        setMapInitialized(false);
      }
    };
  }, [mapData?.imageUrl, mapData?.bounds, useLeaflet, enableDrawing]);

  // Update zone label when zones change
  useEffect(() => {
    if (!useLeaflet || !mapInstance.current || !mapData) return;

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
  }, [useLeaflet, mapData, zoneVertices, checkedZones, showExistingTriggers, existingTriggerPolygons, mapInitialized]);

  useEffect(() => {
    console.log("Tag marker useEffect triggered", { tagData, isConnected, mapInstance: !!mapInstance.current, mapInitialized });
    if (!useLeaflet || !mapInstance.current || !mapData || !mapInitialized) return;

    if (updateTimeout.current) {
      clearTimeout(updateTimeout.current);
    }

    updateTimeout.current = setTimeout(() => {
      // Only plot the tag marker if the tag's zone matches the selected zone
      const selectedZoneId = zones[0]?.i_zn; // Assuming zones[0] is the currently selected zone
      const tagZoneId = tagData?.zone_id || selectedZoneId;

      if (!tagData || tagZoneId !== selectedZoneId) {
        if (tagMarkerRef.current) {
          mapInstance.current.removeLayer(tagMarkerRef.current);
          tagMarkerRef.current = null;
          console.log("Tag marker removed due to zone mismatch or no tag data", { tagZoneId, selectedZoneId });
          firstTagAppearance.current = true;
        }
        return;
      }

      if (tagData && isConnected) {
        const { x, y } = tagData;
        const latLng = [y, x];

        const bounds = L.latLngBounds(mapData.bounds);
        if (!bounds.contains(latLng)) {
          console.warn(`Tag position ${latLng} is outside map bounds:`, mapData.bounds);
          return;
        }

        if (!tagMarkerRef.current) {
          tagMarkerRef.current = L.circle(latLng, {
            color: "red",
            fillColor: "red",
            fillOpacity: 0.8,
            radius: 0.4572,
            zIndexOffset: 1000
          }).addTo(mapInstance.current);
          console.log("Tag marker created at:", latLng);
        } else {
          tagMarkerRef.current.setLatLng(latLng);
          tagMarkerRef.current.setStyle({ color: "red", fillColor: "red" });
          console.log("Tag marker updated to:", latLng);
        }

        if (firstTagAppearance.current && !userInteracted.current) {
          const tagBounds = L.latLngBounds(latLng, latLng);
          mapInstance.current.fitBounds(tagBounds.pad(0.5), { animate: false });
          console.log("Map centered on tag:", latLng);
          firstTagAppearance.current = false;
        }
      } else if (tagData && !isConnected && tagMarkerRef.current) {
        tagMarkerRef.current.setStyle({ color: "gray", fillColor: "gray" });
        console.log("Tag marker turned gray due to disconnect");
      } else if (!tagData && tagMarkerRef.current) {
        mapInstance.current.removeLayer(tagMarkerRef.current);
        tagMarkerRef.current = null;
        console.log("Tag marker removed due to no tag data");
        firstTagAppearance.current = true;
      }
    }, 100);

    return () => {
      if (updateTimeout.current) {
        clearTimeout(updateTimeout.current);
      }
    };
  }, [useLeaflet, tagData, isConnected, mapData, zones, mapInitialized]); // Added mapInitialized to dependencies

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