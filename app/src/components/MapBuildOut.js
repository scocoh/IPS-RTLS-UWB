/* Name: MapBuildOut.js */
/* Version: 0.1.2 */
/* Created: 971201 */
/* Modified: 250613 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: JavaScript file for ParcoRTLS frontend */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// # VERSION 250613 /home/parcoadmin/parco_fastapi/app/src/components/MapBuildOut.js 0P.10B.23
// # --- CHANGED: Fixed blank display in Leaflet mode by using correct vertex fields (x, y), filtering vertices by selectedZoneId, and validating bounds; bumped from 0P.10B.22
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

const MapBuildOut = ({ zoneId, selectedZoneId, showZoneBoundary, onDrawComplete, devices, useLeaflet, onDeviceSelect, deploymentMode, clickMarker }) => {
    const mapRef = useRef(null);
    const canvasRef = useRef(null);
    const markersRef = useRef([]);
    const clickMarkerRef = useRef(null);
    const zonePolygonRef = useRef(null);

    useEffect(() => {
        const fetchData = async () => {
            let mapData = null;
            let vertices = null;

            // Fetch map data if not showing zone boundary
            if (!showZoneBoundary) {
                try {
                    const res = await fetch(`/zonebuilder/get_map_data/${zoneId}`);
                    mapData = await res.json();
                    console.log("✅ Fetched map data:", mapData);
                } catch (err) {
                    console.error("❌ Error fetching map data:", err);
                }
            }

            // Fetch zone vertices if showing zone boundary and selectedZoneId is provided
            if (showZoneBoundary && selectedZoneId) {
                try {
                    const res = await fetch(`/zoneviewer/get_vertices_for_campus/${selectedZoneId}`);
                    vertices = await res.json();
                    console.log("✅ Fetched zone vertices:", vertices);
                } catch (err) {
                    console.error("❌ Error fetching zone vertices:", err);
                    // Fall back to map rendering if vertices fetch fails
                    showZoneBoundary = false;
                }
            }

            if (useLeaflet) {
                if (!mapRef.current) {
                    mapRef.current = L.map("map", {
                        crs: L.CRS.Simple,
                        minZoom: -5,
                        maxZoom: 5,
                    });
                }

                // Remove existing zone polygon if it exists
                if (zonePolygonRef.current) {
                    zonePolygonRef.current.remove();
                    zonePolygonRef.current = null;
                }

                if (showZoneBoundary && vertices && vertices.vertices && vertices.vertices.length >= 3) {
                    // Filter vertices for the selected zone
                    const zoneVertices = vertices.vertices.filter(v => v.zone_id === parseInt(selectedZoneId));
                    console.log(`ℹ️ Filtered vertices for zone ${selectedZoneId}:`, zoneVertices);

                    if (zoneVertices.length >= 3) {
                        // Render zone boundary as a polygon
                        const polygonPoints = zoneVertices.map(v => [v.y, v.x]); // Use x, y instead of n_x, n_y
                        console.log("ℹ️ Polygon points:", polygonPoints);

                        // Validate points
                        const validPoints = polygonPoints.every(p => !isNaN(p[0]) && !isNaN(p[1]));
                        if (validPoints) {
                            zonePolygonRef.current = L.polygon(polygonPoints, {
                                color: "blue",
                                fillColor: "blue",
                                fillOpacity: 0.2,
                                weight: 2,
                            }).addTo(mapRef.current);

                            try {
                                mapRef.current.fitBounds(L.latLngBounds(polygonPoints));
                                console.log("✅ Set map bounds to polygon points");
                            } catch (err) {
                                console.error("❌ Error setting map bounds:", err);
                                mapRef.current.setView([0, 0], 0); // Fallback to default view
                            }
                        } else {
                            console.error("❌ Invalid polygon points, skipping polygon rendering");
                            mapRef.current.setView([0, 0], 0); // Fallback to default view
                        }
                    } else {
                        console.warn(`⚠️ Insufficient vertices for zone ${selectedZoneId}:`, zoneVertices.length);
                        mapRef.current.setView([0, 0], 0); // Fallback to default view
                    }
                } else if (mapData) {
                    // Render map as usual
                    const bounds = mapData.bounds;
                    const image = L.imageOverlay(mapData.imageUrl, bounds).addTo(mapRef.current);
                    mapRef.current.fitBounds(bounds);
                    console.log("✅ Rendered map with bounds:", bounds);
                } else {
                    // Default bounds if no map or vertices
                    mapRef.current.setView([0, 0], 0);
                    console.log("ℹ️ Set default map view");
                }

                mapRef.current.on("click", (e) => {
                    const { lat, lng } = e.latlng;
                    onDrawComplete({ n_x: lng, n_y: lat });
                });

                // Remove existing click marker if it exists
                if (clickMarkerRef.current) {
                    clickMarkerRef.current.remove();
                    clickMarkerRef.current = null;
                }

                // Add click marker if it exists
                if (clickMarker && clickMarker.x != null && clickMarker.y != null) {
                    clickMarkerRef.current = L.marker([clickMarker.y, clickMarker.x], {
                        icon: L.divIcon({ className: "click-marker", html: "✖" })
                    }).addTo(mapRef.current);
                    console.log("✅ Added click marker at:", [clickMarker.y, clickMarker.x]);
                }

                // Update device markers
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
                                console.log("ℹ️ Device marker clicked:", device.x_id_dev);
                                onDeviceSelect(device);
                            });
                        }

                        console.log(`✅ Drew device ${device.x_id_dev} at:`, [device.n_moe_y, device.n_moe_x]);
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
                const container = document.getElementById("map");
                const maxWidth = container.clientWidth;
                const maxHeight = 400;

                let canvasWidth, canvasHeight, scaleX, scaleY, bounds;

                if (showZoneBoundary && vertices && vertices.vertices && vertices.vertices.length >= 3) {
                    // Filter vertices for the selected zone
                    const zoneVertices = vertices.vertices.filter(v => v.zone_id === parseInt(selectedZoneId));
                    console.log(`ℹ️ Filtered vertices for zone ${selectedZoneId}:`, zoneVertices);

                    if (zoneVertices.length >= 3) {
                        // Calculate bounds from vertices
                        const xValues = zoneVertices.map(v => v.x); // Use x instead of n_x
                        const yValues = zoneVertices.map(v => v.y); // Use y instead of n_y
                        const minX = Math.min(...xValues);
                        const maxX = Math.max(...xValues);
                        const minY = Math.min(...yValues);
                        const maxY = Math.max(...yValues);
                        bounds = [[maxY, minX], [minY, maxX]]; // [top-left, bottom-right]
                        console.log("ℹ️ Calculated bounds from vertices:", bounds);

                        const width = maxX - minX;
                        const height = maxY - minY;
                        const aspectRatio = width / height;

                        canvasWidth = width;
                        canvasHeight = height;

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

                        scaleX = canvasWidth / width;
                        scaleY = canvasHeight / height;

                        // Draw zone boundary polygon
                        ctx.beginPath();
                        zoneVertices.forEach((v, i) => {
                            const x = (v.x - minX) * scaleX;
                            const y = (maxY - v.y) * scaleY;
                            if (i === 0) {
                                ctx.moveTo(x, y);
                            } else {
                                ctx.lineTo(x, y);
                            }
                            console.log(`ℹ️ Drawing vertex ${i}:`, [x, y]);
                        });
                        ctx.closePath();
                        ctx.fillStyle = "rgba(0, 0, 255, 0.2)";
                        ctx.fill();
                        ctx.strokeStyle = "blue";
                        ctx.lineWidth = 2;
                        ctx.stroke();
                        console.log("✅ Drew zone polygon");
                    } else {
                        console.warn(`⚠️ Insufficient vertices for zone ${selectedZoneId}:`, zoneVertices.length);
                        bounds = [[0, 0], [100, 100]]; // Default bounds
                        canvasWidth = maxWidth;
                        canvasHeight = maxHeight;
                        canvasRef.current.width = canvasWidth;
                        canvasRef.current.height = canvasHeight;
                        scaleX = canvasWidth / 100;
                        scaleY = canvasHeight / 100;
                    }
                } else if (mapData) {
                    // Render map as usual
                    const img = new Image();
                    img.src = mapData.imageUrl;
                    img.onload = () => {
                        const aspectRatio = img.width / img.height;

                        canvasWidth = img.width;
                        canvasHeight = img.height;

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

                        bounds = mapData.bounds;
                        const width = bounds[1][1] - bounds[0][1];
                        const height = bounds[1][0] - bounds[0][0];
                        scaleX = canvasWidth / width;
                        scaleY = canvasHeight / height;

                        // Draw devices
                        devices.forEach(device => {
                            if (device.n_moe_x != null && device.n_moe_y != null) {
                                const x = (device.n_moe_x - bounds[0][1]) * scaleX;
                                const y = (bounds[1][0] - device.n_moe_y) * scaleY;
                                console.log(`ℹ️ Drawing device ${device.x_id_dev} at (${x}, ${y})`);
                                ctx.beginPath();
                                ctx.arc(x, y, 5, 0, 2 * Math.PI);
                                ctx.fillStyle = "red";
                                ctx.fill();
                            }
                        });

                        // Draw click marker if it exists
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
                            console.log("✅ Drew click marker at:", [x, y]);
                        }

                        canvasRef.current.onclick = (e) => {
                            const rect = canvasRef.current.getBoundingClientRect();
                            const x = (e.clientX - rect.left) / scaleX + bounds[0][1];
                            const y = bounds[1][0] - (e.clientY - rect.top) / scaleY;
                            onDrawComplete({ n_x: x, n_y: y });
                            console.log("ℹ️ Canvas click at:", { n_x: x, n_y: y });
                        };
                    };
                    return; // Exit early to avoid duplicate rendering
                } else {
                    // Default canvas size if no map or vertices
                    canvasWidth = maxWidth;
                    canvasHeight = maxHeight;
                    canvasRef.current.width = canvasWidth;
                    canvasRef.current.height = canvasHeight;
                    bounds = [[0, 0], [100, 100]]; // Default bounds
                    scaleX = canvasWidth / 100;
                    scaleY = canvasHeight / 100;
                    console.log("ℹ️ Set default canvas bounds");
                }

                // Draw devices for zone boundary or default canvas
                devices.forEach(device => {
                    if (device.n_moe_x != null && device.n_moe_y != null) {
                        const x = (device.n_moe_x - bounds[0][1]) * scaleX;
                        const y = (bounds[1][0] - device.n_moe_y) * scaleY;
                        console.log(`ℹ️ Drawing device ${device.x_id_dev} at (${x}, ${y})`);
                        ctx.beginPath();
                        ctx.arc(x, y, 5, 0, 2 * Math.PI);
                        ctx.fillStyle = "red";
                        ctx.fill();
                    }
                });

                // Draw click marker if it exists
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
                    console.log("✅ Drew click marker at:", [x, y]);
                }

                canvasRef.current.onclick = (e) => {
                    const rect = canvasRef.current.getBoundingClientRect();
                    const x = (e.clientX - rect.left) / scaleX + bounds[0][1];
                    const y = bounds[1][0] - (e.clientY - rect.top) / scaleY;
                    onDrawComplete({ n_x: x, n_y: y });
                    console.log("ℹ️ Canvas click at:", { n_x: x, n_y: y });
                };
            }
        };

        fetchData();

        return () => {
            if (mapRef.current) {
                mapRef.current.remove();
                mapRef.current = null;
            }
            if (canvasRef.current) {
                canvasRef.current.remove();
                canvasRef.current = null;
            }
            if (zonePolygonRef.current) {
                zonePolygonRef.current = null;
            }
        };
    }, [zoneId, selectedZoneId, showZoneBoundary, useLeaflet, devices, onDrawComplete, onDeviceSelect, deploymentMode, clickMarker]);

    return <div id="map" style={{ height: "400px", width: "100%", overflow: "hidden" }} />;
};

export default MapBuildOut;