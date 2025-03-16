// # VERSION 250316 /home/parcoadmin/parco_fastapi/app/src/components/MapList.js 0P.10B.01
// #  
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import React, { useState, useEffect } from "react";
import MapPreview from "./MapPreview";  // ✅ Import the new preview component

const MapList = () => {
    const [maps, setMaps] = useState([]);
    const [selectedMapId, setSelectedMapId] = useState(null);  // ✅ Track the selected map

    useEffect(() => {
        fetchMaps();
    }, []);

    const fetchMaps = async () => {
        try {
            const response = await fetch("/maps/get_maps");
            const data = await response.json();
    
            if (response.ok) {
                // Fetch counts for each map
                const mapsWithCounts = await Promise.all(
                    data.map(async (map) => {
                        const [zoneRes, regionRes, triggerRes] = await Promise.all([
                            fetch(`/maps/get_map_zones/${map.i_map}`),
                            fetch(`/maps/get_map_regions/${map.i_map}`),
                            fetch(`/maps/get_map_triggers/${map.i_map}`)
                        ]);
    
                        const [zoneData, regionData, triggerData] = await Promise.all([
                            zoneRes.json(),
                            regionRes.json(),
                            triggerRes.json()
                        ]);
    
                        return {
                            ...map,
                            zone_count: zoneData.zone_count || 0,
                            region_count: regionData.region_count || 0,
                            trigger_count: triggerData.trigger_count || 0
                        };
                    })
                );
    
                setMaps(mapsWithCounts);
            } else {
                throw new Error(data.detail || "Failed to fetch maps");
            }
        } catch (err) {
            console.error("Error fetching maps:", err);
        }
    };
    

    return (
        <div style={{ maxWidth: "700px", margin: "auto", padding: "20px", border: "1px solid #ddd", borderRadius: "8px" }}>
            <h2>Uploaded Maps</h2>
            {maps.length === 0 ? <p>No maps uploaded yet.</p> : (
                <ul style={{ listStyle: "none", padding: 0 }}>
                    {maps.map(map => (
                        <li key={map.i_map} style={{ padding: "10px", borderBottom: "1px solid #ddd", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                            <div>
                                <strong>{map.x_nm_map}</strong>
                                <p style={{ fontSize: "14px", margin: "5px 0" }}>
                                    🗺 Zones: {map.zone_count} | 📌 Regions: {map.region_count} | 🚀 Triggers: {map.trigger_count}
                                </p>
                            </div>
                            <div>
                                <button onClick={() => setSelectedMapId(map.i_map)} style={{ padding: "5px 10px", marginRight: "5px", background: "blue", color: "white", border: "none", cursor: "pointer" }}>👀 View</button>
                                <button onClick={() => deleteMap(map.i_map)} style={{ padding: "5px 10px", background: "red", color: "white", border: "none", cursor: "pointer" }}>🗑 Delete</button>
                            </div>
                        </li>
                    ))}
                </ul>
            )}

            {/* ✅ Show MapPreview when a map is selected */}
            {selectedMapId && <MapPreview mapId={selectedMapId} onClose={() => setSelectedMapId(null)} />}
        </div>
    );
};

export default MapList;
