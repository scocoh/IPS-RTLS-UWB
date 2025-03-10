import React, { useEffect, useRef, useState, memo } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css"; // Leaflet core CSS
import "leaflet-draw/dist/leaflet.draw.css"; // Leaflet.Draw CSS
import "leaflet-draw"; // Import Leaflet.Draw
import "./Map.css"; // Canvas styling

const Map = memo(({ zoneId, onDrawComplete, triggerColor, useLeaflet }) => {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const drawnItems = useRef(new L.FeatureGroup());
  const canvasRef = useRef(null);
  const [mapData, setMapData] = useState(null);
  const [error, setError] = useState(null);
  const isInitialized = useRef(false);
  const points = useRef([]);
  const isDrawing = useRef(false);
  const ctxRef = useRef(null);
  const imageRef = useRef(null);
  const lastClickTime = useRef(0); // For debouncing double-click

  // Fetch map data when zoneId changes
  useEffect(() => {
    if (zoneId && !mapData) {
      const fetchMapData = async () => {
        try {
          const response = await fetch(`/maps/get_map_data/${zoneId}`);
          if (!response.ok) {
            const text = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
          }
          const data = await response.json();
          console.log("Map data fetched:", data);
          setMapData(data);
          setError(null);
        } catch (error) {
          console.error("Error fetching map data:", error);
          setError(`Error fetching map data: ${error.message}`);
        }
      };
      fetchMapData();
    }
  }, [zoneId, mapData]);

  // Canvas rendering logic
  useEffect(() => {
    if (mapData && canvasRef.current && !useLeaflet && !isInitialized.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");
      ctxRef.current = ctx;

      canvas.width = 600;
      canvas.height = 500;

      const img = new Image();
      img.crossOrigin = "anonymous";
      img.src = mapData.imageUrl;
      imageRef.current = img;

      img.onload = () => {
        console.log("Canvas: Map image loaded successfully:", mapData.imageUrl, "Dimensions:", img.width, "x", img.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        const getCanvasCoordinates = (e) => {
          const rect = canvas.getBoundingClientRect();
          const scaleX = canvas.width / rect.width;
          const scaleY = canvas.height / rect.height;
          const x = (e.clientX - rect.left) * scaleX;
          const y = (e.clientY - rect.top) * scaleY;
          console.log("Raw click coordinates:", { x, y });
          return { x, y };
        };

        const drawPolygon = (points, currentPoint = null, close = false) => {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          if (points.length === 0) return;
          ctx.beginPath();
          ctx.moveTo(points[0].x, points[0].y);
          for (let i = 1; i < points.length; i++) {
            ctx.lineTo(points[i].x, points[i].y);
          }
          if (currentPoint) ctx.lineTo(currentPoint.x, currentPoint.y);
          if (close) ctx.closePath();
          ctx.strokeStyle = triggerColor || "red";
          ctx.stroke();
          points.forEach((point) => {
            ctx.beginPath();
            ctx.arc(point.x, point.y, 5, 0, Math.PI * 2);
            ctx.fillStyle = triggerColor || "red";
            ctx.fill();
            ctx.closePath();
          });
        };

        const scalePoints = (points) => {
          const canvasWidth = canvas.width;
          const canvasHeight = canvas.height;
          const xMin = -80;
          const xMax = 160;
          const yMin = -40;
          const yMax = 160;
          const xRange = xMax - xMin;
          const yRange = yMax - yMin;
          return points.map((point, index) => {
            const x = xMin + (point.x / canvasWidth) * xRange;
            const y = yMax - (point.y / canvasHeight) * yRange;
            return { n_x: x, n_y: y, n_z: 0, n_ord: index + 1 };
          }).filter((point, index, self) =>
            index === self.findIndex((p) => p.n_x === point.n_x && p.n_y === point.n_y)
          );
        };

        const handleMouseDown = (e) => {
          if (e.button === 0) {
            isDrawing.current = true;
            const point = getCanvasCoordinates(e);
            if (points.current.length === 0 || 
                Math.hypot(point.x - points.current[points.current.length - 1].x, 
                          point.y - points.current[points.current.length - 1].y) > 5) {
              points.current.push(point);
              drawPolygon(points.current);
            }
          }
        };

        const handleMouseMove = (e) => {
          if (isDrawing.current) {
            const point = getCanvasCoordinates(e);
            drawPolygon(points.current, point);
          }
        };

        const handleMouseUp = (e) => {
          if (e.button === 0) isDrawing.current = false;
        };

        const handleDoubleClick = (e) => {
          const now = Date.now();
          if (now - lastClickTime.current < 500) return;
          lastClickTime.current = now;
          isDrawing.current = false;
          if (points.current.length >= 3) {
            drawPolygon(points.current, null, true);
            const scaledPoints = scalePoints(points.current);
            console.log("Scaled points (Canvas):", scaledPoints);
            if (onDrawComplete) onDrawComplete(JSON.stringify(scaledPoints));
            points.current = [];
          }
        };

        canvas.addEventListener("mousedown", handleMouseDown);
        canvas.addEventListener("mousemove", handleMouseMove);
        canvas.addEventListener("mouseup", handleMouseUp);
        canvas.addEventListener("dblclick", handleDoubleClick);

        return () => {
          canvas.removeEventListener("mousedown", handleMouseDown);
          canvas.removeEventListener("mousemove", handleMouseMove);
          canvas.removeEventListener("mouseup", handleMouseUp);
          canvas.removeEventListener("dblclick", handleDoubleClick);
        };
      };

      img.onerror = () => {
        console.error("Failed to load map image:", mapData.imageUrl);
        setError("Failed to load map image. Please check the server response.");
      };
    }
  }, [mapData, onDrawComplete, triggerColor, useLeaflet]);

  // Leaflet rendering logic
  useEffect(() => {
    if (mapData && mapRef.current && useLeaflet && !isInitialized.current) {
      mapInstance.current = L.map(mapRef.current, {
        crs: L.CRS.Simple,
        minZoom: -5,
        maxZoom: 5,
        zoomControl: true,
        attributionControl: false,
      });

      mapInstance.current.eachLayer((layer) => {
        if (layer instanceof L.TileLayer) mapInstance.current.removeLayer(layer);
      });

      const xMin = mapData.bounds[0][1]; // -80
      const xMax = mapData.bounds[1][1]; // 160
      const yMin = mapData.bounds[0][0]; // -40
      const yMax = mapData.bounds[1][0]; // 160
      const xRange = xMax - xMin; // 240
      const yRange = yMax - yMin; // 200

      const img = new Image();
      img.crossOrigin = "anonymous";
      img.src = mapData.imageUrl;

      img.onload = () => {
        console.log("Leaflet: Map image loaded successfully:", mapData.imageUrl, "Dimensions:", img.width, "x", img.height);
        const pixelBounds = [
          [0, 0], // Bottom-left in pixel coordinates
          [600, 500], // Top-right in pixel coordinates
        ];

        // Use logical bounds for image overlay
        L.imageOverlay(mapData.imageUrl, [
          [yMin, xMin], // Bottom-left [-40, -80]
          [yMax, xMax], // Top-right [160, 160]
        ]).addTo(mapInstance.current);
        mapInstance.current.fitBounds([
          [yMin, xMin],
          [yMax, xMax],
        ]);

        mapInstance.current.addLayer(drawnItems.current);

        const colorMap = {
          red: "#ff0000",
          green: "#00ff00",
          blue: "#0000ff",
        };

        const drawControl = new L.Control.Draw({
          edit: { featureGroup: drawnItems.current },
          draw: {
            polygon: {
              shapeOptions: { color: colorMap[triggerColor] || "#ff0000", weight: 2 },
            },
            rectangle: false,
            polyline: false,
            circle: false,
            marker: false,
            circlemarker: false,
          },
        });
        mapInstance.current.addControl(drawControl);

        mapInstance.current.on(L.Draw.Event.CREATED, (event) => {
          const layer = event.layer;
          drawnItems.current.addLayer(layer);
          const coords = layer.getLatLngs()[0].map((latLng, index) => {
            console.log(`Raw latLng for point ${index + 1}:`, { lat: latLng.lat, lng: latLng.lng });
            // Normalize latLng to pixel bounds and map to logical coordinates
            const normalizedLat = (latLng.lat - yMin) / yRange; // Normalize to [0, 1]
            const normalizedLng = (latLng.lng - xMin) / xRange; // Normalize to [0, 1]
            const x = xMin + normalizedLng * xRange; // Map to [-80, 160]
            const y = yMin + normalizedLat * yRange; // Map to [-40, 160]
            return { n_x: x, n_y: y, n_z: 0, n_ord: index + 1 };
          });
          console.log("Scaled points (Leaflet):", coords);
          if (onDrawComplete) onDrawComplete(JSON.stringify(coords));
        });

        isInitialized.current = true;
      };

      img.onerror = () => {
        console.error("Failed to load map image:", mapData.imageUrl);
        setError("Failed to load map image. Please check the server response.");
      };
    }
  }, [mapData, onDrawComplete, triggerColor, useLeaflet]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
        isInitialized.current = false;
      }
      if (mapData && imageRef.current) {
        const img = new Image();
        img.src = mapData.imageUrl; // Clear any pending loads
      }
    };
  }, [mapData]);

  if (useLeaflet) {
    return (
      <div>
        {error && <div style={{ color: "red", marginBottom: "10px" }}>{error}</div>}
        <div ref={mapRef} style={{ height: "500px", width: "600px", border: "2px solid black" }} />
      </div>
    );
  } else {
    return (
      <div>
        {error && <div style={{ color: "red", marginBottom: "10px" }}>{error}</div>}
        <canvas ref={canvasRef} id="map" style={{ border: "2px solid black" }} />
      </div>
    );
  }
});

export default Map;