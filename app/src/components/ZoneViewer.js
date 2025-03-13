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
    const [fetchError, setFetchError] = useState(null);

    // Fetch campuses on mount
    useEffect(() => {
        const fetchCampuses = async () => {
            try {
                const response = await fetch("/zoneviewer/get_campus_zones");
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

    // Fetch zones and vertices when campus changes
    useEffect(() => {
        if (selectedCampus) {
            const fetchZonesAndVertices = async () => {
                try {
                    const zonesResponse = await fetch(`/zoneviewer/get_all_zones_for_campus/${selectedCampus}`);
                    if (!zonesResponse.ok) throw new Error(`Zones fetch failed: ${zonesResponse.status}`);
                    const zonesData = await zonesResponse.json();
                    setZones(zonesData.zones || []);
                    setCheckedZones([selectedCampus]); // Default to campus checked

                    const verticesResponse = await fetch(`/zoneviewer/get_vertices_for_campus/${selectedCampus}`);
                    if (!verticesResponse.ok) throw new Error(`Vertices fetch failed: ${verticesResponse.status}`);
                    const verticesData = await verticesResponse.json();
                    setVertices(verticesData.vertices || []);
                    setEditedVertices({});
                } catch (error) {
                    console.error("❌ Error fetching zones/vertices:", error);
                    setFetchError(error.message);
                }
            };
            fetchZonesAndVertices();
        }
    }, [selectedCampus]);

    // Handle zone checkbox toggle
    const handleZoneToggle = (zoneId) => {
        setCheckedZones((prev) =>
            prev.includes(zoneId) ? prev.filter((id) => id !== zoneId) : [...prev, zoneId]
        );
    };

    // Render zones recursively
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

    // Handle vertex edit
    const handleVertexChange = (vertexId, field, value) => {
        const numValue = parseFloat(value) || 0;
        setEditedVertices((prev) => ({
            ...prev,
            [vertexId]: { ...prev[vertexId], [field]: numValue },
        }));
    };

    // Save edited vertices
    const saveVertices = async () => {
        const updates = Object.entries(editedVertices).map(([vertexId, changes]) => {
            const vertex = vertices.find((v) => v.vertex_id === parseInt(vertexId));
            return { vertex_id: vertex.vertex_id, x: changes.x ?? vertex.x, y: changes.y ?? vertex.y, z: changes.z ?? vertex.z };
        });
        if (updates.length === 0) return;

        try {
            const response = await fetch("/zoneviewer/update_vertices", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(updates),
            });
            if (!response.ok) throw new Error(`Failed to save: ${response.status}`);
            const result = await response.json();
            console.log("✅ Vertices saved:", result);
            setVertices((prev) =>
                prev.map((v) => {
                    const update = updates.find((u) => u.vertex_id === v.vertex_id);
                    return update ? { ...v, ...update } : v;
                })
            );
            setEditedVertices({});
            alert("Vertices updated successfully!");
        } catch (error) {
            console.error("❌ Error saving vertices:", error);
            alert("Failed to save vertices.");
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
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                        <thead>
                            <tr>
                                <th>Vertex #</th>
                                <th>X</th>
                                <th>Y</th>
                                <th>Z</th>
                            </tr>
                        </thead>
                        <tbody>
                            {vertices
                                .filter((v) => checkedZones.includes(v.zone_id))
                                .map((v) => (
                                    <tr key={v.vertex_id}>
                                        <td>{v.vertex_id}</td>
                                        <td>
                                            <input
                                                type="number"
                                                value={editedVertices[v.vertex_id]?.x ?? v.x}
                                                onChange={(e) => handleVertexChange(v.vertex_id, "x", e.target.value)}
                                                step="0.000001"
                                            />
                                        </td>
                                        <td>
                                            <input
                                                type="number"
                                                value={editedVertices[v.vertex_id]?.y ?? v.y}
                                                onChange={(e) => handleVertexChange(v.vertex_id, "y", e.target.value)}
                                                step="0.000001"
                                            />
                                        </td>
                                        <td>
                                            <input
                                                type="number"
                                                value={editedVertices[v.vertex_id]?.z ?? v.z}
                                                onChange={(e) => handleVertexChange(v.vertex_id, "z", e.target.value)}
                                                step="0.000001"
                                            />
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