// 
// # VERSION 250316 /home/parcoadmin/parco_fastapi/app/src/components/ZoneBuilder.js 0P.10B.01
// #  
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
import React, { useState, useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet-draw";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import MapZoneBuilder from "./MapZoneBuilder";
import "./ZoneBuilder.css";

const ZoneBuilder = () => {
    const [maps, setMaps] = useState([]);
    const [zones, setZones] = useState([]);
    const [parentZones, setParentZones] = useState([]);
    const [selectedMapId, setSelectedMapId] = useState(null);
    const [selectedZoneType, setSelectedZoneType] = useState(null);
    const [selectedParentZone, setSelectedParentZone] = useState(null);
    const [zoneName, setZoneName] = useState("");
    const [vertices, setVertices] = useState([]);
    const [parentZoneVertices, setParentZoneVertices] = useState([]);
    const [fetchError, setFetchError] = useState(null);
    const [useLeaflet, setUseLeaflet] = useState(false);
    const drawnItems = useRef(new L.FeatureGroup());

    // Fetch maps, zone types, and parent zones
    useEffect(() => {
        const fetchData = async () => {
            try {
                const mapsResponse = await fetch("/zonebuilder/get_maps");
                if (!mapsResponse.ok) throw new Error(`Failed to fetch maps: ${mapsResponse.status}`);
                const mapsData = await mapsResponse.json();
                console.log("📡 Raw maps response:", mapsData);
                setMaps(mapsData.maps || []);
                console.log("✅ Fetched maps:", mapsData.maps);

                const zonesResponse = await fetch("/zonebuilder/get_zone_types");
                if (!zonesResponse.ok) throw new Error(`Failed to fetch zone types: ${zonesResponse.status}`);
                const zonesData = await zonesResponse.json();
                console.log("📡 Raw zone types response:", zonesData);
                setZones(zonesData || []);
                console.log("✅ Fetched zone types:", zonesData);

                const parentZonesResponse = await fetch("/zonebuilder/get_parent_zones");
                if (!parentZonesResponse.ok) throw new Error(`Failed to fetch parent zones: ${parentZonesResponse.status}`);
                const parentZonesData = await parentZonesResponse.json();
                console.log("📡 Raw parent zones response:", parentZonesData);
                setParentZones(parentZonesData.zones || []);
                console.log("✅ Fetched parent zones:", parentZonesData.zones);

                setFetchError(null);
            } catch (error) {
                console.error("❌ Error fetching initial data:", error);
                setFetchError(error.message);
            }
        };
        fetchData();
    }, []);

    // Fetch parent zone vertices when selectedParentZone changes
    useEffect(() => {
        const fetchParentZoneVertices = async () => {
            if (!selectedParentZone) {
                setParentZoneVertices([]);
                console.log("ℹ️ No parent zone selected, clearing parentZoneVertices");
                return;
            }

            try {
                const response = await fetch(`/api/get_zone_vertices/${selectedParentZone}`);
                if (!response.ok) throw new Error(`Failed to fetch vertices for zone ${selectedParentZone}: ${response.status}`);
                const data = await response.json();
                console.log("📡 Raw response from /api/get_zone_vertices:", data);
                if (data.vertices && Array.isArray(data.vertices)) {
                    setParentZoneVertices(data.vertices);
                    console.log("✅ Fetched parent zone vertices:", data.vertices);
                } else {
                    console.warn("⚠️ No valid 'vertices' array in response:", data);
                    setParentZoneVertices([]);
                }
            } catch (error) {
                console.error("❌ Error fetching parent zone vertices:", error);
                setParentZoneVertices([]);
            }
        };

        fetchParentZoneVertices();
    }, [selectedParentZone]);

    // Save Zone with Correct X, Y, Z Coordinates (Feet-Based), adding closing vertex
    const saveZone = async () => {
        if (!zoneName || !selectedMapId || !selectedZoneType) {
            alert("⚠️ Please fill in all required fields (zone name, map, zone type).");
            return;
        }

        let zoneVertices = [];
        if (useLeaflet) {
            drawnItems.current.eachLayer(layer => {
                if (layer instanceof L.Polygon) {
                    const leafletVertices = layer.getLatLngs()[0].map((point, index) => ({
                        n_x: point.lng,
                        n_y: point.lat,
                        n_z: 0,
                        n_ord: index + 1
                    }));
                    zoneVertices = [...zoneVertices, ...leafletVertices];
                }
            });
            if (zoneVertices.length === 0) {
                alert("⚠️ No polygon drawn. Please draw a zone and click 'Finish' before saving.");
                return;
            }
        } else {
            zoneVertices = vertices.map((v, index) => ({
                n_x: v.x,
                n_y: v.y,
                n_z: 0,
                n_ord: index + 1
            }));
            if (zoneVertices.length < 3) {
                alert("⚠️ At least 3 vertices are required to define a zone.");
                console.error("❌ Insufficient vertices:", zoneVertices);
                return;
            }
        }

        // Add closing vertex (last vertex = first vertex) to close the polygon
        if (zoneVertices.length > 0) {
            zoneVertices.push({ ...zoneVertices[0], n_ord: zoneVertices.length + 1 });
            console.log("✅ Added closing vertex:", zoneVertices[zoneVertices.length - 1]);
        }

        // Convert parent_zone_id to integer or null
        let parentZoneId = selectedParentZone;
        if (parentZoneId === "" || parentZoneId === null) {
            parentZoneId = null;
        } else {
            parentZoneId = parseInt(parentZoneId, 10);
            if (isNaN(parentZoneId)) {
                alert("⚠️ Invalid parent zone ID. Please select a valid parent zone or leave it blank.");
                return;
            }
        }

        const zoneData = {
            zone_name: zoneName,
            map_id: selectedMapId,
            zone_level: selectedZoneType,
            parent_zone_id: parentZoneId,
            vertices: zoneVertices,
        };

        console.log("📡 Sending Zone Data to /zonebuilder/create_zone:", zoneData);

        try {
            const response = await fetch("/zonebuilder/create_zone", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(zoneData),
            });

            const result = await response.json();
            if (response.ok) {
                console.log("✅ Zone creation response:", result);
                alert(`✅ Zone '${zoneName}' created successfully! Zone ID: ${result.zone_id}`);
                setVertices([]); // Clear vertices after saving
                drawnItems.current.clearLayers(); // Clear Leaflet layers
            } else {
                console.error("❌ Zone creation failed:", result);
                alert(`❌ Error: ${result.detail || "Unknown error"}`);
            }
        } catch (error) {
            console.error("❌ Network error creating zone:", error);
            alert("⚠️ Failed to create zone. Check console for details.");
        }
    };

    // Log parentZoneVertices to verify it’s being passed
    console.log("📌 Current parentZoneVertices:", parentZoneVertices);

    return (
        <div>
            <h2>Zone Builder</h2>

            {fetchError && <div style={{ color: "red", marginBottom: "10px" }}>Error: {fetchError}</div>}

            <label>Zone Type:</label>
            <select onChange={(e) => setSelectedZoneType(e.target.value)} value={selectedZoneType || ""}>
                <option value="">Select Zone Type</option>
                {zones.map(zone => (
                    <option key={zone.zone_level} value={zone.zone_level}>
                        {zone.zone_name || "Unknown Zone Type"}
                    </option>
                ))}
            </select>

            <label>Map:</label>
            <select onChange={(e) => setSelectedMapId(e.target.value)} value={selectedMapId || ""}>
                <option value="">Select Map</option>
                {maps.map(map => (
                    <option key={map.map_id} value={map.map_id}>
                        {map.name || "Unknown Map"}
                    </option>
                ))}
            </select>

            <label>Parent Zone:</label>
            <select onChange={(e) => setSelectedParentZone(e.target.value)} value={selectedParentZone || ""}>
                <option value="">(None - Parent Zone)</option>
                {parentZones.map(zone => (
                    <option key={zone.zone_id} value={zone.zone_id}>
                        {`${zone.name || "Unknown Zone"} (L${zone.level || "Unknown"})`}
                    </option>
                ))}
            </select>

            <label>Zone Name:</label>
            <input
                type="text"
                value={zoneName}
                onChange={(e) => setZoneName(e.target.value)}
                placeholder="Enter Zone Name"
            />

            <label>Render with Leaflet:</label>
            <input
                type="checkbox"
                checked={useLeaflet}
                onChange={(e) => setUseLeaflet(e.target.checked)}
            />

            <div style={{ display: "flex", flexDirection: "row", marginTop: "10px" }}>
                {useLeaflet ? (
                    <div id="zoneMap" style={{ height: "600px", width: "800px", border: "2px solid black" }}>
                        <MapZoneBuilder
                            zoneId={selectedMapId}
                            onDrawComplete={setVertices}
                            useLeaflet={true}
                            drawnItems={drawnItems.current}
                            parentZoneVertices={parentZoneVertices}
                        />
                    </div>
                ) : (
                    <div id="zoneCanvas" style={{ height: "600px", width: "800px", border: "2px solid black" }}>
                        <MapZoneBuilder
                            zoneId={selectedMapId}
                            onDrawComplete={setVertices}
                            useLeaflet={false}
                            parentZoneVertices={parentZoneVertices}
                        />
                    </div>
                )}
            </div>

            <button onClick={saveZone} style={{ marginTop: "10px" }}>Save Zone</button>
        </div>
    );
};

export default ZoneBuilder;