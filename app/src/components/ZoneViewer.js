// # VERSION 250316 /home/parcoadmin/parco_fastapi/app/src/components/ZoneViewer.js 0P.10B.02
// # --- CHANGED: Bumped version from 0P.10B.01 to 0P.10B.02 to add coordinate rounding and "Check All" feature for zones
// # 
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import React, { useState, useEffect } from "react";
import MapZoneViewer from "./MapZoneViewer";

const ZoneViewer = () => {
    const [campuses, setCampuses] = useState([]);
    const [selectedCampus, setSelectedCampus] = useState(null);
    const [zones, setZones] = useState([]);
    const [checkedZones, setCheckedZones] = useState([]);
    const [vertices, setVertices] = useState([]);
    const [useLeaflet, setUseLeaflet] = useState(false);
    const [editedVertices, setEditedVertices] = useState({});
    const [deletedVertices, setDeletedVertices] = useState([]);
    const [fetchError, setFetchError] = useState(null);
    const API_BASE_URL = "http://192.168.210.231:8000";

    useEffect(() => {
        const fetchCampuses = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/zoneviewer/get_campus_zones`);
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                const data = await response.json();
                setCampuses(data.campuses || []);
                setFetchError(null);
            } catch (error) {
                console.error("❌ Error fetching campuses:", error);
                setFetchError(error.message);
            }
        };
        fetchCampuses();
    }, []);

    useEffect(() => {
        if (selectedCampus) {
            const fetchZonesAndVertices = async () => {
                try {
                    const zonesResponse = await fetch(`${API_BASE_URL}/zoneviewer/get_all_zones_for_campus/${selectedCampus}`);
                    if (!zonesResponse.ok) throw new Error(`Zones fetch failed: ${zonesResponse.status}`);
                    const zonesData = await zonesResponse.json();
                    setZones(zonesData.zones || []);
                    setCheckedZones([selectedCampus]);

                    const verticesResponse = await fetch(`${API_BASE_URL}/zoneviewer/get_vertices_for_campus/${selectedCampus}`);
                    if (!verticesResponse.ok) throw new Error(`Vertices fetch failed: ${verticesResponse.status}`);
                    const verticesData = await verticesResponse.json();
                    setVertices(verticesData.vertices || []);
                    setEditedVertices({});
                    setDeletedVertices([]);
                } catch (error) {
                    console.error("❌ Error fetching zones/vertices:", error);
                    setFetchError(error.message);
                }
            };
            fetchZonesAndVertices();
        }
    }, [selectedCampus]);

    const handleZoneToggle = (zoneId) => {
        setCheckedZones((prev) =>
            prev.includes(zoneId) ? prev.filter((id) => id !== zoneId) : [...prev, zoneId]
        );
    };

    // --- CHANGED: Added function to toggle all zones under a parent (including nested children)
    const toggleAllZones = (zone, check) => {
        const toggleZoneAndChildren = (z) => {
            if (check) {
                setCheckedZones((prev) => prev.includes(z.zone_id) ? prev : [...prev, z.zone_id]);
            } else {
                setCheckedZones((prev) => prev.filter((id) => id !== z.zone_id));
            }
            if (z.children && z.children.length > 0) {
                z.children.forEach(child => toggleZoneAndChildren(child));
            }
        };
        toggleZoneAndChildren(zone);
    };

    // --- CHANGED: Added "Check All" functionality to toggle all zones
    const handleCheckAll = (check) => {
        if (check) {
            setCheckedZones(zones.map(zone => zone.zone_id));
        } else {
            setCheckedZones([]);
        }
    };

    // --- CHANGED: Updated renderZones to include "Check All" checkboxes for each parent zone
    const renderZones = (zones, depth = 0) => {
        return zones.map((zone) => (
            <div key={zone.zone_id} style={{ marginLeft: `${depth * 20}px`, marginBottom: "5px" }}>
                <div style={{ display: "flex", alignItems: "center" }}>
                    <input
                        type="checkbox"
                        checked={checkedZones.includes(zone.zone_id)}
                        onChange={() => handleZoneToggle(zone.zone_id)}
                        style={{ marginRight: "5px" }}
                    />
                    <span>{zone.zone_name}</span>
                    {zone.children && zone.children.length > 0 && (
                        <input
                            type="checkbox"
                            checked={zone.children.every(child => checkedZones.includes(child.zone_id))}
                            onChange={(e) => toggleAllZones(zone, e.target.checked)}
                            style={{ marginLeft: "10px", marginRight: "5px" }}
                        />
                    )}
                    {zone.children && zone.children.length > 0 && <span style={{ fontSize: "12px", color: "#666" }}>(Check All)</span>}
                    {zone.parent_zone_id === null && (
                        <button
                            onClick={() => handleDeleteZone(zone.zone_id)}
                            style={{ marginLeft: "10px", color: "red", border: "none", background: "none", cursor: "pointer" }}
                        >
                            Delete Zone
                        </button>
                    )}
                </div>
                {zone.children && zone.children.length > 0 && (
                    renderZones(zone.children, depth + 1)
                )}
            </div>
        ));
    };

    const handleVertexChange = (vertexId, field, value) => {
        const numValue = parseFloat(value) || 0;
        setEditedVertices((prev) => ({
            ...prev,
            [vertexId]: { ...prev[vertexId], [field]: numValue },
        }));
    };

    const stageDeleteVertex = (vertexId) => {
        setDeletedVertices((prev) => [...prev, vertexId]);
        setVertices((prev) => prev.filter((v) => v.vertex_id !== vertexId));
        setEditedVertices((prev) => {
            const newEdits = { ...prev };
            delete newEdits[vertexId];
            return newEdits;
        });
    };

    // --- CHANGED: Round default coordinates to 6 decimal places when adding a new vertex
    const addVertex = async (zoneId, position, refVertexId) => {
        try {
            const zoneVertices = vertices.filter(v => v.zone_id === zoneId).sort((a, b) => a.order - b.order);
            const refVertex = vertices.find(v => v.vertex_id === refVertexId);
            const order = position === "before" 
                ? (refVertex ? refVertex.order - 0.5 : 0) 
                : (refVertex ? refVertex.order + 0.5 : zoneVertices.length + 1);

            const payload = { 
                zone_id: zoneId, 
                x: Number(0.0).toFixed(6), 
                y: Number(0.0).toFixed(6), 
                z: Number(0.0).toFixed(6), 
                order 
            };
            console.log("Sending payload to add_vertex:", payload);
            const response = await fetch(`${API_BASE_URL}/zoneviewer/add_vertex`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (!response.ok) throw new Error(`Failed to add vertex: ${response.status}`);
            const newVertex = await response.json();

            const updatedVertices = [...vertices, newVertex].map(v => {
                if (v.zone_id !== zoneId) return v;
                const currentOrder = v.vertex_id === newVertex.vertex_id ? order : v.order;
                return { ...v, order: currentOrder };
            }).sort((a, b) => a.order - b.order).map((v, idx) => ({ ...v, order: idx + 1 }));

            setVertices(updatedVertices);
            console.log("✅ Added vertex:", newVertex);
        } catch (error) {
            console.error("❌ Error adding vertex:", error);
            alert("Failed to add vertex: " + error.message);
        }
    };

    // --- CHANGED: Round coordinates to 6 decimal places before saving to backend
    const saveVertices = async () => {
        try {
            for (const vertexId of deletedVertices) {
                const response = await fetch(`${API_BASE_URL}/zoneviewer/delete_vertex/${vertexId}`, {
                    method: "DELETE",
                });
                if (!response.ok) throw new Error(`Failed to delete vertex ${vertexId}: ${response.status}`);
            }

            const updates = Object.entries(editedVertices)
                .filter(([vertexId]) => vertices.some(v => v && v.vertex_id === parseInt(vertexId)))
                .map(([vertexId, changes]) => {
                    const vertex = vertices.find((v) => v && v.vertex_id === parseInt(vertexId));
                    if (!vertex) return null;
                    return { 
                        vertex_id: vertex.vertex_id, 
                        x: Number(changes.x ?? vertex.x).toFixed(6), 
                        y: Number(changes.y ?? vertex.y).toFixed(6), 
                        z: Number(changes.z ?? vertex.z).toFixed(6),
                        order: vertex.order
                    };
                })
                .filter(update => update !== null);

            const allUpdates = [...updates, ...vertices.filter(v => !editedVertices[v.vertex_id] && !deletedVertices.includes(v.vertex_id)).map(v => ({
                vertex_id: v.vertex_id,
                x: Number(v.x).toFixed(6),
                y: Number(v.y).toFixed(6),
                z: Number(v.z).toFixed(6),
                order: v.order
            }))];
            if (allUpdates.length > 0) {
                const response = await fetch(`${API_BASE_URL}/zoneviewer/update_vertices`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(allUpdates),
                });
                if (!response.ok) throw new Error(`Failed to save edits: ${response.status}`);
                const result = await response.json();
                console.log("✅ Vertices saved:", result);
            }

            const verticesResponse = await fetch(`${API_BASE_URL}/zoneviewer/get_vertices_for_campus/${selectedCampus}`);
            if (!verticesResponse.ok) throw new Error(`Vertices fetch failed: ${verticesResponse.status}`);
            const verticesData = await verticesResponse.json();
            setVertices(verticesData.vertices || []);
            setEditedVertices({});
            setDeletedVertices([]);
            alert("Changes saved successfully!");
        } catch (error) {
            console.error("❌ Error saving changes:", error);
            alert("Failed to save changes: " + error.message);
        }
    };

    const exportVertices = () => {
        if (!selectedCampus) {
            alert("Please select a campus first.");
            return;
        }
        const verticesToExport = vertices.filter(v => checkedZones.includes(v.zone_id));
        if (verticesToExport.length === 0) {
            alert("No vertices to export for the selected zones.");
            return;
        }
        const json = JSON.stringify(verticesToExport, null, 2);
        const blob = new Blob([json], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `vertices_zone_${selectedCampus}.json`;
        link.click();
        URL.revokeObjectURL(url);
    };

    const importVertices = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        try {
            const text = await file.text();
            const importedVertices = JSON.parse(text);
            if (!Array.isArray(importedVertices)) {
                throw new Error("Imported file must contain an array of vertices.");
            }

            const validVertices = importedVertices.filter(v => {
                return (
                    typeof v.vertex_id === "number" &&
                    typeof v.x === "number" &&
                    typeof v.y === "number" &&
                    (v.z === null || typeof v.z === "number") &&
                    typeof v.order === "number" &&
                    typeof v.zone_id === "number" &&
                    checkedZones.includes(v.zone_id)
                );
            });

            if (validVertices.length === 0) {
                throw new Error("No valid vertices found in the imported file for the selected zones.");
            }

            const existingVertexIds = new Set(vertices.map(v => v.vertex_id));
            const newVertices = validVertices.filter(v => !existingVertexIds.has(v.vertex_id));
            const updatedVertices = vertices.map(v => {
                const imported = validVertices.find(iv => iv.vertex_id === v.vertex_id);
                return imported ? { ...v, ...imported } : v;
            });

            setVertices([...updatedVertices, ...newVertices].sort((a, b) => a.order - b.order));
            alert(`Imported ${newVertices.length} new vertices and updated ${validVertices.length - newVertices.length} existing vertices.`);
        } catch (error) {
            console.error("❌ Error importing vertices:", error);
            alert("Failed to import vertices: " + error.message);
        }
    };

    const exportToSVG = () => {
        if (!selectedCampus) {
            alert("Please select a campus first.");
            return;
        }
        const verticesToExport = vertices.filter(v => checkedZones.includes(v.zone_id));
        if (verticesToExport.length === 0) {
            alert("No vertices to export for the selected zones.");
            return;
        }

        const width = 1000;
        const height = 800;
        const min_x = Math.min(...verticesToExport.map(v => v.x));
        const min_y = Math.min(...verticesToExport.map(v => v.y));
        const max_x = Math.max(...verticesToExport.map(v => v.x));
        const max_y = Math.max(...verticesToExport.map(v => v.y));

        const scale_x = (max_x - min_x) ? width / (max_x - min_x) : 1;
        const scale_y = (max_y - min_y) ? height / (max_y - min_y) : 1;

        const normalizedVertices = verticesToExport.map(v => ({
            ...v,
            x: (v.x - min_x) * scale_x,
            y: height - (v.y - min_y) * scale_y
        }));

        const regions = {};
        normalizedVertices.forEach(v => {
            if (!regions[v.zone_id]) {
                regions[v.zone_id] = [];
            }
            regions[v.zone_id].push({ x: v.x, y: v.y, vertex_id: v.vertex_id });
        });

        let svgContent = `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">\n`;
        for (const [zone_id, points] of Object.entries(regions)) {
            const zoneVertices = vertices.filter(v => v.zone_id === parseInt(zone_id)).sort((a, b) => a.order - b.order);
            const orderedPoints = zoneVertices.map(v => {
                const normalized = normalizedVertices.find(nv => nv.vertex_id === v.vertex_id);
                return { x: normalized.x, y: normalized.y, vertex_id: v.vertex_id };
            });

            const pointsStr = orderedPoints.map(p => `${p.x},${p.y}`).join(" ");
            svgContent += `<polygon points="${pointsStr}" fill="rgba(173, 216, 230, 0.6)" stroke="black" stroke-width="2"/>\n`;

            const centroid_x = orderedPoints.reduce((sum, p) => sum + p.x, 0) / orderedPoints.length;
            const centroid_y = orderedPoints.reduce((sum, p) => sum + p.y, 0) / orderedPoints.length;
            svgContent += `<text x="${centroid_x}" y="${centroid_y}" font-size="14" fill="black">Zone ${zone_id}</text>\n`;

            orderedPoints.forEach(p => {
                svgContent += `<text x="${p.x + 5}" y="${p.y - 5}" font-size="12" fill="black">${p.vertex_id}</text>\n`;
            });
        }
        svgContent += `</svg>`;

        const blob = new Blob([svgContent], { type: "image/svg+xml" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `map_zone_${selectedCampus}.svg`;
        link.click();
        URL.revokeObjectURL(url);
    };

    const handleDeleteZone = async (zoneId) => {
        if (!window.confirm(`Are you sure? This will delete zone ${zoneId} and all its progeny.`)) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/zoneviewer/delete_zone_recursive/${zoneId}`, {
                method: "DELETE",
            });
            if (!response.ok) throw new Error(`Failed to delete zone: ${response.status}`);
            const result = await response.json();
            console.log("✅ Zone deleted:", result);

            const campusesResponse = await fetch(`${API_BASE_URL}/zoneviewer/get_campus_zones`);
            if (!campusesResponse.ok) throw new Error(`Failed to fetch campuses: ${campusesResponse.status}`);
            const campusesData = await campusesResponse.json();
            setCampuses(campusesData.campuses || []);

            const zonesResponse = await fetch(`${API_BASE_URL}/zoneviewer/get_all_zones_for_campus/${selectedCampus}`);
            if (!zonesResponse.ok) throw new Error(`Failed to fetch zones: ${zonesResponse.status}`);
            const zonesData = await zonesResponse.json();
            setZones(zonesData.zones || []);
            setCheckedZones([selectedCampus]);

            const verticesResponse = await fetch(`${API_BASE_URL}/zoneviewer/get_vertices_for_campus/${selectedCampus}`);
            if (!verticesResponse.ok) throw new Error(`Failed to fetch vertices: ${verticesResponse.status}`);
            const verticesData = await verticesResponse.json();
            setVertices(verticesData.vertices || []);

            alert(result.message);
        } catch (error) {
            console.error("❌ Error deleting zone:", error);
            alert("Failed to delete zone: " + error.message);
        }
    };

    return (
        <div>
            <h2>Zone Viewer & Editor</h2>
            {fetchError && <div style={{ color: "red" }}>{fetchError}</div>}

            <label>Select Campus:</label>
            <select onChange={(e) => setSelectedCampus(parseInt(e.target.value))} value={selectedCampus || ""}>
                <option value="">Select a Campus</option>
                {campuses.map((campus) => (
                    <option key={campus.zone_id} value={campus.zone_id}>
                        {campus.zone_name}
                    </option>
                ))}
            </select>

            <label>Render with Leaflet:</label>
            <input type="checkbox" checked={useLeaflet} onChange={(e) => setUseLeaflet(e.target.checked)} />

            {selectedCampus && (
                <>
                    <h3>Zones:</h3>
                    {/* --- CHANGED: Added "Check All" checkbox for all zones */}
                    <div style={{ marginBottom: "10px" }}>
                        <input
                            type="checkbox"
                            checked={zones.every(zone => checkedZones.includes(zone.zone_id))}
                            onChange={(e) => handleCheckAll(e.target.checked)}
                            style={{ marginRight: "5px" }}
                        />
                        <span style={{ fontSize: "14px", color: "#666" }}>Check All Zones</span>
                    </div>
                    <div>{renderZones(zones)}</div>

                    <MapZoneViewer
                        mapId={zones[0]?.map_id}
                        zones={zones}
                        checkedZones={checkedZones}
                        vertices={vertices}
                        useLeaflet={useLeaflet}
                    />

                    <h3>Edit Vertices:</h3>
                    <button onClick={exportVertices} style={{ marginBottom: "10px" }}>Export Vertices (JSON)</button>
                    <button onClick={exportToSVG} style={{ marginBottom: "10px", marginLeft: "10px" }}>Export to SVG</button>
                    <input
                        type="file"
                        accept=".json"
                        onChange={importVertices}
                        style={{ marginBottom: "10px" }}
                    />
                    <table style={{ width: "100%", borderCollapse: "collapse", border: "1px solid black" }}>
                        <thead>
                            <tr>
                                <th style={{ border: "1px solid black", padding: "8px" }}>Vertex #</th>
                                <th style={{ border: "1px solid black", padding: "8px" }}>X</th>
                                <th style={{ border: "1px solid black", padding: "8px" }}>Y</th>
                                <th style={{ border: "1px solid black", padding: "8px" }}>Z</th>
                                <th style={{ border: "1px solid black", padding: "8px" }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {vertices
                                .filter((v) => checkedZones.includes(v.zone_id))
                                .map((v) => (
                                    <tr key={v.vertex_id}>
                                        <td style={{ border: "1px solid black", padding: "8px" }}>{v.vertex_id}</td>
                                        {/* --- CHANGED: Round displayed x coordinate to 6 decimal places */}
                                        <td style={{ border: "1px solid black", padding: "8px" }}>
                                            <input
                                                type="number"
                                                value={Number(editedVertices[v.vertex_id]?.x ?? v.x).toFixed(6)}
                                                onChange={(e) => handleVertexChange(v.vertex_id, "x", e.target.value)}
                                                step="0.000001"
                                                style={{ width: "100px" }}
                                            />
                                        </td>
                                        {/* --- CHANGED: Round displayed y coordinate to 6 decimal places */}
                                        <td style={{ border: "1px solid black", padding: "8px" }}>
                                            <input
                                                type="number"
                                                value={Number(editedVertices[v.vertex_id]?.y ?? v.y).toFixed(6)}
                                                onChange={(e) => handleVertexChange(v.vertex_id, "y", e.target.value)}
                                                step="0.000001"
                                                style={{ width: "100px" }}
                                            />
                                        </td>
                                        {/* --- CHANGED: Round displayed z coordinate to 6 decimal places */}
                                        <td style={{ border: "1px solid black", padding: "8px" }}>
                                            <input
                                                type="number"
                                                value={Number(editedVertices[v.vertex_id]?.z ?? v.z).toFixed(6)}
                                                onChange={(e) => handleVertexChange(v.vertex_id, "z", e.target.value)}
                                                step="0.000001"
                                                style={{ width: "100px" }}
                                            />
                                        </td>
                                        <td style={{ border: "1px solid black", padding: "8px" }}>
                                            <button onClick={() => addVertex(v.zone_id, "before", v.vertex_id)}>Add Before</button>
                                            <button onClick={() => addVertex(v.zone_id, "after", v.vertex_id)}>Add After</button>
                                            <button onClick={() => stageDeleteVertex(v.vertex_id)}>Delete</button>
                                        </td>
                                    </tr>
                                ))}
                        </tbody>
                    </table>
                    <button onClick={saveVertices} style={{ marginTop: "10px" }}>Save All Changes</button>
                </>
            )}
        </div>
    );
};

export default ZoneViewer;