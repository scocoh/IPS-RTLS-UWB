// # VERSION 250316 /home/parcoadmin/parco_fastapi/app/src/components/MapZoneViewer.js 0P.10B.02
// # --- CHANGED: Bumped version from 0P.10B.01 to 0P.10B.02 for coordinate precision fix
// # 
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import React, { useEffect, useRef, useState, memo } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import "leaflet-draw";
import "./Map.css";

const MapZoneViewer = memo(({ mapId, zones, checkedZones, vertices, onVerticesUpdate, useLeaflet }) => {
    const mapRef = useRef(null);
    const mapInstance = useRef(null);
    const canvasRef = useRef(null);
    const [mapData, setMapData] = useState(null);
    const [error, setError] = useState(null);
    const isInitialized = useRef(false);
    const ctxRef = useRef(null);
    const imageRef = useRef(null);
    const drawnItems = useRef(new L.FeatureGroup());
    const canvasBounds = useRef({ x: 0, y: 0, width: 800, height: 600 });

    // Fetch map data
    useEffect(() => {
        if (mapId) {
            const fetchMapData = async () => {
                try {
                    const response = await fetch(`/zoneviewer/get_map_data/${mapId}`);
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

    // Canvas rendering
    useEffect(() => {
        if (!useLeaflet && mapData && canvasRef.current && !isInitialized.current) {
            console.log("🖌 Initializing Canvas rendering with mapData:", mapData);
            const canvas = canvasRef.current;
            const ctx = canvas.getContext("2d");
            if (!ctx) return;
            ctxRef.current = ctx;

            canvas.width = 800;
            canvas.height = 600;

            const img = new Image();
            img.crossOrigin = "anonymous";
            img.src = mapData.imageUrl;
            imageRef.current = img;

            img.onload = () => {
                const mapAspect = (mapData.bounds[1][1] - mapData.bounds[0][1]) / (mapData.bounds[1][0] - mapData.bounds[0][0]);
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
                drawCanvas();
            };

            img.onerror = () => {
                setError("Failed to load map image.");
            };

            const drawCanvas = () => {
                if (!ctxRef.current || !imageRef.current) return;
                const ctx = ctxRef.current;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(imageRef.current, canvasBounds.current.x, canvasBounds.current.y, canvasBounds.current.width, canvasBounds.current.height);

                const mapWidth = mapData.bounds[1][1] - mapData.bounds[0][1];
                const mapHeight = mapData.bounds[1][0] - mapData.bounds[0][0];
                const seniorZone = checkedZones.length > 1 ? Math.min(...checkedZones) : checkedZones[0];

                checkedZones.forEach(zoneId => {
                    const zoneVertices = vertices.filter(v => v.zone_id === zoneId);
                    if (zoneVertices.length > 0) {
                        ctx.beginPath();
                        zoneVertices.forEach((vertex, index) => {
                            // --- CHANGED: Round x and y coordinates to 6 decimal places for canvas rendering
                            const x = Number(canvasBounds.current.x + (vertex.x - mapData.bounds[0][1]) * (canvasBounds.current.width / mapWidth)).toFixed(6);
                            const y = Number(canvasBounds.current.y + (mapData.bounds[1][0] - vertex.y) * (canvasBounds.current.height / mapHeight)).toFixed(6);
                            if (index === 0) ctx.moveTo(x, y);
                            else ctx.lineTo(x, y);
                            ctx.fillStyle = "red";
                            ctx.fillRect(x - 2, y - 2, 4, 4);

                            if (zoneId === seniorZone) {
                                ctx.font = "12px Arial";
                                ctx.fillStyle = "black";
                                ctx.fillText(vertex.vertex_id, x + 5, y - 5); // Offset for readability
                            }
                        });
                        ctx.closePath();
                        ctx.strokeStyle = "red";
                        ctx.stroke();
                    }
                });
            };

            isInitialized.current = true;
            return () => {
                isInitialized.current = false;
            };
        }
    }, [mapData, useLeaflet, checkedZones, vertices]);

    // Leaflet rendering
    useEffect(() => {
        if (useLeaflet && mapData && mapRef.current && !mapInstance.current) {
            console.log("🗺 Initializing Leaflet with mapData:", mapData);
            mapInstance.current = L.map(mapRef.current, { crs: L.CRS.Simple }).fitBounds(mapData.bounds);
            L.imageOverlay(mapData.imageUrl, mapData.bounds).addTo(mapInstance.current);
            mapInstance.current.addLayer(drawnItems.current);
        }

        if (mapInstance.current) {
            drawnItems.current.clearLayers();
            const seniorZone = checkedZones.length > 1 ? Math.min(...checkedZones) : checkedZones[0];

            checkedZones.forEach(zoneId => {
                const zoneVertices = vertices.filter(v => v.zone_id === zoneId);
                if (zoneVertices.length > 0) {
                    // --- CHANGED: Round x and y coordinates to 6 decimal places for Leaflet rendering
                    const latLngs = zoneVertices.map(v => [Number(v.y).toFixed(6), Number(v.x).toFixed(6)]);
                    L.polygon(latLngs, { color: "red", weight: 2 }).addTo(drawnItems.current);

                    if (zoneId === seniorZone) {
                        zoneVertices.forEach(v => {
                            L.marker([Number(v.y).toFixed(6), Number(v.x).toFixed(6)], {
                                icon: L.divIcon({
                                    className: "vertex-label",
                                    html: `<span>${v.vertex_id}</span>`,
                                    iconSize: [20, 20],
                                })
                            }).addTo(drawnItems.current);
                        });
                    }
                }
            });
        }

        return () => {
            if (mapInstance.current) {
                mapInstance.current.remove();
                mapInstance.current = null;
            }
        };
    }, [mapData, useLeaflet, checkedZones, vertices]);

    return (
        <div>
            {error && <div style={{ color: "red" }}>{error}</div>}
            {useLeaflet ? (
                <div ref={mapRef} style={{ height: "600px", width: "800px", border: "2px solid black" }} />
            ) : (
                <canvas ref={canvasRef} style={{ border: "2px solid black" }} />
            )}
            {/* --- NOTE: The "Edit Vertices" table shown in the screenshot is not part of this component. 
               If this table is in a parent component or another file, ensure that the x, y, and z coordinates 
               are rounded to 6 decimal places using Number(value).toFixed(6) when displaying and saving. 
               Also, add step="0.000001" to the input fields to enforce 6-decimal precision. */}
        </div>
    );
});

export default MapZoneViewer;