// /home/parcoadmin/parco_fastapi/app/src/components/MapZoneBuilder.js
import React, { useEffect, useRef, useState, memo } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import "leaflet-draw";
import "./Map.css";

const MapZoneBuilder = memo(({ zoneId, onDrawComplete, triggerColor, useLeaflet, drawnItems }) => {
    const mapRef = useRef(null);
    const mapInstance = useRef(null);
    const canvasRef = useRef(null);
    const [mapData, setMapData] = useState(null);
    const [error, setError] = useState(null);
    const isInitialized = useRef(false);
    const points = useRef([]);
    const isDrawing = useRef(false);
    const ctxRef = useRef(null);
    const imageRef = useRef(null);

    // Fetch map data
    useEffect(() => {
        if (zoneId) {
            const fetchMapData = async () => {
                try {
                    const response = await fetch(`/zonebuilder/get_map_data/${zoneId}`);
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
    }, [zoneId]);

    // Canvas rendering
    useEffect(() => {
        if (!useLeaflet && mapData && canvasRef.current && !isInitialized.current) {
            console.log("🖌 Initializing Canvas rendering...");
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
                console.log("✅ Canvas: Map image loaded:", mapData.imageUrl);
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            };

            img.onerror = () => {
                console.error("❌ Canvas: Failed to load map image:", mapData.imageUrl);
                setError("Failed to load map image.");
            };

            const handleMouseDown = (e) => {
                if (e.button !== 0) return;
                isDrawing.current = true;
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / (mapData.bounds[1][1] - mapData.bounds[0][1]); // max_x - min_x
                const scaleY = canvas.height / (mapData.bounds[1][0] - mapData.bounds[0][0]); // max_y - min_y

                const x = mapData.bounds[0][1] + ((e.clientX - rect.left) / scaleX);
                const y = mapData.bounds[1][0] - ((e.clientY - rect.top) / scaleY);

                points.current.push({ x, y });
                console.log("🖱 Canvas click (feet):", { x, y });

                drawPolygon(points.current);
                onDrawComplete(points.current);
            };

            const drawPolygon = (feetPoints) => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                if (feetPoints.length === 0) return;

                ctx.beginPath();
                feetPoints.forEach((point, index) => {
                    const x = (point.x - mapData.bounds[0][1]) * (canvas.width / (mapData.bounds[1][1] - mapData.bounds[0][1]));
                    const y = canvas.height - ((point.y - mapData.bounds[0][0]) * (canvas.height / (mapData.bounds[1][0] - mapData.bounds[0][0])));
                    if (index === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);

                    ctx.fillStyle = "blue";
                    ctx.fillRect(x - 2, y - 2, 4, 4);
                });
                ctx.closePath();
                ctx.strokeStyle = triggerColor || "red";
                ctx.stroke();
            };

            canvas.addEventListener("mousedown", handleMouseDown);
            isInitialized.current = true;
            return () => canvas.removeEventListener("mousedown", handleMouseDown);
        }
    }, [mapData, useLeaflet, onDrawComplete, triggerColor]);

    // Leaflet rendering
    useEffect(() => {
        if (useLeaflet && mapData && mapRef.current && !mapInstance.current) {
            console.log("🗺 Initializing Leaflet with mapData:", mapData);
            mapInstance.current = L.map(mapRef.current, { crs: L.CRS.Simple }).fitBounds(mapData.bounds);
            L.imageOverlay(mapData.imageUrl, mapData.bounds).addTo(mapInstance.current);
            mapInstance.current.addLayer(drawnItems);

            const drawControl = new L.Control.Draw({
                edit: { featureGroup: drawnItems },
                draw: {
                    polygon: { shapeOptions: { color: triggerColor || "red", weight: 2 } },
                    rectangle: false,
                    circle: false,
                    polyline: false,
                    marker: false,
                },
            });
            mapInstance.current.addControl(drawControl);

            mapInstance.current.on(L.Draw.Event.CREATED, (event) => {
                const layer = event.layer;
                drawnItems.addLayer(layer);
                const coords = layer.getLatLngs()[0].map((point, index) => ({
                    n_x: point.lng,
                    n_y: point.lat,
                    n_z: 0,
                    n_ord: index + 1
                }));
                console.log("🖌 Leaflet drawn coordinates (feet):", coords);
                onDrawComplete(coords);
            });

            console.log("✅ Leaflet map initialized with bounds:", mapData.bounds);
        }

        // Cleanup
        return () => {
            if (mapInstance.current) {
                mapInstance.current.remove();
                mapInstance.current = null;
                console.log("🗺 Leaflet map cleaned up");
            }
        };
    }, [mapData, useLeaflet, onDrawComplete, triggerColor, drawnItems]);

    return (
        <div>
            {error && <div style={{ color: "red", marginBottom: "10px" }}>{error}</div>}
            {useLeaflet ? (
                <div ref={mapRef} style={{ height: "600px", width: "800px", border: "2px solid black" }} />
            ) : (
                <canvas ref={canvasRef} id="map" style={{ border: "2px solid black" }} />
            )}
        </div>
    );
});

export default MapZoneBuilder;