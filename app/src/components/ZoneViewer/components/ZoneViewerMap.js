/* Name: ZoneViewerMap.js */
/* Version: 0.1.1 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Map component for ZoneViewer with advanced styling controls */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ZoneViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useEffect, useRef, useState, memo } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import "leaflet-draw";
import { config } from "../../../config.js";

const ZoneViewerMap = memo(({ 
  mapId, 
  zones, 
  checkedZones, 
  vertices, 
  onVerticesUpdate, 
  useLeaflet, 
  zoneStyle = {
    fillOpacity: 30,
    lineOpacity: 70,
    lineColor: '#ff0000',
    vertexColor: '#ff0000'
  }
}) => {
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

    // Calculate opacity values for rendering (0.0 to 1.0)
    const fillOpacity = zoneStyle.fillOpacity / 100;
    const lineOpacity = zoneStyle.lineOpacity / 100;

    console.log(`🎨 Zone styling: Fill ${zoneStyle.fillOpacity}%, Line ${zoneStyle.lineOpacity}%, Colors: ${zoneStyle.lineColor}/${zoneStyle.vertexColor}`);

    // Fetch map data
    useEffect(() => {
        if (mapId) {
            const fetchMapData = async () => {
                try {
                    const response = await fetch(`${config.API_BASE_URL}/zoneviewer/get_map_data/${mapId}`);
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

    // Canvas rendering with advanced styling
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

                checkedZones.forEach(zoneId => {
                    const filteredVertices = vertices.filter(v => v.zone_id === zoneId);
                    if (filteredVertices.length > 0) {
                        // Draw filled polygon with separate fill opacity
                        ctx.globalAlpha = fillOpacity;
                        ctx.beginPath();
                        filteredVertices.forEach((vertex, index) => {
                            const x = Number(canvasBounds.current.x + (vertex.x - mapData.bounds[0][1]) * (canvasBounds.current.width / mapWidth));
                            const y = Number(canvasBounds.current.y + (mapData.bounds[1][0] - vertex.y) * (canvasBounds.current.height / mapHeight));
                            if (index === 0) ctx.moveTo(x, y);
                            else ctx.lineTo(x, y);
                        });
                        ctx.closePath();
                        ctx.fillStyle = zoneStyle.lineColor;
                        ctx.fill();

                        // Draw border with separate line opacity
                        ctx.globalAlpha = lineOpacity;
                        ctx.beginPath();
                        filteredVertices.forEach((vertex, index) => {
                            const x = Number(canvasBounds.current.x + (vertex.x - mapData.bounds[0][1]) * (canvasBounds.current.width / mapWidth));
                            const y = Number(canvasBounds.current.y + (mapData.bounds[1][0] - vertex.y) * (canvasBounds.current.height / mapHeight));
                            if (index === 0) ctx.moveTo(x, y);
                            else ctx.lineTo(x, y);
                        });
                        ctx.closePath();
                        ctx.strokeStyle = zoneStyle.lineColor;
                        ctx.lineWidth = 2;
                        ctx.stroke();

                        // Draw vertices with line opacity and vertex color
                        ctx.globalAlpha = lineOpacity;
                        filteredVertices.forEach((vertex) => {
                            const x = Number(canvasBounds.current.x + (vertex.x - mapData.bounds[0][1]) * (canvasBounds.current.width / mapWidth));
                            const y = Number(canvasBounds.current.y + (mapData.bounds[1][0] - vertex.y) * (canvasBounds.current.height / mapHeight));
                            
                            ctx.beginPath();
                            ctx.arc(x, y, 5, 0, 2 * Math.PI);
                            ctx.fillStyle = zoneStyle.vertexColor;
                            ctx.fill();
                            
                            // Vertex labels with high contrast
                            ctx.globalAlpha = 1.0; // Full opacity for text readability
                            ctx.font = "12px Arial";
                            ctx.fillStyle = "black";
                            ctx.strokeStyle = "white";
                            ctx.lineWidth = 3;
                            ctx.strokeText(vertex.vertex_id, x + 5, y - 5);
                            ctx.fillText(vertex.vertex_id, x + 5, y - 5);
                            ctx.globalAlpha = lineOpacity; // Reset for next vertex
                        });
                    } else {
                        console.log(`ℹ️ No vertices to render for zone ${zoneId}`);
                    }
                });

                // Reset global alpha
                ctx.globalAlpha = 1.0;
            };

            isInitialized.current = true;
            return () => {
                isInitialized.current = false;
            };
        }
    }, [mapData, useLeaflet, checkedZones, vertices, fillOpacity, lineOpacity, zoneStyle]);

    // Leaflet rendering with advanced styling
    useEffect(() => {
        if (useLeaflet && mapData && mapRef.current && !mapInstance.current) {
            console.log("🗺 Initializing Leaflet with mapData:", mapData);
            mapInstance.current = L.map(mapRef.current, { crs: L.CRS.Simple }).fitBounds(mapData.bounds);
            L.imageOverlay(mapData.imageUrl, mapData.bounds).addTo(mapInstance.current);
            mapInstance.current.addLayer(drawnItems.current);
        }

        if (mapInstance.current) {
            drawnItems.current.clearLayers();

            checkedZones.forEach(zoneId => {
                const filteredVertices = vertices.filter(v => v.zone_id === zoneId);
                if (filteredVertices.length > 0) {
                    const latLngs = filteredVertices.map(v => [Number(v.y), Number(v.x)]);
                    
                    // Advanced polygon styling with separate fill and line properties
                    L.polygon(latLngs, { 
                        color: zoneStyle.lineColor,           // Border color
                        weight: 2,                            // Border width
                        opacity: lineOpacity,                 // Border transparency
                        fillColor: zoneStyle.lineColor,      // Fill color (same as border)
                        fillOpacity: fillOpacity              // Fill transparency (separate from border)
                    }).addTo(drawnItems.current);

                    // Enhanced vertices with custom colors and transparency
                    filteredVertices.forEach(v => {
                        // Vertex marker
                        L.circleMarker([Number(v.y), Number(v.x)], {
                            radius: 5,
                            color: zoneStyle.vertexColor,        // Vertex border color
                            fillColor: zoneStyle.vertexColor,    // Vertex fill color
                            fillOpacity: lineOpacity,             // Vertex transparency
                            opacity: lineOpacity,                 // Vertex border transparency
                            weight: 2
                        }).addTo(drawnItems.current);
                        
                        // Enhanced vertex label with better visibility
                        L.marker([Number(v.y), Number(v.x)], {
                            icon: L.divIcon({
                                className: "vertex-label-enhanced",
                                html: `<span style="
                                    color: black; 
                                    font-weight: bold; 
                                    font-size: 12px;
                                    text-shadow: 
                                        -1px -1px 0 white,  
                                        1px -1px 0 white,
                                        -1px 1px 0 white,
                                        1px 1px 0 white,
                                        0 0 3px white;
                                    background: rgba(255, 255, 255, 0.8);
                                    padding: 1px 3px;
                                    border-radius: 3px;
                                    border: 1px solid rgba(0,0,0,0.2);
                                ">${v.vertex_id}</span>`,
                                iconSize: [25, 20],
                                iconAnchor: [0, 20]
                            })
                        }).addTo(drawnItems.current);
                    });
                } else {
                    console.log(`ℹ️ No vertices to render for zone ${zoneId}`);
                }
            });
        }

        return () => {
            if (mapInstance.current && !useLeaflet) {
                mapInstance.current.remove();
                mapInstance.current = null;
            }
        };
    }, [mapData, useLeaflet, checkedZones, vertices, fillOpacity, lineOpacity, zoneStyle]);

    // Cleanup on component unmount
    useEffect(() => {
        return () => {
            if (mapInstance.current) {
                mapInstance.current.remove();
                mapInstance.current = null;
            }
        };
    }, []);

    return (
        <div>
            {error && <div style={{ color: "red", marginBottom: "10px" }}>{error}</div>}
            {useLeaflet ? (
                <div ref={mapRef} style={{ height: "600px", width: "800px", border: "2px solid black" }} />
            ) : (
                <canvas ref={canvasRef} style={{ border: "2px solid black" }} />
            )}
        </div>
    );
});

export default ZoneViewerMap;