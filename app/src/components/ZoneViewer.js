// /home/parcoadmin/parco_fastapi/app/src/components/ZoneViewer.js
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

    const renderZones = (zones, depth = 0) => {
        return zones.map((zone) => (
            <div key={zone.zone_id} style={{ marginLeft: `${depth * 20}px` }}>
                <input
                    type="checkbox"
                    checked={checkedZones.includes(zone.zone_id)}
                    onChange={() => handleZoneToggle(zone.zone_id)}
                />
                <span>{zone.zone_name}</span>
                {zone.children && zone.children.length > 0 && renderZones(zone.children, depth + 1)}
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

    const addVertex = async (zoneId, position, refVertexId) => {
        try {
            const zoneVertices = vertices.filter(v => v.zone_id === zoneId).sort((a, b) => a.order - b.order);
            const refVertex = vertices.find(v => v.vertex_id === refVertexId);
            const order = position === "before" 
                ? (refVertex ? refVertex.order - 0.5 : 0) 
                : (refVertex ? refVertex.order + 0.5 : zoneVertices.length + 1);

            const payload = { zone_id: zoneId, x: 0.0, y: 0.0, z: 0.0, order };
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
                        x: changes.x ?? vertex.x, 
                        y: changes.y ?? vertex.y, 
                        z: changes.z ?? vertex.z,
                        order: vertex.order // Include order
                    };
                })
                .filter(update => update !== null);

            const allUpdates = [...updates, ...vertices.filter(v => !editedVertices[v.vertex_id] && !deletedVertices.includes(v.vertex_id))];
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
                    <div>{renderZones(zones)}</div>

                    <MapZoneViewer
                        mapId={zones[0]?.map_id}
                        zones={zones}
                        checkedZones={checkedZones}
                        vertices={vertices}
                        useLeaflet={useLeaflet}
                    />

                    <h3>Edit Vertices:</h3>
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
                                        <td style={{ border: "1px solid black", padding: "8px" }}>
                                            <input
                                                type="number"
                                                value={editedVertices[v.vertex_id]?.x ?? v.x}
                                                onChange={(e) => handleVertexChange(v.vertex_id, "x", e.target.value)}
                                                step="0.000001"
                                                style={{ width: "100px" }}
                                            />
                                        </td>
                                        <td style={{ border: "1px solid black", padding: "8px" }}>
                                            <input
                                                type="number"
                                                value={editedVertices[v.vertex_id]?.y ?? v.y}
                                                onChange={(e) => handleVertexChange(v.vertex_id, "y", e.target.value)}
                                                step="0.000001"
                                                style={{ width: "100px" }}
                                            />
                                        </td>
                                        <td style={{ border: "1px solid black", padding: "8px" }}>
                                            <input
                                                type="number"
                                                value={editedVertices[v.vertex_id]?.z ?? v.z}
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