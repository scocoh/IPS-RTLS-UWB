// # VERSION 250320 /home/parcoadmin/parco_fastapi/app/src/components/MapBuildOut.js 0P.10B.21
// # --- CHANGED: Bumped version from 0P.10B.20 to 0P.10B.21 to fix marker visibility in Estimating Mode for Canvas and Leaflet
// # 
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const MapBuildOut = ({ zoneId, onDrawComplete, devices, useLeaflet, onDeviceSelect, deploymentMode, clickMarker }) => { // --- CHANGED: Added clickMarker prop
    const mapRef = useRef(null);
    const canvasRef = useRef(null);
    const markersRef = useRef([]);
    const clickMarkerRef = useRef(null); // --- CHANGED: Added to store the click marker in Leaflet mode

    useEffect(() => {
        const fetchMapData = async () => {
            try {
                const res = await fetch(`/zonebuilder/get_map_data/${zoneId}`);
                const mapData = await res.json();
                console.log("✅ Fetched map data:", mapData);

                if (useLeaflet) {
                    if (!mapRef.current) {
                        mapRef.current = L.map("map", {
                            crs: L.CRS.Simple,
                            minZoom: -5,
                            maxZoom: 5,
                        });
                    }

                    const bounds = mapData.bounds;
                    const image = L.imageOverlay(mapData.imageUrl, bounds).addTo(mapRef.current);
                    mapRef.current.fitBounds(bounds);

                    mapRef.current.on("click", (e) => {
                        const { lat, lng } = e.latlng;
                        onDrawComplete({ n_x: lng, n_y: lat });
                    });

                    // --- CHANGED: Remove existing click marker if it exists
                    if (clickMarkerRef.current) {
                        clickMarkerRef.current.remove();
                        clickMarkerRef.current = null;
                    }

                    // --- CHANGED: Add click marker if it exists
                    if (clickMarker && clickMarker.x != null && clickMarker.y != null) {
                        clickMarkerRef.current = L.marker([clickMarker.y, clickMarker.x], {
                            icon: L.divIcon({ className: "click-marker", html: "✖" })
                        }).addTo(mapRef.current);
                    }

                    markersRef.current.forEach(marker => marker.remove());
                    markersRef.current = devices.map(device => {
                        if (device.n_moe_x != null && device.n_moe_y != null) {
                            const marker = L.marker([device.n_moe_y, device.n_moe_x], {
                                icon: L.divIcon({
                                    className: "device-marker",
                                    html: `<div style="background-color: red; width: 10px; height: 10px; border-radius: 50%;"></div>`,
                                }),
                            }).addTo(mapRef.current);

                            if (deploymentMode) {
                                marker.on("click", () => {
                                    console.log("Device marker clicked:", device.x_id_dev);
                                    onDeviceSelect(device);
                                });
                            }

                            return marker;
                        }
                        return null;
                    }).filter(marker => marker !== null);

                } else {
                    if (!canvasRef.current) {
                        canvasRef.current = document.createElement("canvas");
                        canvasRef.current.id = "mapCanvas";
                        document.getElementById("map").appendChild(canvasRef.current);
                    }

                    const ctx = canvasRef.current.getContext("2d");
                    const img = new Image();
                    img.src = mapData.imageUrl;
                    img.onload = () => {
                        const container = document.getElementById("map");
                        const maxWidth = container.clientWidth;
                        const maxHeight = 400;
                        const aspectRatio = img.width / img.height;

                        let canvasWidth = img.width;
                        let canvasHeight = img.height;

                        if (canvasWidth > maxWidth) {
                            canvasWidth = maxWidth;
                            canvasHeight = canvasWidth / aspectRatio;
                        }
                        if (canvasHeight > maxHeight) {
                            canvasHeight = maxHeight;
                            canvasWidth = canvasHeight * aspectRatio;
                        }

                        canvasRef.current.width = canvasWidth;
                        canvasRef.current.height = canvasHeight;
                        ctx.drawImage(img, 0, 0, canvasWidth, canvasHeight);

                        const bounds = mapData.bounds;
                        const width = bounds[1][1] - bounds[0][1];
                        const height = bounds[1][0] - bounds[0][0];
                        const scaleX = canvasWidth / width;
                        const scaleY = canvasHeight / height;

                        devices.forEach(device => {
                            if (device.n_moe_x != null && device.n_moe_y != null) {
                                const x = (device.n_moe_x - bounds[0][1]) * scaleX;
                                const y = (bounds[1][0] - device.n_moe_y) * scaleY;
                                console.log(`Drawing device ${device.x_id_dev} at (${x}, ${y})`);
                                ctx.beginPath();
                                ctx.arc(x, y, 5, 0, 2 * Math.PI);
                                ctx.fillStyle = "red";
                                ctx.fill();
                            }
                        });

                        // --- CHANGED: Draw the click marker if it exists
                        if (clickMarker && clickMarker.x != null && clickMarker.y != null) {
                            const x = (clickMarker.x - bounds[0][1]) * scaleX;
                            const y = (bounds[1][0] - clickMarker.y) * scaleY;
                            ctx.beginPath();
                            ctx.moveTo(x - 5, y - 5);
                            ctx.lineTo(x + 5, y + 5);
                            ctx.moveTo(x + 5, y - 5);
                            ctx.lineTo(x - 5, y + 5);
                            ctx.strokeStyle = "black";
                            ctx.stroke();
                        }

                        canvasRef.current.onclick = (e) => {
                            const rect = canvasRef.current.getBoundingClientRect();
                            const x = (e.clientX - rect.left) / scaleX + bounds[0][1];
                            const y = bounds[1][0] - (e.clientY - rect.top) / scaleY;
                            onDrawComplete({ n_x: x, n_y: y });
                        };
                    };
                }
            } catch (err) {
                console.error("Error fetching map data:", err);
            }
        };

        fetchMapData();

        return () => {
            if (mapRef.current) {
                mapRef.current.remove();
                mapRef.current = null;
            }
            if (canvasRef.current) {
                canvasRef.current.remove();
                canvasRef.current = null;
            }
        };
    }, [zoneId, useLeaflet, devices, onDrawComplete, onDeviceSelect, deploymentMode, clickMarker]); // --- CHANGED: Added clickMarker to dependencies

    return <div id="map" style={{ height: "400px", width: "100%", overflow: "hidden" }} />;
};

export default MapBuildOut;