// # VERSION 250316 /home/parcoadmin/parco_fastapi/app/src/components/MapBuildOut.js 0P.10B.01
// #  
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const MapBuildOut = ({ zoneId, onDrawComplete, devices, useLeaflet }) => {
    const mapRef = useRef(null);
    const mapInstance = useRef(null);
    const canvasRef = useRef(null);
    const [mapData, setMapData] = useState(null);
    const [error, setError] = useState(null);
    const [clickDots, setClickDots] = useState([]); // Track click dots for both modes
    const ctxRef = useRef(null);
    const imageRef = useRef(null);
    const canvasBounds = useRef({ x: 0, y: 0, width: 600, height: 400 });
    const markerLayer = useRef(null); // Layer group for Leaflet markers

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
                    setClickDots([]);
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
        if (!useLeaflet && mapData && canvasRef.current) {
            console.log("🖌 Initializing Canvas rendering with mapData:", mapData);
            console.log("Devices:", devices);
            const canvas = canvasRef.current;
            const ctx = canvas.getContext("2d");
            if (!ctx) return;
            ctxRef.current = ctx;

            canvas.width = 600;
            canvas.height = 400;

            const img = new Image();
            img.crossOrigin = "anonymous";
            img.src = mapData.imageUrl;
            imageRef.current = img;

            const mapWidth = mapData.bounds[1][1] - mapData.bounds[0][1];
            const mapHeight = mapData.bounds[1][0] - mapData.bounds[0][0];

            const drawCanvas = () => {
                if (!ctxRef.current || !imageRef.current) return;
                const context = ctxRef.current;
                context.clearRect(0, 0, canvas.width, canvas.height);
                context.drawImage(imageRef.current, canvasBounds.current.x, canvasBounds.current.y, canvasBounds.current.width, canvasBounds.current.height);

                if (devices && Array.isArray(devices)) {
                    devices.forEach(d => {
                        if (d.n_moe_x != null && d.n_moe_y != null) {
                            const xPixel = canvasBounds.current.x + (d.n_moe_x - mapData.bounds[0][1]) * (canvasBounds.current.width / mapWidth);
                            const yPixel = canvasBounds.current.y + (mapData.bounds[1][0] - d.n_moe_y) * (canvasBounds.current.height / mapHeight);
                            console.log(`Drawing device ${d.x_id_dev} at (${xPixel}, ${yPixel})`);
                            context.fillStyle = "red";
                            context.beginPath();
                            context.arc(xPixel, yPixel, 5, 0, 2 * Math.PI);
                            context.fill();
                            context.fillStyle = "black";
                            context.fillText(`${d.x_id_dev}: ${d.x_nm_dev}`, xPixel + 10, yPixel);
                        }
                    });
                }

                clickDots.forEach(dot => {
                    const xPixel = canvasBounds.current.x + (dot.n_x - mapData.bounds[0][1]) * (canvasBounds.current.width / mapWidth);
                    const yPixel = canvasBounds.current.y + (mapData.bounds[1][0] - dot.n_y) * (canvasBounds.current.height / mapHeight);
                    context.fillStyle = "red";
                    context.beginPath();
                    context.arc(xPixel, yPixel, 5, 0, 2 * Math.PI);
                    context.fill();
                });
            };

            img.onload = () => {
                const mapAspect = mapWidth / mapHeight;
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

            canvas.onclick = (e) => {
                const rect = canvas.getBoundingClientRect();
                const xPixel = e.clientX - rect.left;
                const yPixel = e.clientY - rect.top;
                const xFeet = mapData.bounds[0][1] + (xPixel - canvasBounds.current.x) * (mapWidth / canvasBounds.current.width);
                const yFeet = mapData.bounds[1][0] - (yPixel - canvasBounds.current.y) * (mapHeight / canvasBounds.current.height);
                console.log(`Canvas click at (${xFeet}, ${yFeet})`);
                setClickDots(prev => [...prev, { n_x: xFeet, n_y: yFeet }]);
                onDrawComplete({ n_x: xFeet, n_y: yFeet });
                drawCanvas();
            };

            drawCanvas();
            return () => {
                // Cleanup not needed here
            };
        }
    }, [mapData, useLeaflet, devices, onDrawComplete]);

    // Leaflet rendering
    useEffect(() => {
        if (useLeaflet && mapData && mapRef.current && !mapInstance.current) {
            console.log("🗺 Initializing Leaflet with mapData:", mapData);
            console.log("Devices:", devices);
            mapInstance.current = L.map(mapRef.current, { 
                crs: L.CRS.Simple, 
                dragging: true 
            }).fitBounds(mapData.bounds);
            L.imageOverlay(mapData.imageUrl, mapData.bounds).addTo(mapInstance.current);
            console.log("Leaflet bounds:", mapInstance.current.getBounds());

            // Layer group for markers
            markerLayer.current = L.layerGroup().addTo(mapInstance.current);

            // Custom marker icon
            const customIcon = L.divIcon({
                html: '<div style="background-color: red; width: 20px; height: 20px; border-radius: 50%; border: 2px solid black;"></div>',
                className: "",
                iconSize: [24, 24],
                iconAnchor: [12, 12],
                popupAnchor: [0, -12]
            });

            mapInstance.current.on("click", (e) => {
                const { lat, lng } = e.latlng;
                console.log(`Leaflet click at (${lng}, ${lat})`);
                setClickDots(prev => [...prev, { n_x: lng, n_y: lat }]);
                onDrawComplete({ n_x: lng, n_y: lat });
                L.marker([lat, lng], { icon: customIcon })
                    .addTo(markerLayer.current)
                    .bindPopup("Clicked Marker")
                    .openPopup();
            });

            // Draw devices
            if (devices && Array.isArray(devices)) {
                devices.forEach(d => {
                    if (d.n_moe_x != null && d.n_moe_y != null) {
                        console.log(`Adding marker for ${d.x_id_dev} at (${d.n_moe_y}, ${d.n_moe_x})`);
                        L.marker([d.n_moe_y, d.n_moe_x], { icon: customIcon })
                            .addTo(markerLayer.current)
                            .bindPopup(`${d.x_id_dev}: ${d.x_nm_dev}`)
                            .openPopup();
                    }
                });
            }

            // Draw initial click dots
            clickDots.forEach(dot => {
                L.marker([dot.n_y, dot.n_x], { icon: customIcon })
                    .addTo(markerLayer.current)
                    .bindPopup("Clicked Marker")
                    .openPopup();
            });
        }
    }, [mapData, useLeaflet, devices, onDrawComplete]);

    // Redraw Leaflet markers when clickDots change
    useEffect(() => {
        if (useLeaflet && mapInstance.current && markerLayer.current) {
            markerLayer.current.clearLayers();

            const customIcon = L.divIcon({
                html: '<div style="background-color: red; width: 20px; height: 20px; border-radius: 50%; border: 2px solid black;"></div>',
                className: "",
                iconSize: [24, 24],
                iconAnchor: [12, 12],
                popupAnchor: [0, -12]
            });

            if (devices && Array.isArray(devices)) {
                devices.forEach(d => {
                    if (d.n_moe_x != null && d.n_moe_y != null) {
                        console.log(`Adding marker for ${d.x_id_dev} at (${d.n_moe_y}, ${d.n_moe_x})`);
                        L.marker([d.n_moe_y, d.n_moe_x], { icon: customIcon })
                            .addTo(markerLayer.current)
                            .bindPopup(`${d.x_id_dev}: ${d.x_nm_dev}`)
                            .openPopup();
                    }
                });
            }

            clickDots.forEach(dot => {
                console.log(`Adding click marker at (${dot.n_x}, ${dot.n_y})`);
                L.marker([dot.n_y, dot.n_x], { icon: customIcon })
                    .addTo(markerLayer.current)
                    .bindPopup("Clicked Marker")
                    .openPopup();
            });
        }
    }, [clickDots, devices, useLeaflet]);

    return (
        <div>
            {error && <div style={{ color: "red" }}>{error}</div>}
            {useLeaflet ? (
                <div ref={mapRef} style={{ height: "400px", width: "600px", border: "2px solid black", cursor: "pointer" }} />
            ) : (
                <canvas ref={canvasRef} style={{ border: "2px solid black", cursor: "pointer" }} width="600" height="400" />
            )}
        </div>
    );
};

export default MapBuildOut;