// /home/parcoadmin/parco_fastapi/app/src/components/MapZoneBuilder.js
import React, { useEffect, useRef, useState, memo } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import "leaflet-draw";
import "./Map.css";

const MapZoneBuilder = memo(({ zoneId, onDrawComplete, triggerColor, useLeaflet, drawnItems, parentZoneVertices }) => {
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
    const parentLayer = useRef(null); // For Leaflet mode
    const canvasBounds = useRef({ x: 0, y: 0, width: 800, height: 600 }); // Adjusted bounds

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
        } else {
            setMapData(null);
            setError(null);
        }
    }, [zoneId]);

    // Canvas rendering
    useEffect(() => {
        if (!useLeaflet && mapData && canvasRef.current && !isInitialized.current) {
            console.log("🖌 Initializing Canvas rendering with mapData:", mapData);
            const canvas = canvasRef.current;
            const ctx = canvas.getContext("2d");
            if (!ctx) {
                console.error("❌ Canvas context is null");
                return;
            }
            ctxRef.current = ctx;

            canvas.width = 800;
            canvas.height = 600;

            const img = new Image();
            img.crossOrigin = "anonymous";
            img.src = mapData.imageUrl;
            imageRef.current = img;

            img.onload = () => {
                console.log("✅ Canvas: Map image loaded:", mapData.imageUrl, "Dimensions:", img.width, "x", img.height);
                // Calculate adjusted bounds to maintain aspect ratio
                const mapWidth = mapData.bounds[1][1] - mapData.bounds[0][1]; // max_x - min_x
                const mapHeight = mapData.bounds[1][0] - mapData.bounds[0][0]; // max_y - min_y
                const mapAspect = mapWidth / mapHeight;
                const canvasAspect = canvas.width / canvas.height;

                let drawWidth = canvas.width;
                let drawHeight = canvas.height;
                let offsetX = 0;
                let offsetY = 0;

                if (mapAspect > canvasAspect) {
                    // Map is wider than canvas: fit width, adjust height
                    drawHeight = canvas.width / mapAspect;
                    offsetY = (canvas.height - drawHeight) / 2;
                } else {
                    // Map is taller than canvas: fit height, adjust width
                    drawWidth = canvas.height * mapAspect;
                    offsetX = (canvas.width - drawWidth) / 2;
                }

                canvasBounds.current = { x: offsetX, y: offsetY, width: drawWidth, height: drawHeight };
                console.log("🖌 Canvas adjusted bounds:", canvasBounds.current);

                drawCanvas();
            };

            img.onerror = () => {
                console.error("❌ Canvas: Failed to load map image:", mapData.imageUrl);
                setError("Failed to load map image.");
            };

            const handleMouseDown = (e) => {
                if (e.button !== 0) return;
                isDrawing.current = true;
                const rect = canvas.getBoundingClientRect();
                if (!rect) {
                    console.error("❌ Canvas bounding rect is null");
                    return;
                }
                const scaleX = canvasBounds.current.width / (mapData.bounds[1][1] - mapData.bounds[0][1]);
                const scaleY = canvasBounds.current.height / (mapData.bounds[1][0] - mapData.bounds[0][0]);

                const x = mapData.bounds[0][1] + ((e.clientX - rect.left - canvasBounds.current.x) / scaleX);
                const y = mapData.bounds[1][0] - ((e.clientY - rect.top - canvasBounds.current.y) / scaleY); // Invert Y-axis to match map

                points.current.push({ x, y });
                console.log("🖱 Canvas click (feet):", { x, y });

                drawCanvas();
                onDrawComplete(points.current);
            };

            const drawCanvas = () => {
                if (!ctxRef.current || !imageRef.current) {
                    console.error("❌ Canvas context or image ref is null");
                    return;
                }
                const ctx = ctxRef.current;
                const img = imageRef.current;

                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, canvasBounds.current.x, canvasBounds.current.y, canvasBounds.current.width, canvasBounds.current.height);

                // Draw parent zone vertices as a light blue shape (non-editable)
                if (parentZoneVertices && parentZoneVertices.length > 0) {
                    console.log("📌 Rendering parent zone vertices in Canvas:", parentZoneVertices);
                    ctx.beginPath();
                    let firstPoint = true;
                    let hasValidPoints = false;
                    parentZoneVertices.forEach((vertex, index) => {
                        const x = vertex.n_x !== undefined ? vertex.n_x : (vertex.x || 0);
                        const y = vertex.n_y !== undefined ? vertex.n_y : (vertex.y || 0);
                        if (isNaN(x) || isNaN(y)) {
                            console.warn(`⚠️ Invalid vertex at index ${index}: x=${x}, y=${y}`, vertex);
                            return;
                        }
                        const canvasX = canvasBounds.current.x + (x - mapData.bounds[0][1]) * (canvasBounds.current.width / (mapData.bounds[1][1] - mapData.bounds[0][1]));
                        const canvasY = canvasBounds.current.y + ((mapData.bounds[1][0] - y) * (canvasBounds.current.height / (mapData.bounds[1][0] - mapData.bounds[0][0])));
                        if (firstPoint) {
                            ctx.moveTo(canvasX, canvasY);
                            firstPoint = false;
                            hasValidPoints = true;
                        } else {
                            ctx.lineTo(canvasX, canvasY);
                        }
                    });
                    if (hasValidPoints) {
                        ctx.closePath();
                        ctx.strokeStyle = "lightblue";
                        ctx.lineWidth = 2;
                        ctx.stroke();
                        ctx.fillStyle = "rgba(173, 216, 230, 0.3)"; // Light blue fill with transparency
                        ctx.fill();
                        console.log("✅ Rendered parent zone shape in Canvas");
                    } else {
                        console.warn("⚠️ No valid points to render parent zone in Canvas");
                    }
                } else {
                    console.log("ℹ️ No parent zone vertices to render in Canvas");
                }

                // Draw current editable polygon
                if (points.current.length === 0) return;
                ctx.beginPath();
                points.current.forEach((point, index) => {
                    const x = canvasBounds.current.x + (point.x - mapData.bounds[0][1]) * (canvasBounds.current.width / (mapData.bounds[1][1] - mapData.bounds[0][1]));
                    const y = canvasBounds.current.y + ((mapData.bounds[1][0] - point.y) * (canvasBounds.current.height / (mapData.bounds[1][0] - mapData.bounds[0][0])));
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
            return () => {
                canvas.removeEventListener("mousedown", handleMouseDown);
                isInitialized.current = false;
            };
        }
    }, [mapData, useLeaflet, onDrawComplete, triggerColor, parentZoneVertices]);

    // Leaflet rendering
    useEffect(() => {
        if (useLeaflet && mapData && mapRef.current && !mapInstance.current) {
            console.log("🗺 Initializing Leaflet with mapData:", mapData);
            mapInstance.current = L.map(mapRef.current, { crs: L.CRS.Simple }).fitBounds(mapData.bounds);
            console.log("🗺 Leaflet fitBounds applied:", mapData.bounds);
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

        // Draw parent zone vertices as a non-editable light blue shape
        if (useLeaflet && mapInstance.current) {
            if (parentLayer.current) {
                mapInstance.current.removeLayer(parentLayer.current);
                parentLayer.current = null;
            }

            if (parentZoneVertices && parentZoneVertices.length > 0) {
                console.log("📌 Rendering parent zone vertices in Leaflet:", parentZoneVertices);
                const latLngs = parentZoneVertices
                    .map(vertex => {
                        const x = vertex.n_x !== undefined ? vertex.n_x : (vertex.x || 0);
                        const y = vertex.n_y !== undefined ? vertex.n_y : (vertex.y || 0);
                        if (isNaN(x) || isNaN(y)) {
                            console.warn(`⚠️ Invalid vertex in parentZoneVertices: x=${x}, y=${y}`, vertex);
                            return null;
                        }
                        return [y, x]; // [lat, lng] for Leaflet
                    })
                    .filter(coord => coord !== null);
                if (latLngs.length > 0) {
                    parentLayer.current = L.polygon(latLngs, {
                        color: "lightblue",
                        weight: 2,
                        fillColor: "lightblue",
                        fillOpacity: 0.3,
                        interactive: false,
                    }).addTo(mapInstance.current);
                    console.log("✅ Rendered parent zone shape in Leaflet:", latLngs);
                } else {
                    console.warn("⚠️ No valid latLngs to render parent zone in Leaflet");
                }
            } else {
                console.log("ℹ️ No parent zone vertices to render in Leaflet");
            }
        }

        // Cleanup
        return () => {
            if (mapInstance.current) {
                mapInstance.current.remove();
                mapInstance.current = null;
                console.log("🗺 Leaflet map cleaned up");
            }
        };
    }, [mapData, useLeaflet, onDrawComplete, triggerColor, drawnItems, parentZoneVertices]);

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